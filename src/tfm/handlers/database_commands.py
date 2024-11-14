import re
from decimal import Decimal
from typing import Any, Awaitable, Callable, Dict, Match

from aiogram import BaseMiddleware, Router
from aiogram.filters import Command
from aiogram.types import Message, TelegramObject
from structlog import BoundLogger, get_logger

from ..database import PostgresDatabase
from ..model import User

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


@database_commands_router.message(Command("change_transactions_types"))
async def cmd_change_transactions_types(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user and message.text
    logger.info(f"Changing transactions types: {message.text=}")
    types: list[str] = message.text.split("\n")[1:]
    logger.info(f"Changing transactions types: {types=}")
    await db.change_transactions_types(user_id=message.from_user.id, types=types)


@database_commands_router.message(Command("change_initial_balance"))
async def cmd_change_initial_balance(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user and message.text
    logger.info(f"Changing initial balance: {message.text=}")
    new_balance: Decimal = Decimal(message.text.split(" ")[1])
    await db.change_initial_balance(user_id=message.from_user.id, new_balance=new_balance)


@database_commands_router.message(Command("get_balance"))
async def cmd_add_transaction(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user and message.text
    match: Match[str] | None = re.match(r"/add (\d+(\.\d+)?) (.+)", message.text)
    if not match:
        await message.answer("Invalid command format")
        return

    logger.info(f"Adding transaction: {match=}, {match.group(1)=}, {match.group(3)=}")
    amount: Decimal = Decimal(match.group(1))
    transaction_type: str = match.group(3)
    await db.add_transaction(
        user_id=message.from_user.id, amount=amount, transaction_type=transaction_type
    )


@database_commands_router.message(Command("get_transactions_types"))
async def cmd_get_transactions_types(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user
    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    await message.answer(f"Your transactions types: {user.transactions_types}")


@database_commands_router.message(Command("add_user"))
async def cmd_add_user(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user
    await db.add_user(id=message.from_user.id, initial_balance=0)
    await message.answer("User added!")


@database_commands_router.message(Command("get_user"))
async def cmd_get_user(message: Message, db: PostgresDatabase) -> None:
    assert message.from_user

    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    await message.answer(f"{user=}")
