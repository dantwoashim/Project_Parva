"""Failures reproduced during the calendar review, fixed at their public boundaries."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from parva import astro, bs, festivals, holidays, review
from parva.api import app, create_app

client = TestClient(app)


@pytest.mark.parametrize("day", ["2026-10-23", "2026-11-12", "2025-10-24"])
def test_inclusive_closure_endpoints(day: str) -> None:
    assert holidays.is_working_day(date.fromisoformat(day)) is False


def test_missing_and_partial_coverage_are_unknown() -> None:
    for day in (date(2030, 4, 15), date(2026, 10, 27)):
        result = client.get("/v1/working-day", params={"ad": day.isoformat()}).json()["data"]
        assert result["working"] is None
        assert result["status"] == "unknown"
        assert result["next_working_day"] is None
        assert result["gazette_covers_year"] is False


def test_scope_validation_and_union() -> None:
    assert client.get("/v1/working-day?ad=2026-09-14&scope=woemn").status_code == 400
    assert client.get("/v1/working-day?ad=2026-09-14&weekend=typo").status_code == 422
    assert holidays.is_working_day(date(2026, 9, 14), scope="women,kathmandu-valley") is False
    assert holidays.is_working_day(bs.to_ad(2083, 10, 28)) is None
    assert holidays.is_working_day(bs.to_ad(2083, 10, 28), scope="schools") is False
    assert holidays.on(bs.to_ad(2083, 5, 23)) == []


def test_calendar_includes_spans_starting_previous_month() -> None:
    rows = client.get("/v1/month/2083/7").json()["data"]["holidays"]
    assert next(row for row in rows if row["id"] == "dashain-holidays")["days"] == 7


def test_upcoming_keeps_nearest_occurrence() -> None:
    rows = festivals.upcoming(date(2026, 10, 1), 100)
    assert next(row for row in rows if row.id == "dashain").start == date(2026, 10, 11)
    assert rows[0].start.year == 2026


@pytest.mark.parametrize(
    "text",
    [
        "name\nPrabin\n",
        "date,name\n2026-01-01\n",
        "date\n2026-01-01,extra\n",
        'date\n"unterminated',
        "date,date\n2026-01-01,2026-02-01\n",
    ],
)
def test_malformed_csv_is_rejected(text: str) -> None:
    assert client.post("/v1/check", content=text).status_code == 400


def test_csv_size_encoding_and_per_row_provenance() -> None:
    assert client.post("/v1/check", content=b"date\n\xff").status_code == 400
    assert client.post("/v1/check", content=b"x" * (review.MAX_CSV_BYTES + 1)).status_code == 413
    response = client.post("/v1/check", content="date\n2026-10-19\n2030-04-15\n").json()
    assert response["source"] == "per-row"
    first, second = response["data"]["rows"]
    assert first["source"] == "moha-2083" and second["source"] is None
    assert first["coverage"] == "partial" and second["coverage"] == "missing"


def test_explicit_calendar_and_range_boundaries() -> None:
    assert client.get("/v1/convert?ad=2026-04-14&bs=2083-01-01").status_code == 400
    assert client.get("/v1/festivals?year=9999").status_code == 400
    final = bs.END - timedelta(days=1)
    assert client.get("/v1/working-day", params={"ad": final.isoformat()}).status_code == 200
    assert holidays.next_working_day(final) is None
    assert review.review(["2083-01-01"])[0]["error"] is not None
    assert review.review(["2083-01-01"], force_bs=True)[0]["ad"] == "2026-04-14"


def test_static_files_and_spa_are_distinct(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<html>Parva</html>")
    (tmp_path / "festivals").mkdir()
    (tmp_path / "festivals/dashain.webp").write_bytes(b"RIFFfixture")
    browser = TestClient(create_app(tmp_path))
    assert browser.get("/festivals/dashain.webp").headers["content-type"] == "image/webp"
    assert browser.get("/festivals/dashain").text == "<html>Parva</html>"
    for path in ("/v1/unknown", "/assets/missing.js", "/festivals/missing.webp"):
        assert browser.get(path).status_code == 404


def test_ics_folding_and_review_status() -> None:
    text = client.get("/v1/holidays/2083.ics?scope=all").text
    assert all(len(line.encode("utf-8")) <= 75 for line in text.split("\r\n"))
    unfolded = text.replace("\r\n ", "")
    assert "civil-service-day-" not in unfolded and "genz-martyrs-day-" not in unfolded
    assert "DTEND;VALUE=DATE:20261024" in unfolded
    assert client.get("/v1/holidays/2081.ics").text.count("BEGIN:VEVENT") == 0


def test_threaded_ephemeris_and_invalid_solver_inputs() -> None:
    instant = datetime(2026, 10, 11, tzinfo=astro.NPT)
    expected = astro.longitudes(instant)
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert all(value == expected for value in pool.map(astro.longitudes, [instant] * 32))
    with pytest.raises(ValueError):
        astro.jd(datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        astro.solve(lambda _: 10, instant, 0)
    assert client.get("/v1/panchanga?ad=2026-01-01&lat=100").status_code == 422


def test_callers_cannot_mutate_cached_evidence() -> None:
    rows = holidays.of_year(2083)
    rows[0]["days"] = 999
    assert holidays.of_year(2083)[0]["days"] == 1
