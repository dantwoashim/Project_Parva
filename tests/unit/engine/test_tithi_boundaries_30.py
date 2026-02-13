"""Boundary corpus tests for udaya-tithi behavior (Week 14)."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from app.calendar.tithi.tithi_udaya import get_udaya_tithi, detect_vriddhi, detect_ksheepana


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "tithi_boundaries_30.json"


def test_boundary_fixture_has_expected_sample_size():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["metadata"]["samples"] == 30
    assert len(data["samples"]) == 30


def test_boundary_cases_match_expected_tithi_and_flags():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    for row in data["samples"]:
        d = date.fromisoformat(row["date"])
        actual = get_udaya_tithi(d)

        assert actual["tithi"] == row["tithi"]
        assert actual["paksha"] == row["paksha"]
        assert detect_vriddhi(d) == row["vriddhi"]
        assert detect_ksheepana(d) == row["ksheepana"]

        # sunrise is deterministic within 60 seconds for regression
        expected_sunrise = datetime.fromisoformat(row["sunrise_utc"])
        delta = abs((actual["sunrise"] - expected_sunrise).total_seconds())
        assert delta <= 60
