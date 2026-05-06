"""BS conversion confidence transitions and estimated mode."""

from __future__ import annotations

from datetime import date

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR
from app.calendar.provenance import STATIC_LOOKUP_RANGE_LABEL


def _year_start_end_gregorian() -> tuple[date, date]:
    start = bs_to_gregorian(BS_MIN_YEAR, 1, 1)
    end = bs_to_gregorian(BS_MAX_YEAR, 12, days_in_bs_month(BS_MAX_YEAR, 12))
    return start, end


def test_confidence_transitions_at_static_lookup_range_boundaries():
    start, end = _year_start_end_gregorian()

    assert get_bs_confidence(start - date.resolution) == "estimated"
    assert get_bs_confidence(start) == "static_lookup"

    assert get_bs_confidence(end) == "static_lookup"
    assert get_bs_confidence(end + date.resolution) == "estimated"


def test_source_range_and_error_bound_labels_follow_confidence():
    start, end = _year_start_end_gregorian()
    in_range = start
    out_range = end + date.resolution

    assert get_bs_source_range(in_range) == STATIC_LOOKUP_RANGE_LABEL
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
        assert get_bs_confidence(g_date) in {"official", "static_lookup", "estimated"}
