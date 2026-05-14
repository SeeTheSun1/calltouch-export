import hashlib
import re
from datetime import datetime

from .config import COLUMNS


def normalize_phone(raw: str | None) -> str:
    if not raw:
        return ""
    digits = re.sub(r"\D", "", str(raw))
    if not digits:
        return ""
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits


def normalize_email(raw: str | None) -> str:
    if not raw:
        return ""
    return str(raw).strip().lower()


def md5(value: str) -> str:
    if not value:
        return ""
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def format_dt(raw: str | None) -> str:
    """Convert Calltouch 'dd/mm/yyyy HH:MM:SS' → 'DD.MM.YYYY H:MM:SS'.

    Часы без ведущего нуля, чтобы значение совпадало с display-форматом
    Google Sheets (нужно для дедупликации: при чтении get_all_values
    возвращает отформатированное значение)."""
    if not raw:
        return ""
    try:
        dt = datetime.strptime(str(raw), "%d/%m/%Y %H:%M:%S")
        return f"{dt.day:02d}.{dt.month:02d}.{dt.year} {dt.hour}:{dt.minute:02d}:{dt.second:02d}"
    except ValueError:
        return str(raw)


def _pick_email(call: dict) -> str:
    callback_info = call.get("callbackInfo") or {}
    return callback_info.get("email") or call.get("email") or ""


def to_rows(calls: list[dict], order_status: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for c in calls:
        phone = normalize_phone(c.get("callerNumber"))
        email = normalize_email(_pick_email(c))
        row = [
            format_dt(c.get("date")),
            str(c.get("yaClientId") or ""),
            md5(email),
            md5(phone),
            order_status,
            "",
            "",
        ]
        rows.append(row)
    return rows


def filter_new(new_rows: list[list[str]], existing_rows: list[list[str]]) -> list[list[str]]:
    """Drop rows whose full tuple (all 7 columns) already exists in the sheet."""
    n = len(COLUMNS)

    def _norm(row: list) -> tuple:
        padded = list(row) + [""] * (n - len(row))
        return tuple("" if v is None else str(v) for v in padded[:n])

    existing_set = {_norm(r) for r in existing_rows}
    return [r for r in new_rows if _norm(r) not in existing_set]
