import re
from decimal import Decimal
from typing import Match

from aiogram.types import Message
from structlog import BoundLogger, get_logger

from ..model import User
from ..singleton_instances import db

logger: BoundLogger = get_logger()


async def cmd_change_transactions_types(message: Message) -> None:
    assert message.from_user and message.text
    logger.info(f"Changing transactions types: {message.text=}")
    types: list[str] = message.text.split("\n")[1:]
    logger.info(f"Changing transactions types: {types=}")
    await db.change_transactions_types(user_id=message.from_user.id, types=types)


async def cmd_change_initial_balance(message: Message) -> None:
    assert message.from_user and message.text
    logger.info(f"Changing initial balance: {message.text=}")
    new_balance: Decimal = Decimal(message.text.split(" ")[1])
    await db.change_initial_balance(user_id=message.from_user.id, new_balance=new_balance)


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
    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    await message.answer(f"Your transactions types: {user.transactions_types}")


async def cmd_add_user(message: Message) -> None:
    assert message.from_user
    await db.add_user(id=message.from_user.id, initial_balance=0)
    await message.answer("User added!")


async def cmd_get_id(message: Message) -> None:
    assert message.from_user
    await message.answer("Your ID is: " + str(message.from_user.id))


async def cmd_get_user(message: Message) -> None:
    assert message.from_user

    user: User | None = await db.get_user(id=message.from_user.id)
    if not user:
        await message.answer("We have no information about you")
        return
    await message.answer(f"{user=}")
