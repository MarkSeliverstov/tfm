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
