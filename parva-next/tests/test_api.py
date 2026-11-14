"""The twelve routes: shape, values, and errors."""

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("swisseph")
from fastapi.testclient import TestClient  # noqa: E402

from parva.api import app  # noqa: E402

client = TestClient(app)


def get(path: str, **params):
    r = client.get(path, params=params)
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) == {"data", "source", "version"}
    return body


def test_convert_both_ways() -> None:
    a = get("/v1/convert", ad="2026-04-14")
    assert a["data"]["bs"]["text"] == "2083-01-01" and a["data"]["weekday"] == "Tuesday"
    assert "moha-gazette-weekdays" in a["source"]
    b = get("/v1/convert", bs="2083-03-32")
    assert b["data"]["ad"] == "2026-07-16"
    assert len(client.get("/v1/convert", params={"ad": "2026-04-14"}).content) < 600  # the answer, not a treatise


def test_errors_are_400_with_a_reason() -> None:
    r = client.get("/v1/convert", params={"bs": "2082-01-32"})
    assert r.status_code == 400 and "does not exist" in r.json()["detail"]
    assert client.get("/v1/festivals/not-a-festival").status_code == 404


def test_valid_month_fiscal() -> None:
    assert get("/v1/valid", bs="2083-03-32")["data"] == {"bs": "2083-03-32", "valid": True, "max_day": 32}
    m = get("/v1/month/2083/6")["data"]
    assert m["days"] == 31 and m["start_ad"] == "2026-09-17" and any(h["id"] == "ghatasthapana" for h in m["holidays"])
    assert get("/v1/fiscal-year", ad="2026-07-16")["data"]["fiscal_year"] == "2082/83"


def test_working_day_and_holidays() -> None:
    w = get("/v1/working-day", ad="2026-10-19")
    assert w["data"]["working"] is False and w["data"]["holidays"][0]["id"] == "dashain-holidays"
    assert w["source"] == "moha-2083"
    h = get("/v1/holidays/2083")
    assert {x["id"] for x in h["data"]} >= {"bs-new-year", "ghatasthapana", "chhath", "shivaratri"}
    assert not any(x["scope"] == "women" for x in h["data"])
    assert any(x["id"] == "teej" for x in get("/v1/holidays/2083", scope="women")["data"])


def test_festivals() -> None:
    d = get("/v1/festivals/dashain", year=2026)
    assert d["data"]["start"] == "2026-10-11" and d["source"] == "moha-2083" and d["data"]["engine"] == "2026-10-11"
    lst = get("/v1/festivals", year=2026)["data"]
    october = [o["id"] for o in lst if o["start"] and o["start"].startswith("2026-10")]
    assert october[:2] == ["ghatasthapana", "dashain"]  # both begin 11 October 2026
    assert all({"id", "start", "end", "source", "gazette", "engine"} <= set(o) for o in lst)


def test_check_posts_a_csv() -> None:
    csv = "date\n2026-10-19\n2026-10-24\n2026-10-27\n2083-13-01\n"
    r = client.post("/v1/check", content=csv)
    assert r.status_code == 200, r.text
    body = r.json()["data"]
    assert body["to_review"] == 4 and len(body["rows"]) == 4
    flags = [r["flags"] for r in body["rows"]]
    assert "dashain-holidays" in flags[0] and "saturday" in flags[1] and flags[2] == ["incomplete_holiday_coverage"]
    assert body["rows"][3]["error"] is not None


def test_holidays_ics() -> None:
    r = client.get("/v1/holidays/2083.ics")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/calendar")
    assert "SUMMARY:Ghatasthapana" in r.text and "DTSTART;VALUE=DATE:20261011" in r.text
    from parva import holidays

    assert r.text.count("BEGIN:VEVENT") == sum(
        h.get("closure", True) and h.get("review") == "source_checked" for h in holidays.of_year(2083, "national")
    )


def test_panchanga_audit_sources() -> None:
    p = get("/v1/panchanga", ad="2026-10-11")["data"]
    assert p["tithi"] == 1 and p["paksha"] == "shukla" and p["bs"]["text"] == "2083-06-25"
    a = get("/v1/audit/2026")["data"]
    assert a["compared"] >= 15 and a["agree"] >= a["compared"] - 2
    assert "moha-2083" in get("/v1/sources")["data"]["sources"]
