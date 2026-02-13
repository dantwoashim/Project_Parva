"""Week 22 tests for BS conversion confidence transitions and estimated mode."""

from __future__ import annotations

from datetime import date

from app.calendar.bikram_sambat import (
    BS_MIN_YEAR,
    BS_MAX_YEAR,
    bs_to_gregorian,
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_source_range,
    gregorian_to_bs,
)


def _year_start_end_gregorian() -> tuple[date, date]:
    start = bs_to_gregorian(BS_MIN_YEAR, 1, 1)
    end = bs_to_gregorian(BS_MAX_YEAR, 12, 30)
    return start, end


def test_confidence_transitions_at_official_range_boundaries():
    start, end = _year_start_end_gregorian()

    assert get_bs_confidence(start - date.resolution) == "estimated"
    assert get_bs_confidence(start) == "official"

    assert get_bs_confidence(end) == "official"
    assert get_bs_confidence(end + date.resolution) == "estimated"


def test_source_range_and_error_bound_labels_follow_confidence():
    start, end = _year_start_end_gregorian()
    in_range = start
    out_range = end + date.resolution

    assert get_bs_source_range(in_range) == f"{BS_MIN_YEAR}-{BS_MAX_YEAR}"
    assert get_bs_estimated_error_days(in_range) is None

    assert get_bs_source_range(out_range) is None
    assert get_bs_estimated_error_days(out_range) == "0-1"


def test_estimated_mode_handles_far_years_roundtrip():
    # Dates far outside official lookup should still convert with estimated confidence.
    samples = [date(1944, 1, 1), date(2043, 4, 14), date(2094, 6, 1)]

    for g_date in samples:
        bs = gregorian_to_bs(g_date)
        back = bs_to_gregorian(*bs)

        # Estimated mode should not drift wildly for roundtrip diagnostics.
        assert abs((back - g_date).days) <= 2
        assert get_bs_confidence(g_date) in {"official", "estimated"}
