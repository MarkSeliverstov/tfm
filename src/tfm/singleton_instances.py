"""
This file contains singleton instances.
Since tg bot must be a singleton instance, we need to explicitly define all instances.
"""

from os import environ

from aiogram import Bot
from openai import OpenAI

bot: Bot = Bot(token=environ["BOT_TOKEN"])
openai: OpenAI = OpenAI(api_key=environ["OPENAI_API_KEY"])
