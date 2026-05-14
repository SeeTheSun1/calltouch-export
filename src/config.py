COLUMNS = [
    "create_date_time",
    "client_ids",
    "emails_md5",
    "phones_md5",
    "order_status",
    "revenue",
    "cost",
]

CALLTOUCH_BASE_URL = "https://api.calltouch.ru/calls-service/RestAPI"
PAGE_LIMIT = 1000
REQUEST_TIMEOUT = 60
SLEEP_BETWEEN_PAGES = 0.25
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_BASE = 2.0
