import asyncio

from .config import Config
from .handlers import setup
from .singleton_instances import bot, db, dp


async def start() -> None:
    await db.setup(dsn=Config.DATABASE_DSN)
    setup(dp)
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(start())


if __name__ == "__main__":
    main()
