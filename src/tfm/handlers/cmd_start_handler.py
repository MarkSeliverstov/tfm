from aiogram.types import Message


async def cmd_start_handler(message: Message) -> None:
    if not message.from_user:
        await message.answer("Hello!")
        return
    await message.answer(f"Hello, {message.from_user.first_name}!")
