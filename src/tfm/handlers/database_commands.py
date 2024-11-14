from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, TelegramObject
from aiogram.types.keyboard_button import KeyboardButton
from structlog import BoundLogger, get_logger

from ..database import PostgresDatabase
from ..model import Transaction, User

logger: BoundLogger = get_logger()
database_commands_router: Router = Router()


class DatabaseCommandsMiddleware(BaseMiddleware):
    def __init__(self, db: PostgresDatabase) -> None:
        self.db: PostgresDatabase = db

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db"] = self.db
        return await handler(event, data)


@database_commands_router.message(Command("start"))
async def cmd_start(message: types.Message, db: PostgresDatabase) -> None:
    assert message.from_user
    logger.info(f"Starting bot for user {message.from_user.id=}")
    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await db.add_user(id=message.from_user.id, initial_balance=0)
        logger.info(f"User {message.from_user.id=} added to the database")
        return

    kb: list[list[KeyboardButton]] = [
        [types.KeyboardButton(text="Balance"), types.KeyboardButton(text="Transactions")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Choose an command",
        resize_keyboard=True,
    )
    await message.answer("Hi!", reply_markup=keyboard)


@database_commands_router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer(
        "/start - start the bot\n"
        "/help - get help\n"
        "/get_transactions_types - get transactions types\n"
        "/change_transactions_types - change transactions types (write types separated by new line)"
    )


@database_commands_router.message(Command("change_transactions_types"))
async def cmd_change_transactions_types(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user and message.text
    logger.info(f"Changing transactions types: {message.text=}")
    types: list[str] = message.text.split("\n")[1:]
    logger.info(f"Changing transactions types: {types=}")
    await db.change_transactions_types(user_id=message.from_user.id, types=types)


@database_commands_router.message(Command("get_transactions_types"))
async def cmd_get_transactions_types(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user
    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    await message.answer(f"Your transactions types: {user.transactions_types}")


@database_commands_router.message(F.text.lower() == "transactions")
async def cmd_transactions(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user
    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    transactions: list[Transaction] = await db.get_transactions(user_id=message.from_user.id)
    if not transactions:
        await message.answer("You have no transactions")
        return
    await message.answer("\n".join(str(transaction) for transaction in transactions))


@database_commands_router.message(F.text.lower() == "balance")
async def cmd_balance(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user
    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    await message.answer(f"Your balance: {user.current_balance}")
