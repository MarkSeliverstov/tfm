import re
from decimal import Decimal
from typing import Any, Match

from aiogram.types import Message
from structlog import BoundLogger, get_logger

from ..singleton_instances import db

logger: BoundLogger = get_logger()


async def cmd_change_transactions_types(message: Message) -> None:
    assert message.from_user and message.text
    logger.info(f"Changing transactions types: {message.text=}")
    types: list[str] = message.text.split("\n")[1:]
    logger.info(f"Changing transactions types: {types=}")
    await db.change_transactions_types(user_id=message.from_user.id, types=types)


async def cmd_add_transaction(message: Message) -> None:
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


async def cmd_get_transactions_types(message: Message) -> None:
    assert message.from_user
    types: list[str] = await db.get_transactions_types(user_id=message.from_user.id)
    await message.answer(f"Your transactions types: {types}")


async def cmd_add_user(message: Message) -> None:
    if not message.from_user:
        await message.answer("You are not a user!")
        return

    await db.add_user(id=message.from_user.id, initial_balance=0)
    await message.answer("User added!")


async def cmd_get_id(message: Message) -> None:
    if not message.from_user:
        await message.answer("You are not a user!")
        return
    await message.answer("Your ID is: " + str(message.from_user.id))


async def cmd_get_user(message: Message) -> None:
    if not message.from_user:
        await message.answer("You are not a user!")
        return

    user: dict[str, Any] = await db.get_user(id=message.from_user.id)
    await message.answer(f"{user=}")
