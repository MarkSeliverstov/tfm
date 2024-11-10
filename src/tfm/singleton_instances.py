"""
This file contains singleton instances.
Since tg bot must be a singleton instance, we need to explicitly define all instances.
"""

from aiogram import Bot, Dispatcher
from openai import OpenAI

from .config import Config
from .database import PostgresDatabase
from .spread_sheet_client import SpreadSheetClient

dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=Config.BOT_TOKEN)
openai: OpenAI = OpenAI(api_key=Config.OPENAI_API_KEY)
sheet_client: SpreadSheetClient = SpreadSheetClient(
    sheet_id=Config.SPREADSHEET_ID, sa_secret=Config.GOOGLE_SA
)
db: PostgresDatabase = PostgresDatabase()
