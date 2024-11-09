import os


class Config:
    SPREADSHEET_ID: str = os.environ["SPREADSHEET_ID"]
    BOT_TOKEN: str = os.environ["BOT_TOKEN"]
    OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
    GOOGLE_SA: str = os.environ["GOOGLE_SA"]
    GOOGLE_SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
    MY_TELEGRAM_ID: int = int(os.environ["MY_TELEGRAM_ID"])
