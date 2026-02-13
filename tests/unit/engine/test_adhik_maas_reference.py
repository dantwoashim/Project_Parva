"""Adhik-Maas regression tests (Week 17)."""

from __future__ import annotations

import json
from pathlib import Path

from app.calendar.lunar_calendar import get_lunar_year


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "adhik_maas_reference.json"


def test_adhik_reference_fixture_shape():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["metadata"]["range_bs"] == "2000-2030"
    assert len(data["years"]) == 31


def test_adhik_detection_matches_regression_baseline():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    for row in data["years"]:
        lunar_year = get_lunar_year(row["gregorian_year"])
        actual = sorted({m.full_name for m in lunar_year.months if m.is_adhik})

        assert bool(actual) == row["has_adhik"]
        assert actual == row["adhik_months"]
