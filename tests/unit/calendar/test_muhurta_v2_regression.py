"""Regression fixtures for Muhurta v2 across seasons and geographies."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.calendar.muhurta import get_auspicious_windows, get_muhurtas, get_rahu_kalam


FIXTURE_PATH = Path("tests/fixtures/muhurta/muhurta_v2_regression.json")


def _load_cases() -> list[dict]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload["cases"]


def _assert_approx(actual: float, expected: float, *, tolerance: float = 0.2) -> None:
    assert abs(actual - expected) <= tolerance, f"expected {expected}±{tolerance}, got {actual}"


def test_muhurta_regression_fixture_cases_stable():
    for case in _load_cases():
        target_date = date.fromisoformat(case["date"])

        day = get_muhurtas(
            target_date,
            lat=case["lat"],
            lon=case["lon"],
            tz_name=case["tz"],
            birth_nakshatra=case["birth_nakshatra"],
        )
        rahu = get_rahu_kalam(
            target_date,
            lat=case["lat"],
            lon=case["lon"],
            tz_name=case["tz"],
        )
        ranked = get_auspicious_windows(
            target_date,
            lat=case["lat"],
            lon=case["lon"],
            tz_name=case["tz"],
            ceremony_type=case["ceremony_type"],
            birth_nakshatra=case["birth_nakshatra"],
            assumption_set_id=case["assumption_set"],
        )

        expected = case["expect"]

        assert day["total_muhurtas"] == 30
        assert len(day["day_muhurtas"]) == 15
        assert len(day["night_muhurtas"]) == 15
        assert len(day["hora"]["day"]) == 12
        assert len(day["hora"]["night"]) == 12
        assert len(day["chaughadia"]["day"]) == 8
        assert len(day["chaughadia"]["night"]) == 8

        _assert_approx(day["daylight_minutes"], expected["daylight_minutes"])
        _assert_approx(day["night_minutes"], expected["night_minutes"])

        assert day["hora"]["day"][0]["lord"] == expected["hora_day_first_lord"]
        assert day["chaughadia"]["day"][0]["name"] == expected["chaughadia_day_first"]
        assert rahu["rahu_kalam"]["segment"] == expected["rahu_segment"]

        assert ranked["best_window"]["name"] == expected["best_window_name"]
        assert ranked["best_window"]["score"] == expected["best_window_score"]
        assert ranked["tara_bala"]["quality"] == expected["tara_quality"]
        assert len(ranked["auspicious_muhurtas"]) >= expected["auspicious_count_min"]


def test_assumption_sets_affect_scores_for_same_window():
    target_date = date.fromisoformat("2026-03-21")
    common = {
        "lat": 27.7172,
        "lon": 85.3240,
        "tz_name": "Asia/Kathmandu",
        "ceremony_type": "vivah",
        "birth_nakshatra": "7",
    }

    strict = get_auspicious_windows(target_date, assumption_set_id="np-mainstream-v2", **common)
    practical = get_auspicious_windows(target_date, assumption_set_id="diaspora-practical-v2", **common)

    assert strict["assumption_set_id"] == "np-mainstream-v2"
    assert practical["assumption_set_id"] == "diaspora-practical-v2"

    assert strict["best_window"]["name"] == practical["best_window"]["name"]
    assert strict["best_window"]["score"] != practical["best_window"]["score"]
