"""Kundali v2 regression corpus (Month 6 hardening)."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from app.calendar.kundali import compute_kundali


FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "kundali" / "kundali_v2_regression.json"


def _load_cases() -> list[dict]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload.get("cases", [])


def test_kundali_v2_regression_corpus_is_stable():
    cases = _load_cases()
    assert cases

    for case in cases:
        expected = case["expected"]
        result = compute_kundali(
            datetime.fromisoformat(case["datetime"]),
            lat=float(case["lat"]),
            lon=float(case["lon"]),
            tz_name=case["tz"],
        )

        assert result["lagna"]["rashi_number"] == expected["lagna_rashi"], case["id"]
        assert result["lagna"]["rashi_english"] == expected["lagna_name"], case["id"]

        assert len(result["aspects"]) == expected["aspect_count"], case["id"]
        assert [row["id"] for row in result["yogas"]] == expected["yoga_ids"], case["id"]
        assert [row["id"] for row in result["doshas"]] == expected["dosha_ids"], case["id"]

        first_major = result["dasha"]["timeline"][0]
        assert first_major["lord"] == expected["first_major_lord"], case["id"]
        assert first_major["duration_years"] == expected["first_major_years"], case["id"]

        first_antar = first_major["antar_dasha"][0]
        assert first_antar["lord"] == expected["first_antar_lord"], case["id"]

        assert result["grahas"]["mars"]["dignity"]["state"] == expected["mars_dignity"], case["id"]

        pass_checks = [row for row in result["consistency_checks"] if row.get("status") == "pass"]
        assert len(pass_checks) == expected["consistency_pass_count"], case["id"]


def test_kundali_v2_dasha_antar_has_nine_segments():
    result = compute_kundali(
        datetime.fromisoformat("2026-02-15T06:30:00+05:45"),
        lat=27.7172,
        lon=85.3240,
        tz_name="Asia/Kathmandu",
    )

    major_periods = result["dasha"]["timeline"]
    assert major_periods
    assert len(major_periods) == 9
    assert all(len(period["antar_dasha"]) == 9 for period in major_periods)
