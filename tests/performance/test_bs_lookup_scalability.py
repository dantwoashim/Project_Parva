from __future__ import annotations

import time
from datetime import timedelta

from app.calendar.bikram_sambat import gregorian_to_bs_official
from app.calendar.constants import BS_CALENDAR_DATA, BS_MAX_YEAR, BS_MIN_YEAR


def test_gregorian_to_bs_official_lookup_stays_fast_across_supported_range():
    dates = []
    for year in range(BS_MIN_YEAR, BS_MAX_YEAR + 1):
        month_lengths, start = BS_CALENDAR_DATA[year]
        dates.append(start)
        dates.append(start + timedelta(days=sum(month_lengths) // 2))
        dates.append(start + timedelta(days=sum(month_lengths) - 1))

    started = time.perf_counter()
    for _ in range(200):
        for item in dates:
            gregorian_to_bs_official(item)
    elapsed = time.perf_counter() - started

    assert elapsed < 0.5
