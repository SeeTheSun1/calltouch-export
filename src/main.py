import os
import sys
from datetime import datetime, timedelta, timezone

from . import calltouch, sheets, transform

MSK = timezone(timedelta(hours=3))


def _parse_run_date(raw: str | None):
    if not raw:
        return (datetime.now(MSK) - timedelta(days=1)).date()
    return datetime.strptime(raw.strip(), "%d/%m/%Y").date()


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def main() -> int:
    site_id = _require("CALLTOUCH_SITE_ID")
    api_token = _require("CALLTOUCH_API_TOKEN")
    sheet_id = _require("GOOGLE_SHEET_ID")
    order_status = os.environ.get("ORDER_STATUS", "ct_static_call").strip() or "ct_static_call"

    sa_json = os.environ.get("GOOGLE_SA_JSON")
    sa_json_path = os.environ.get("GOOGLE_SA_JSON_PATH")
    if not sa_json and not sa_json_path:
        raise RuntimeError("Either GOOGLE_SA_JSON or GOOGLE_SA_JSON_PATH must be set")

    run_date = _parse_run_date(os.environ.get("RUN_DATE"))
    print(f"Fetching Calltouch calls for {run_date.isoformat()} (MSK)")

    calls = calltouch.fetch_calls(site_id, api_token, run_date)
    fetched = len(calls)

    records = transform.to_records(calls, order_status)

    worksheet = sheets.open_worksheet(sheet_id, sa_json, sa_json_path)
    header, existing = sheets.read_header_and_rows(worksheet)
    if not header:
        raise RuntimeError("Лист пустой: ожидается строка-заголовок в первой строке")

    candidate_rows = transform.align_to_header(records, header)
    new_rows = transform.filter_new(candidate_rows, existing)

    duplicates = fetched - len(new_rows)
    sheets.append(worksheet, new_rows)

    print(f"пришло {fetched}, дублей {duplicates}, записано {len(new_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
