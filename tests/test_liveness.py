"""pipeline/liveness.py says closed only on a definite signal (no network here)."""

import io
import json
import urllib.error

from conftest import load_script

lv = load_script("pipeline/liveness.py")


def test_status_mapping():
    assert lv.verdict_from_status(200, "x")[0] == "open"
    assert lv.verdict_from_status(404, "x")[0] == "closed"
    assert lv.verdict_from_status(410, "x")[0] == "closed"
    for code in (301, 403, 429, 500, 503):
        assert lv.verdict_from_status(code, "x")[0] == "unknown"


def test_greenhouse_url_goes_to_the_api(monkeypatch):
    seen = []
    monkeypatch.setattr(lv, "http", lambda url, timeout=20: (seen.append(url), (404, ""))[1])
    assert lv.check("https://job-boards.greenhouse.io/acme/jobs/123")[0] == "closed"
    assert seen == ["https://boards-api.greenhouse.io/v1/boards/acme/jobs/123"]


def test_ashby_board_without_the_id_is_closed(monkeypatch):
    jid = "7a67a108-1b94-4d11-9dc1-b1c62d95a3c8"
    monkeypatch.setattr(lv, "http", lambda url, timeout=20: (200, json.dumps({"jobs": [{"id": "other"}]})))
    assert lv.check(f"https://jobs.ashbyhq.com/acme/{jid}")[0] == "closed"
    monkeypatch.setattr(lv, "http", lambda url, timeout=20: (200, json.dumps({"jobs": [{"id": jid}]})))
    assert lv.check(f"https://jobs.ashbyhq.com/acme/{jid}")[0] == "open"


def _workday_error(code, body):
    return urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(json.dumps(body).encode()))  # type: ignore[arg-type]


def test_workday_403_s22_is_withdrawn_other_403_is_unknown(monkeypatch):
    import workday
    url = "https://acme.wd5.myworkdayjobs.com/en-US/External/job/Analyst_R1"

    def raise_(err):
        def f(board, path):
            raise err
        return f
    monkeypatch.setattr(workday, "detail", raise_(_workday_error(403, {"errorCode": "S22", "httpStatus": 403})))
    assert lv.check(url)[0] == "closed"
    monkeypatch.setattr(workday, "detail", raise_(_workday_error(403, {"errorCode": "WAF"})))
    assert lv.check(url)[0] == "unknown"
    monkeypatch.setattr(workday, "detail", lambda board, path: {"can_apply": False})
    assert lv.check(url)[0] == "closed"


def test_page_banner_and_js_shell(monkeypatch):
    monkeypatch.setattr(lv, "http", lambda url, timeout=20: (200, "<p>This position has been filled</p>" + "x" * 3000))
    assert lv.check("https://careers.example.com/job/1")[0] == "closed"
    monkeypatch.setattr(lv, "http", lambda url, timeout=20: (200, "<div id=app></div>"))
    assert lv.check("https://careers.example.com/job/1")[0] == "unknown"
