import asyncio

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart

from tfm.handlers.cmd_get_id import cmd_get_id
from tfm.handlers.cmd_start_handler import cmd_start_handler
from tfm.handlers.view_spreadsheet import cmd_view_spread_sheet
from tfm.handlers.voice_handler import voice_handler

from .config import Config
from .singleton_instances import bot

dp: Dispatcher = Dispatcher()
dp.message.register(voice_handler, F.voice, F.from_user.id == Config.MY_TELEGRAM_ID)
dp.message.register(cmd_start_handler, CommandStart(), F.from_user.id == Config.MY_TELEGRAM_ID)
dp.message.register(
    cmd_view_spread_sheet, Command("view"), F.from_user.id == Config.MY_TELEGRAM_ID
)
dp.message.register(cmd_get_id, Command("id"), F.from_user.id == Config.MY_TELEGRAM_ID)


def main() -> None:
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
