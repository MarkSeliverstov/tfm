import asyncio

from .handlers import setup
from .singleton_instances import bot, dp


def main() -> None:
    setup(dp)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
