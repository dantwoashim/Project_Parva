"""Week 9 timezone hardening tests."""

from datetime import date, datetime, timezone, timedelta

import pytest

from app.engine.time_utils import ensure_utc, from_npt, to_npt
from app.calendar.ephemeris.time_utils import NEPAL_TZ
from app.calendar.ephemeris.swiss_eph import get_julian_day, TimezoneError


@pytest.mark.parametrize(
    "input_dt,expected_hour",
    [
        (datetime(2026, 2, 7, 0, 0, tzinfo=timezone.utc), 0),
        (datetime(2026, 2, 7, 5, 45, tzinfo=NEPAL_TZ), 0),
        (datetime(2026, 2, 7, 0, 0), 0),
    ],
)
def test_ensure_utc_normalizes_to_utc(input_dt, expected_hour):
    normalized = ensure_utc(input_dt)
    assert normalized.tzinfo == timezone.utc
    assert normalized.hour == expected_hour


def test_ensure_utc_from_date_assumes_midnight_utc():
    normalized = ensure_utc(date(2026, 2, 7))
    assert normalized.tzinfo == timezone.utc
    assert normalized.hour == 0


def test_to_npt_and_back_roundtrip():
    original = datetime(2026, 2, 7, 12, 30, tzinfo=timezone.utc)
    npt = to_npt(original)
    roundtrip = from_npt(npt)
    assert roundtrip == original


def test_from_npt_naive_assumes_nepal_time():
    local = datetime(2026, 2, 7, 6, 0)  # naive => Nepal time
    utc = from_npt(local)
    assert utc.tzinfo == timezone.utc
    assert utc.hour == 0
    assert utc.minute == 15


def test_get_julian_day_requires_timezone_aware_datetime():
    with pytest.raises(TimezoneError):
        get_julian_day(datetime(2026, 2, 7, 0, 0))


def test_get_julian_day_accepts_aware_datetimes_with_any_tz():
    utc = datetime(2026, 2, 7, 0, 0, tzinfo=timezone.utc)
    npt = datetime(2026, 2, 7, 5, 45, tzinfo=NEPAL_TZ)
    assert abs(get_julian_day(utc) - get_julian_day(npt)) < 1e-9


def test_nepal_midnight_crossover_behavior():
    # 00:10 NPT is previous UTC date
    npt = datetime(2026, 2, 7, 0, 10, tzinfo=NEPAL_TZ)
    utc = ensure_utc(npt)
    assert utc.date().isoformat() == "2026-02-06"


def test_non_dst_timezone_remains_stable():
    # Nepal has no DST. Offset should be fixed +5:45 year-round.
    winter = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc).astimezone(NEPAL_TZ)
    summer = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc).astimezone(NEPAL_TZ)
    assert winter.utcoffset() == timedelta(hours=5, minutes=45)
    assert summer.utcoffset() == timedelta(hours=5, minutes=45)


def test_date_line_scenario_with_extreme_offset():
    # Simulates diaspora timezone conversion edge behavior.
    plus14 = timezone(timedelta(hours=14))
    dt = datetime(2026, 2, 7, 1, 0, tzinfo=plus14)
    utc = ensure_utc(dt)
    assert utc.tzinfo == timezone.utc
    assert utc.date().isoformat() == "2026-02-06"
