import json
import os


class Config:
    SPREADSHEET_ID: str = os.environ["SPREADSHEET_ID"]
    BOT_TOKEN: str = os.environ["BOT_TOKEN"]
    OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
    GOOGLE_SA: dict[str, str] = json.loads(os.environ["GOOGLE_SA"])
    MY_TELEGRAM_ID: int = int(os.environ["MY_TELEGRAM_ID"])
