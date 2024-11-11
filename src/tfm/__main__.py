import asyncio

from structlog import BoundLogger, get_logger

from .config import Config
from .handlers import setup
from .singleton_instances import bot, db, dp

logger: BoundLogger = get_logger()


async def start() -> None:
    try:
        await db.setup(dsn=Config.DATABASE_DSN)
        setup(dp)
        await dp.start_polling(bot)
    finally:
        await db.aclose()


def main() -> None:
    asyncio.run(start())


if __name__ == "__main__":
    main()
