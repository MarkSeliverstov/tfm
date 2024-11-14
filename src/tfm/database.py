from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from decimal import Decimal
from importlib import resources
from typing import cast

import asyncpg
from structlog import BoundLogger, get_logger

from .model import Transaction, User

logger: BoundLogger = get_logger()


class PostgresDatabase:
    def __init__(self) -> None:
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
        INSERT INTO users (id, current_balance, transactions_types)
        VALUES ($1, $2, $3)
        """
        async with self._acquire() as con:
            try:
                await con.execute(query, id, initial_balance, [])
            except asyncpg.exceptions.UniqueViolationError:
                raise ValueError(f"User with id {id} already exists")

    async def get_transactions(self, user_id: int) -> list[Transaction]:
        query: str = "SELECT * FROM transactions WHERE user_id = $1"
        async with self._acquire() as con:
            rows: list[asyncpg.Record] = await con.fetch(query, user_id)
            return [
                Transaction(row["amount"], row["created_at"], row["description"]) for row in rows
            ]

    async def change_transactions_types(self, user_id: int, types: list[str]) -> None:
        query: str = """
        UPDATE users
        SET transactions_types = $2
        WHERE id = $1
        """
        async with self._acquire() as con:
            await con.execute(query, user_id, types)

    async def add_transaction(self, user_id: int, amount: Decimal, description: str) -> None:
        update_current_balance_query: str = """
        UPDATE users
        SET current_balance = current_balance + $1
        WHERE id = $2
        """
        insert_transaction_query: str = """
        INSERT INTO transactions (user_id, amount, description)
        VALUES ($1, $2, $3)
        """
        user: User | None = await self.get_user(user_id)
        if not user:
            logger.info(f"User with {user_id=} does not exist")
            raise ValueError(f"User with id {user_id} does not exist")

        async with self._acquire() as con:
            async with con.transaction():
                await con.execute(update_current_balance_query, amount, user_id)
                await con.execute(insert_transaction_query, user_id, amount, description)

    async def get_user(self, id: int) -> User | None:
        query: str = "SELECT * FROM users WHERE id = $1"
        async with self._acquire() as con:
            row: asyncpg.Record | None = await con.fetchrow(query, id)
            return User(**row) if row else None

    async def aclose(self) -> None:
        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("Database connection pool closed.")
