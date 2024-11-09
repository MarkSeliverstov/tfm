"""
This file contains singleton instances.
Since tg bot must be a singleton instance, we need to explicitly define all instances.
"""

from os import environ

from aiogram import Bot
from google.oauth2.credentials import Credentials
from googleapiclient._apis.sheets.v4 import SheetsResource
from googleapiclient.discovery import build
from openai import OpenAI

bot: Bot = Bot(token=environ["BOT_TOKEN"])

openai: OpenAI = OpenAI(api_key=environ["OPENAI_API_KEY"])

_google_credentials: Credentials = Credentials.from_authorized_user_info( # type: ignore
    environ["GOOGLE_SA"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)
sheet: SheetsResource.SpreadsheetsResource = build(
    "sheets",
    "v4",
    credentials=_google_credentials,
).spreadsheets()
