import os


class Config:
    BOT_TOKEN: str = os.environ["BOT_TOKEN"]
    OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
    MY_TELEGRAM_ID: int = int(os.environ["MY_TELEGRAM_ID"])
    DATABASE_DSN: str = os.environ["DATABASE_DSN"]
