from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from magic_filter import MagicFilter

from ..config import Config
from .cmd_get_id import cmd_get_id
from .cmd_start_handler import cmd_start_handler
from .view_spreadsheet import cmd_view_spread_sheet
from .voice_handler import voice_handler


def setup(dp: Dispatcher):
    user_id_filter: MagicFilter = F.from_user.id == Config.MY_TELEGRAM_ID
    dp.message.register(voice_handler, F.voice, user_id_filter)
    dp.message.register(cmd_start_handler, CommandStart(), user_id_filter)
    dp.message.register(cmd_view_spread_sheet, Command("view"), user_id_filter)
    dp.message.register(cmd_get_id, Command("id"), user_id_filter)
