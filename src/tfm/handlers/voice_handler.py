import json
from decimal import Decimal
from typing import BinaryIO, TypedDict

from aiogram.types import Message
from openai.types.chat import ChatCompletion
from structlog import BoundLogger, get_logger

from ..model import User
from ..singleton_instances import bot, db, openai

logger: BoundLogger = get_logger()


class TransactionData(TypedDict):
    amount: str | None
    transaction_type: str | None


async def _get_transaction_data_from_voice(
    message: Message, voice_file: BinaryIO, transactions_types: list[str]
) -> TransactionData:
    assert message.from_user
    assert message.voice
    prompt: str = f"""
    Extract the transaction data from the message:
    1. Extract the `amount` of the transaction (positive if income, negative if outcome) in the format of a string.
    2. Extract the `transaction type` (one of {transactions_types})

    If the transaction data is not clear, return `None` for both fields.
    """
    transcription: str = openai.audio.transcriptions.create(
        file=(message.voice.file_id + ".ogg", voice_file),
        model="whisper-1",
        response_format="text",
    )

    transaction_data: ChatCompletion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcription},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "transaction_data",
                "schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "string"},
                        "transaction_type": {
                            "type": "string",
                            "enum": transactions_types,
                        },
                    },
                    "required": ["amount", "transaction_type"],
                },
            },
        },
    )
    if not transaction_data.choices or not transaction_data.choices[0].message.content:
        logger.error("Failed to extract transaction data")
        raise ValueError("Failed to extract transaction data")

    logger.info(
        f"Extracted transaction data: {transaction_data.choices[0].message.content} from {transcription=}"
    )
    return json.loads(transaction_data.choices[0].message.content)


async def voice_handler(message: Message) -> None:
    try:
        assert message.voice
        assert message.from_user
        logger.info("Received new voice message")
        voice_file: BinaryIO | None = await bot.download(message.voice)
        if not voice_file:
            logger.error("Failed to download voice")
            await message.answer("Failed to download voice, please try again")
            return

        user: User | None = await db.get_user(id=message.from_user.id)
        if not user:
            await message.answer("We have no information about you")
            return

        if not user.transactions_types:
            await message.answer("You have no transactions types, please add them first")
            return

        transaction_data: TransactionData = await _get_transaction_data_from_voice(
            message, voice_file, user.transactions_types
        )
        if not transaction_data["amount"] or not transaction_data["transaction_type"]:
            raise ValueError("Failed to extract transaction data, no clear message")

        await db.add_transaction(
            user_id=message.from_user.id,
            amount=Decimal(transaction_data["amount"]),
            transaction_type=transaction_data["transaction_type"],
        )
        amount = (
            f"{transaction_data['amount']}"
            if transaction_data["amount"].startswith("-")
            else f"+{transaction_data['amount']}"
        )
        updated_balance: Decimal = user.current_balance + Decimal(transaction_data["amount"])
        await message.answer(
            f"Transaction: {amount} [{transaction_data['transaction_type']}].\n"
            + f"Current balance: {updated_balance}"
        )
    except Exception as exc:
        logger.error(f"Failed to extract transaction data: {exc}")
        await message.answer("Failed to extract transaction data, please try again")
        return
