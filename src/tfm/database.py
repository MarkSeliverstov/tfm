from decimal import Decimal
from importlib import resources
from typing import Any

import asyncpg
from structlog import BoundLogger, get_logger

logger: BoundLogger = get_logger()


class PostgresDatabase:
    def __init__(self) -> None:
        logger.info("Creating database connection pool")
        self.pg_pool: asyncpg.Pool | None = None

    async def setup(self, dsn: str, schema: str = "schema.sql") -> None:
        logger.info("Setting up database")
        self.pg_pool = await asyncpg.create_pool(dsn=dsn)

        logger.info("Ensuring schema")
        path: str = str(resources.files(__package__).joinpath(schema))
        con: asyncpg.Connection
        async with self.pg_pool.acquire() as con:
            with open(path) as file:
                await con.execute(file.read())

    async def add_user(self, id: int, initial_balance: float) -> None:
        assert self.pg_pool
        query: str = """
        INSERT INTO users (id, initial_balance, current_balance, transactions_types)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (id) DO NOTHING
        """
        con: asyncpg.Connection
        async with self.pg_pool.acquire() as con:
            await con.execute(query, id, initial_balance, initial_balance, [])

    async def change_transactions_types(self, user_id: int, types: list[str]) -> None:
        assert self.pg_pool
        query: str = """
        UPDATE users
        SET transactions_types = $2
        WHERE id = $1
        """
        con: asyncpg.Connection
        async with self.pg_pool.acquire() as con:
            await con.execute(query, user_id, types)

    async def get_transactions_types(self, user_id: int) -> list[str]:
        assert self.pg_pool
        query: str = """
        SELECT transactions_types FROM users WHERE id = $1
        """
        con: asyncpg.Connection
        async with self.pg_pool.acquire() as con:
            return await con.fetchval(query, user_id)  # type: ignore

    async def add_transaction(self, user_id: int, amount: Decimal, transaction_type: str) -> None:
        assert self.pg_pool
        update_current_balance_query: str = """
        UPDATE users
        SET current_balance = current_balance + $1
        WHERE id = $2
        """
        insert_transaction_query: str = """
        INSERT INTO transactions (user_id, amount, type) VALUES ($1, $2, $3)
        """
        con: asyncpg.Connection
        async with self.pg_pool.acquire() as con:
            async with con.transaction():
                existed_types: list[str] = await self.get_transactions_types(user_id)
                if transaction_type not in existed_types:
                    raise ValueError(f"Transaction type {transaction_type} is not valid")
                await con.execute(update_current_balance_query, amount, user_id)
                await con.execute(insert_transaction_query, user_id, amount, transaction_type)

    async def get_user(self, id: int) -> dict[str, Any]:
        assert self.pg_pool
        query: str = """
        SELECT * FROM users WHERE id = $1
        """
        con: asyncpg.Connection
        async with self.pg_pool.acquire() as con:
            return await con.fetchrow(query, id)  # type: ignore

    async def aclose(self) -> None:
        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("Database connection pool closed.")
