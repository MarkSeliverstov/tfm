from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from decimal import Decimal
from importlib import resources
from typing import cast

import asyncpg
from structlog import BoundLogger, get_logger

from .model import User

logger: BoundLogger = get_logger()


class PostgresDatabase:
    def __init__(self) -> None:
        logger.info("Creating database connection pool")
        self.pg_pool: asyncpg.Pool | None = None

    @asynccontextmanager
    async def _acquire(self) -> AsyncIterator[asyncpg.Connection]:
        assert self.pg_pool
        async with self.pg_pool.acquire() as con:
            yield cast(asyncpg.Connection, con)

    async def setup(self, dsn: str, schema: str = "schema.sql") -> None:
        logger.info("Setting up database")
        self.pg_pool = await asyncpg.create_pool(dsn=dsn)

        logger.info("Ensuring schema")
        path: str = str(resources.files(__package__).joinpath(schema))
        async with self._acquire() as con:
            with open(path) as file:
                await con.execute(file.read())

    async def add_user(self, id: int, initial_balance: float) -> None:
        query: str = """
        INSERT INTO users (id, initial_balance, current_balance, transactions_types)
        VALUES ($1, $2, $3, $4)
        """
        async with self._acquire() as con:
            try:
                await con.execute(query, id, initial_balance, initial_balance, [])
            except asyncpg.exceptions.UniqueViolationError:
                raise ValueError(f"User with id {id} already exists")

    async def change_transactions_types(self, user_id: int, types: list[str]) -> None:
        query: str = """
        UPDATE users
        SET transactions_types = $2
        WHERE id = $1
        """
        async with self._acquire() as con:
            await con.execute(query, user_id, types)

    async def change_initial_balance(self, user_id: int, new_balance: Decimal) -> User:
        user_data: User | None = await self.get_user(user_id)
        if not user_data:
            logger.info(f"User with {user_id=} does not exist")
            raise ValueError(f"User with id {user_id} does not exist")

        diff: Decimal = new_balance - user_data.initial_balance
        query: str = """
        UPDATE users
        SET initial_balance = initial_balance + $2, current_balance = current_balance + $2
        WHERE id = $1
        RETURNING *
        """
        async with self._acquire() as con:
            row: asyncpg.Record | None = await con.fetchrow(query, user_id, diff)
            assert row
            return User(**row)

    async def add_transaction(self, user_id: int, amount: Decimal, transaction_type: str) -> None:
        update_current_balance_query: str = """
        UPDATE users
        SET current_balance = current_balance + $1
        WHERE id = $2
        """
        insert_transaction_query: str = """
        INSERT INTO transactions (user_id, amount, type)
        VALUES ($1, $2, $3)
        """
        user: User | None = await self.get_user(user_id)
        if not user:
            logger.info(f"User with {user_id=} does not exist")
            raise ValueError(f"User with id {user_id} does not exist")

        existed_types: list[str] = user.transactions_types
        if transaction_type not in existed_types:
            logger.info(
                f"Adding new transaction with {transaction_type=} is not allowed",
                existed_types=existed_types,
            )
            raise ValueError(f"Transaction type {transaction_type} is not valid")

        async with self._acquire() as con:
            async with con.transaction():
                await con.execute(update_current_balance_query, amount, user_id)
                await con.execute(insert_transaction_query, user_id, amount, transaction_type)

    async def get_user(self, id: int) -> User | None:
        query: str = "SELECT * FROM users WHERE id = $1"
        async with self._acquire() as con:
            row: asyncpg.Record | None = await con.fetchrow(query, id)
            return User(**row) if row else None

    async def aclose(self) -> None:
        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("Database connection pool closed.")
