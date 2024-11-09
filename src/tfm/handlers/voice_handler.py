from typing import BinaryIO

from aiogram.types import Message
from structlog import BoundLogger, get_logger

from ..singleton_instances import bot, openai

logger: BoundLogger = get_logger()


async def voice_handler(message: Message) -> None:
    try:
        assert message.voice
        logger.info("Received new voice message")
        voice_file: BinaryIO | None = await bot.download(message.voice)

        if not voice_file:
            logger.error("Failed to download voice")
            await message.answer("Failed to download voice")
            return

        transcription = openai.audio.transcriptions.create(
            file=(message.voice.file_id + ".ogg", voice_file),
            model="whisper-1",
            response_format="text",
        )
        logger.info(f"Transcribed voice with {transcription=}")
        await message.answer(transcription)
    except TypeError:
        await message.answer("Nice try!")
