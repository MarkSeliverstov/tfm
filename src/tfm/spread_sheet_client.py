import json
from typing import TYPE_CHECKING

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from structlog import BoundLogger, get_logger

if TYPE_CHECKING:
    from googleapiclient._apis.sheets.v4 import SheetsResource, Spreadsheet, ValueRange

from tfm.config import Config

logger: BoundLogger = get_logger()


class SpreadSheetClient:
    def __init__(self, sheet_id: str) -> None:
        self._sheet_id: str = sheet_id
        self._api: "SheetsResource" = self._get_resource()

    def _get_resource(self) -> "SheetsResource":
        credentials: Credentials = Credentials.from_service_account_info(  # type: ignore[no-untyped-call]
            json.loads(Config.GOOGLE_SA),
            scopes=Config.GOOGLE_SCOPES,
        )
        return build("sheets", "v4", credentials=credentials)

    def get_sheets(self) -> "Spreadsheet":
        logger.info(f"Spreadsheet ID: {self._sheet_id}")
        return self._api.spreadsheets().get(spreadsheetId=self._sheet_id).execute()

    def get_all_values(self, sheet_name: str) -> "ValueRange":
        logger.info(f"Getting values from {range=}")
        return (
            self._api.spreadsheets()
            .values()
            .get(spreadsheetId=self._sheet_id, range=f"{sheet_name}!A:Z")
            .execute()
        )
