from aiogram.types import Message
from structlog import BoundLogger, get_logger

from ..singleton_instances import sheet_client

logger: BoundLogger = get_logger()


async def cmd_view_spread_sheet(message: Message) -> None:
    await message.answer("Processing...")

    values = sheet_client.get_all_values("october")
    logger.info(f"Received values {values=}")
