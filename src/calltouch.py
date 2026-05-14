import time
from datetime import date

import requests

from .config import (
    CALLTOUCH_BASE_URL,
    PAGE_LIMIT,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF_BASE,
    RETRY_MAX_ATTEMPTS,
    SLEEP_BETWEEN_PAGES,
)


def _get_with_retry(url: str, params: dict) -> dict:
    last_exc = None
    for attempt in range(1, RETRY_MAX_ATTEMPTS + 1):
        try:
            r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt == RETRY_MAX_ATTEMPTS:
                break
            time.sleep(RETRY_BACKOFF_BASE ** attempt)
    raise RuntimeError(f"Calltouch API failed after {RETRY_MAX_ATTEMPTS} attempts: {last_exc}")


def fetch_calls(site_id: str, api_token: str, target_date: date) -> list[dict]:
    """Fetch unique+target CPC calls for a single day with pagination."""
    url = f"{CALLTOUCH_BASE_URL}/{site_id}/calls-diary/calls"
    date_str = target_date.strftime("%d/%m/%Y")
    base_params = {
        "clientApiId": api_token,
        "dateFrom": date_str,
        "dateTo": date_str,
        "limit": PAGE_LIMIT,
        "uniqueOnly": "true",
        "targetOnly": "true",
        "utmMedium": "cpc",
        "withCallbackInfo": "true",
    }

    records: list[dict] = []
    page = 1
    while True:
        params = {**base_params, "page": page}
        data = _get_with_retry(url, params)
        records.extend(data.get("records", []))
        page_total = data.get("pageTotal", 1)
        if page >= page_total:
            break
        page += 1
        time.sleep(SLEEP_BETWEEN_PAGES)
    return records
