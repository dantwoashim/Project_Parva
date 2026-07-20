from __future__ import annotations

from datetime import datetime, timezone

import pytest
from app.core.clock import (
    FixedClock,
    assume_timezone,
    civil_date,
    require_aware_datetime,
    utc_now,
)


def test_kathmandu_civil_date_changes_at_1815_utc() -> None:
    before_midnight = FixedClock(datetime(2026, 7, 15, 18, 14, 59, tzinfo=timezone.utc))
    at_midnight = FixedClock(datetime(2026, 7, 15, 18, 15, tzinfo=timezone.utc))

    assert civil_date(clock=before_midnight).isoformat() == "2026-07-15"
    assert civil_date(clock=at_midnight).isoformat() == "2026-07-16"


def test_civil_date_uses_requested_timezone() -> None:
    clock = FixedClock(datetime(2026, 3, 8, 4, 30, tzinfo=timezone.utc))

    assert civil_date(clock=clock, timezone_name="America/New_York").isoformat() == "2026-03-07"
    assert civil_date(clock=clock, timezone_name="Asia/Kathmandu").isoformat() == "2026-03-08"


def test_clock_rejects_naive_instants() -> None:
    with pytest.raises(ValueError, match="instant must be timezone-aware"):
        FixedClock(datetime(2026, 7, 15, 18, 15))


def test_utc_now_normalizes_an_aware_non_utc_clock() -> None:
    local = assume_timezone(datetime(2026, 7, 16, 0, 0), "Asia/Kathmandu")

    assert utc_now(clock=FixedClock(local)) == datetime(
        2026, 7, 15, 18, 15, tzinfo=timezone.utc
    )


def test_naive_datetime_requires_an_explicit_migration_assumption() -> None:
    naive = datetime(2026, 7, 16, 0, 0)

    with pytest.raises(ValueError, match="must be timezone-aware"):
        require_aware_datetime(naive)

    assumed = assume_timezone(naive, "Asia/Kathmandu")
    assert assumed.utcoffset().total_seconds() == 20_700


def test_unknown_timezone_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown timezone"):
        civil_date(
            clock=FixedClock(datetime(2026, 7, 15, tzinfo=timezone.utc)),
            timezone_name="Mars/Olympus",
        )
