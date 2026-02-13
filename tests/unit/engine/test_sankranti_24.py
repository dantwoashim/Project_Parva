"""Sankranti regression tests (Week 19)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.calendar.sankranti import get_sankrantis_in_year


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "sankranti_24.json"


def test_sankranti_fixture_size():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["metadata"]["samples"] == 24
    assert len(data["sankrantis"]) == 24


def test_sankranti_dates_match_regression_baseline():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    by_year = {}
    for row in data["sankrantis"]:
        by_year.setdefault(row["year"], []).append(row)

    for year, expected_rows in by_year.items():
        actual_rows = get_sankrantis_in_year(year)
        assert len(actual_rows) == len(expected_rows)

        for expected, actual in zip(expected_rows, actual_rows):
            assert actual["rashi_index"] == expected["rashi_index"]
            assert actual["rashi_name"] == expected["rashi_name"]
            assert actual["date"].isoformat() == expected["date"]

            expected_dt = datetime.fromisoformat(expected["datetime_utc"])
            delta = abs((actual["datetime_utc"] - expected_dt).total_seconds())
            assert delta <= 120
