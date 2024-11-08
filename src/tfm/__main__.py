import asyncio
from os import getenv
from typing import BinaryIO

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import OpenAI
from structlog import BoundLogger, get_logger

logger: BoundLogger = get_logger()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
openai = OpenAI(api_key=getenv("OPENAI_API_KEY"))
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message_handler(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(F.voice)
async def echo_handler(message: Message) -> None:
    try:
        assert message.voice
        logger.info(
            f"Downloading voice with {message.voice.file_id=} and {message.voice.mime_type=}"
        )
        voice_file: BinaryIO | None = await bot.download(message.voice)
        if not voice_file:
            await message.answer("Failed to download voice")
            return
        logger.info(f"Downloaded voice with {len(voice_file.read())=}")
        transcription = openai.audio.transcriptions.create(
            file=voice_file, model="whisper-1", response_format="text"
        )
        await message.answer(transcription)

    except TypeError:
        await message.answer("Nice try!")


async def start():
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    print(TOKEN)

    # And the run events dispatching
    await dp.start_polling(bot)


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
