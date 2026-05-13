from __future__ import annotations

from datetime import timedelta

from app.calendar.bikram_sambat import gregorian_to_bs_official
from app.calendar.constants import BS_CALENDAR_DATA, BS_MAX_YEAR, BS_MIN_YEAR


def test_gregorian_to_bs_official_uses_correct_year_boundaries():
    first_start = BS_CALENDAR_DATA[BS_MIN_YEAR][1]
    assert gregorian_to_bs_official(first_start) == (BS_MIN_YEAR, 1, 1)

    year = BS_MIN_YEAR
    month_lengths, year_start = BS_CALENDAR_DATA[year]
    next_year_start = year_start + timedelta(days=sum(month_lengths))
    assert gregorian_to_bs_official(next_year_start) == (year + 1, 1, 1)

    max_lengths, max_start = BS_CALENDAR_DATA[BS_MAX_YEAR]
    max_end = max_start + timedelta(days=sum(max_lengths) - 1)
    assert gregorian_to_bs_official(max_end) == (BS_MAX_YEAR, 12, max_lengths[-1])
