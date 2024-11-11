from typing import Awaitable, Callable

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from magic_filter import MagicFilter

from ..config import Config
from .cmd_start_handler import cmd_start_handler
from .database_commands import (
    cmd_add_transaction,
    cmd_add_user,
    cmd_change_transactions_types,
    cmd_get_id,
    cmd_get_transactions_types,
    cmd_get_user,
)
from .voice_handler import voice_handler

message_handler_t = Callable[[Message], Awaitable[None]]


def setup(dp: Dispatcher) -> None:
    user_id_filter: MagicFilter = F.from_user.id == Config.MY_TELEGRAM_ID
    dp.message.register(voice_handler, F.voice, user_id_filter)
    dp.message.register(cmd_start_handler, CommandStart(), user_id_filter)
    dp.message.register(cmd_get_id, Command("id"), user_id_filter)
    dp.message.register(cmd_add_user, Command("add_user"), user_id_filter)
    dp.message.register(cmd_get_user, Command("get_user"), user_id_filter)
    dp.message.register(cmd_add_transaction, Command("add"), user_id_filter)
    dp.message.register(cmd_get_transactions_types, Command("get_types"), user_id_filter)
    dp.message.register(cmd_change_transactions_types, Command("change_types"), user_id_filter)
    dp.message.register(lambda message: message.answer("Unknown command!"), user_id_filter)
