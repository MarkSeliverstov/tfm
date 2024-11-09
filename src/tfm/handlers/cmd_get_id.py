from aiogram.types import Message


async def cmd_get_id(message: Message) -> None:
    if not message.from_user:
        await message.answer("You are not a user!")
        return
    await message.answer("Your ID is: " + str(message.from_user.id))
