"""Exhaustive BS/AD and Nepal fiscal-period checks for the official range."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_source_range,
    get_bs_year_end,
    get_bs_year_start,
    gregorian_to_bs,
    gregorian_to_bs_official,
    is_valid_bs_date,
)
from app.calendar.constants import BS_CALENDAR_DATA, BS_MAX_YEAR, BS_MIN_YEAR
from app.calendar.fiscal import (
    fiscal_month_for_bs_month,
    fiscal_period_for_bs_date,
    fiscal_period_for_gregorian,
    fiscal_year_label,
    fiscal_year_start_for_bs_date,
)

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "bs_overlap_comparison.json"


def _all_official_bs_dates():
    for year in range(BS_MIN_YEAR, BS_MAX_YEAR + 1):
        for month in range(1, 13):
            for day in range(1, days_in_bs_month(year, month) + 1):
                yield year, month, day


def _parse_bs(value: str) -> tuple[int, int, int]:
    year, month, day = value.split("-")
    return int(year), int(month), int(day)


def test_official_table_shape_is_complete_and_bounded():
    assert (BS_MIN_YEAR, BS_MAX_YEAR) == (2070, 2095)
    assert len(BS_CALENDAR_DATA) == 26

    total_days = 0
    for year in range(BS_MIN_YEAR, BS_MAX_YEAR + 1):
        month_lengths, start = BS_CALENDAR_DATA[year]
        assert len(month_lengths) == 12
        assert all(29 <= length <= 32 for length in month_lengths)
        assert sum(month_lengths) in {365, 366}
        assert start == get_bs_year_start(year)
        assert get_bs_year_end(year) == start + timedelta(days=sum(month_lengths) - 1)
        total_days += sum(month_lengths)

    assert total_days == 9498
    assert get_bs_year_start(BS_MIN_YEAR) == date(2013, 4, 13)
    assert get_bs_year_end(BS_MAX_YEAR) == date(2039, 4, 14)


def test_every_official_bs_date_round_trips_without_gap_overlap_or_confidence_leak():
    seen_ad_dates: set[date] = set()
    previous_ad: date | None = None
    total = 0

    for bs_date in _all_official_bs_dates():
        year, month, day = bs_date
        ad_date = bs_to_gregorian(year, month, day)

        assert is_valid_bs_date(year, month, day) is True
        assert ad_date not in seen_ad_dates
        if previous_ad is not None:
            assert ad_date == previous_ad + timedelta(days=1)

        assert gregorian_to_bs_official(ad_date) == bs_date
        assert gregorian_to_bs(ad_date) == bs_date
        assert bs_to_gregorian(*gregorian_to_bs(ad_date)) == ad_date
        assert get_bs_confidence(ad_date) == "official"
        assert get_bs_source_range(ad_date) == "2070-2095"
        assert get_bs_estimated_error_days(ad_date) is None

        seen_ad_dates.add(ad_date)
        previous_ad = ad_date
        total += 1

    assert total == 9498
    assert len(seen_ad_dates) == 9498


def test_every_official_gregorian_date_matches_golden_fixture_rows():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = fixture["rows"]
    metadata = fixture["metadata"]

    assert metadata["official_bs_range"] == "2070-2095"
    assert metadata["gregorian_start"] == "2013-04-13"
    assert metadata["gregorian_end"] == "2039-04-14"
    assert metadata["total_days"] == 9498
    assert len(rows) == metadata["total_days"]

    current = date.fromisoformat(metadata["gregorian_start"])
    end = date.fromisoformat(metadata["gregorian_end"])
    for row in rows:
        assert row["gregorian"] == current.isoformat()
        official_bs = _parse_bs(row["official_bs"])
        assert gregorian_to_bs_official(current) == official_bs
        assert gregorian_to_bs(current) == official_bs
        assert bs_to_gregorian(*official_bs) == current
        current += timedelta(days=1)

    assert current == end + timedelta(days=1)


def test_official_month_and_year_boundaries_are_strict():
    for year in range(BS_MIN_YEAR, BS_MAX_YEAR + 1):
        assert bs_to_gregorian(year, 1, 1) == get_bs_year_start(year)
        assert bs_to_gregorian(year, 12, days_in_bs_month(year, 12)) == get_bs_year_end(year)

        if year < BS_MAX_YEAR:
            assert get_bs_year_end(year) + timedelta(days=1) == get_bs_year_start(year + 1)

        for month in range(1, 13):
            month_length = days_in_bs_month(year, month)
            month_start = bs_to_gregorian(year, month, 1)
            month_end = bs_to_gregorian(year, month, month_length)
            assert month_end - month_start == timedelta(days=month_length - 1)
            if month < 12:
                assert month_end + timedelta(days=1) == bs_to_gregorian(year, month + 1, 1)
            elif year < BS_MAX_YEAR:
                assert month_end + timedelta(days=1) == bs_to_gregorian(year + 1, 1, 1)


def test_invalid_edge_dates_are_rejected_at_every_official_month_boundary():
    for year in range(BS_MIN_YEAR, BS_MAX_YEAR + 1):
        assert is_valid_bs_date(year, 0, 1) is False
        assert is_valid_bs_date(year, 13, 1) is False
        for month in range(1, 13):
            month_length = days_in_bs_month(year, month)
            assert is_valid_bs_date(year, month, 0) is False
            assert is_valid_bs_date(year, month, month_length + 1) is False
            with pytest.raises(ValueError):
                bs_to_gregorian(year, month, 0)
            with pytest.raises(ValueError):
                bs_to_gregorian(year, month, month_length + 1)


def test_nepal_fiscal_month_mapping_is_shrawan_based():
    expected = {
        1: 10,  # Baishakh
        2: 11,  # Jestha
        3: 12,  # Ashadh
        4: 1,  # Shrawan
        5: 2,
        6: 3,
        7: 4,
        8: 5,
        9: 6,
        10: 7,
        11: 8,
        12: 9,
    }
    for bs_month, fiscal_month in expected.items():
        assert fiscal_month_for_bs_month(bs_month) == fiscal_month

    with pytest.raises(ValueError):
        fiscal_month_for_bs_month(0)
    with pytest.raises(ValueError):
        fiscal_month_for_bs_month(13)


def test_fiscal_period_for_every_official_bs_date_matches_bs_and_ad_paths():
    for year, month, day in _all_official_bs_dates():
        ad_date = bs_to_gregorian(year, month, day)
        period = fiscal_period_for_bs_date(year, month, day)

        expected_fiscal_start = year if month >= 4 else year - 1
        expected_fiscal_month = ((month - 4) % 12) + 1
        assert period.bs_year == year
        assert period.bs_month == month
        assert period.bs_day == day
        assert period.fiscal_year_start == expected_fiscal_start
        assert period.fiscal_year_end == expected_fiscal_start + 1
        assert period.fiscal_year_label == fiscal_year_label(expected_fiscal_start)
        assert period.fiscal_month == expected_fiscal_month
        assert period.fiscal_quarter == ((expected_fiscal_month - 1) // 3) + 1
        assert fiscal_period_for_gregorian(ad_date) == period
        assert fiscal_year_start_for_bs_date(year, month) == expected_fiscal_start


def test_fiscal_year_boundaries_roll_over_on_shrawan_one():
    for fiscal_year_start in range(BS_MIN_YEAR, BS_MAX_YEAR):
        ashadh_end_day = days_in_bs_month(fiscal_year_start + 1, 3)
        fiscal_start = bs_to_gregorian(fiscal_year_start, 4, 1)
        fiscal_end = bs_to_gregorian(fiscal_year_start + 1, 3, ashadh_end_day)

        expected_days = sum(days_in_bs_month(fiscal_year_start, month) for month in range(4, 13))
        expected_days += sum(days_in_bs_month(fiscal_year_start + 1, month) for month in range(1, 4))

        assert fiscal_end - fiscal_start == timedelta(days=expected_days - 1)
        assert fiscal_period_for_bs_date(fiscal_year_start, 4, 1).fiscal_month == 1
        assert fiscal_period_for_bs_date(fiscal_year_start, 4, 1).fiscal_quarter == 1
        assert fiscal_period_for_bs_date(
            fiscal_year_start + 1, 3, ashadh_end_day
        ).fiscal_month == 12
        assert fiscal_period_for_bs_date(
            fiscal_year_start + 1, 3, ashadh_end_day
        ).fiscal_quarter == 4
        assert fiscal_period_for_bs_date(
            fiscal_year_start + 1, 3, ashadh_end_day
        ).fiscal_year_label == fiscal_year_label(fiscal_year_start)

        if fiscal_year_start + 1 <= BS_MAX_YEAR:
            next_period = fiscal_period_for_bs_date(fiscal_year_start + 1, 4, 1)
            assert next_period.fiscal_year_start == fiscal_year_start + 1
            assert next_period.fiscal_month == 1
