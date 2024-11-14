import asyncio

from aiogram import Bot, Dispatcher
from asyncpg.connection import os
from openai import OpenAI
from structlog import BoundLogger, get_logger

from .database import PostgresDatabase
from .handlers.database_commands import DatabaseCommandsMiddleware, database_commands_router
from .handlers.voice_handler import VoiceHandlerMiddleware, voice_handler_router

logger: BoundLogger = get_logger()


class TFMBot:
    def __init__(self) -> None:
        self.database: PostgresDatabase = PostgresDatabase()
        self.openai: OpenAI = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.bot: Bot = Bot(token=os.environ["BOT_TOKEN"])
        self.dispatcher: Dispatcher = Dispatcher()

    def __call__(self) -> None:
        asyncio.run(self.__run())

    async def __run(self) -> None:
        try:
            await self.setup()
            await self.start()
        finally:
            await self.close()

    async def setup(self) -> None:
        logger.info("Preparing bot...")
        await self.database.setup(os.environ["DATABASE_DSN"])
        database_commands_router.message.middleware(DatabaseCommandsMiddleware(self.database))
        voice_handler_router.message.middleware(
            VoiceHandlerMiddleware(self.database, self.openai, self.bot)
        )
        logger.info("Middleware applied")
        self.dispatcher.include_routers(database_commands_router, voice_handler_router)
        logger.info("Routers included")

    async def start(self) -> None:
        logger.info("Starting bot...")
        await self.dispatcher.start_polling(self.bot)

    async def close(self) -> None:
        logger.info("Closing bot...")
        await self.database.aclose()
