import json
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _build_credentials(sa_json: str | None, sa_json_path: str | None) -> Credentials:
    if sa_json:
        info = json.loads(sa_json)
    elif sa_json_path:
        info = json.loads(Path(sa_json_path).read_text(encoding="utf-8"))
    else:
        raise RuntimeError("GOOGLE_SA_JSON or GOOGLE_SA_JSON_PATH must be set")
    return Credentials.from_service_account_info(info, scopes=SCOPES)


def open_worksheet(sheet_id: str, sa_json: str | None, sa_json_path: str | None):
    creds = _build_credentials(sa_json, sa_json_path)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.get_worksheet(0)


def read_all_rows(worksheet) -> list[list[str]]:
    """Return all rows except the header."""
    values = worksheet.get_all_values()
    if not values:
        return []
    return values[1:]


def append(worksheet, rows: list[list[str]]) -> None:
    """Дописываем строки в конец листа.

    insert_data_option=INSERT_ROWS — Google Sheets вставляет новые строки,
    копируя форматирование из предыдущей строки (числовой формат столбцов,
    шрифт, цвет фона и т.д.).

    value_input_option=USER_ENTERED — значения парсятся так же, как при
    ручном вводе. Строка вида '16.03.2026 0:00:00' сохраняется как
    datetime и отображается согласно числовому формату столбца.
    """
    if not rows:
        return
    worksheet.append_rows(
        rows,
        value_input_option="USER_ENTERED",
        insert_data_option="INSERT_ROWS",
    )
