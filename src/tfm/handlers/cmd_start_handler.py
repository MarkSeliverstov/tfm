from aiogram.types import Message


async def cmd_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.full_name}!")
