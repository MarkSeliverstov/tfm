import asyncio

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart

from tfm.handlers.cmd_start_handler import cmd_start_handler
from tfm.handlers.voice_handler import voice_handler

from .singleton_instances import bot

dp: Dispatcher = Dispatcher()
dp.message.register(voice_handler, F.voice)
dp.message.register(cmd_start_handler, CommandStart())


def main():
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
