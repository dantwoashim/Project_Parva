"""Lunar month boundary API tests (Week 18)."""

from __future__ import annotations

from datetime import timedelta

from app.calendar.lunar_calendar import (
    lunar_month_boundaries,
    name_lunar_month,
    detect_adhik_maas,
)


def test_lunar_month_boundaries_cover_year():
    boundaries = lunar_month_boundaries(2026)
    assert len(boundaries) >= 11

    # Ensure monotonic and non-overlapping.
    for i in range(len(boundaries) - 1):
        s1, e1 = boundaries[i]
        s2, e2 = boundaries[i + 1]
        assert s1 < e1
        assert s2 >= e1


def test_lunar_month_name_and_adhik_detection_work_for_boundaries():
    boundaries = lunar_month_boundaries(2026)
    start, end = boundaries[0]

    month_name = name_lunar_month(start, end)
    assert isinstance(month_name, str)
    assert len(month_name) > 0

    is_adhik = detect_adhik_maas(start, end)
    assert isinstance(is_adhik, bool)
