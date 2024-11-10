from typing import Any

from aiogram.types import Message

from ..singleton_instances import db


async def cmd_get_user(message: Message) -> None:
    if not message.from_user:
        await message.answer("You are not a user!")
        return

    user: dict[str, Any] = await db.get_user(id=message.from_user.id)
    await message.answer(f"{user=}")
