from aiogram.types import Message

from ..singleton_instances import db


async def cmd_add_user(message: Message) -> None:
    if not message.from_user:
        await message.answer("You are not a user!")
        return

    await db.add_user(id=message.from_user.id, initial_balance=0)
    await message.answer("User added!")
