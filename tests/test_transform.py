from src import transform


def test_normalize_phone_variants():
    assert transform.normalize_phone("+7 (999) 123-45-67") == "79991234567"
    assert transform.normalize_phone("8 999 123 45 67") == "79991234567"
    assert transform.normalize_phone("79991234567") == "79991234567"
    assert transform.normalize_phone("") == ""
    assert transform.normalize_phone(None) == ""


def test_normalize_email():
    assert transform.normalize_email("  Foo@Bar.RU  ") == "foo@bar.ru"
    assert transform.normalize_email("") == ""
    assert transform.normalize_email(None) == ""


def test_md5_known():
    assert transform.md5("79991234567") == "c523d04542feb526ea83dc33a4dc6aea"
    assert transform.md5("") == ""


def test_format_dt():
    assert transform.format_dt("22/11/2016 12:30:57") == "22.11.2016 12:30:57"
    assert transform.format_dt("16/03/2026 00:00:00") == "16.03.2026 0:00:00"
    assert transform.format_dt("16/03/2026 09:05:03") == "16.03.2026 9:05:03"
    assert transform.format_dt("") == ""
    assert transform.format_dt("garbage") == "garbage"


def test_to_rows_minimal():
    calls = [{
        "date": "08/05/2026 15:32:47",
        "callerNumber": "+7 (921) 029-70-55",
        "yaClientId": "1778229125198207864",
        "callbackInfo": {"email": "Test@Example.COM"},
    }]
    rows = transform.to_rows(calls, "ct_static_call")
    assert len(rows) == 1
    row = rows[0]
    assert row[0] == "08.05.2026 15:32:47"
    assert row[1] == "1778229125198207864"
    assert row[2] == transform.md5("test@example.com")
    assert row[3] == transform.md5("79210297055")
    assert row[4] == "ct_static_call"
    assert row[5] == ""
    assert row[6] == ""


def test_filter_new_full_identity():
    existing = [
        ["08.05.2026 15:32:47", "abc", "", "hash1", "ct_static_call", "", ""],
    ]
    new = [
        ["08.05.2026 15:32:47", "abc", "", "hash1", "ct_static_call", "", ""],  # duplicate
        ["08.05.2026 16:00:00", "def", "", "hash2", "ct_static_call", "", ""],  # new
    ]
    result = transform.filter_new(new, existing)
    assert result == [["08.05.2026 16:00:00", "def", "", "hash2", "ct_static_call", "", ""]]


def test_filter_new_handles_padding():
    existing = [["08.05.2026 15:32:47", "abc", "", "hash1", "ct_static_call"]]
    new = [["08.05.2026 15:32:47", "abc", "", "hash1", "ct_static_call", "", ""]]
    assert transform.filter_new(new, existing) == []
