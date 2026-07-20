"""Canonical clock and civil-date helpers.

Runtime code receives a clock explicitly or through ``app.state.clock``. This
keeps host timezone settings out of calendar decisions and makes date-boundary
behavior deterministic in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone, tzinfo
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_CIVIL_TIMEZONE = "Asia/Kathmandu"


class Clock(Protocol):
    """Source of timezone-aware instants."""

    def now(self) -> datetime:
        """Return the current instant as a timezone-aware datetime."""


@dataclass(frozen=True)
class SystemClock:
    """Production wall clock."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass(frozen=True)
class FixedClock:
    """Immutable clock for tests, replay, and deterministic jobs."""

    instant: datetime

    def __post_init__(self) -> None:
        require_aware_datetime(self.instant, parameter="instant")

    def now(self) -> datetime:
        return self.instant


SYSTEM_CLOCK = SystemClock()


def require_aware_datetime(value: datetime, *, parameter: str = "datetime") -> datetime:
    """Reject a datetime whose timezone and UTC offset are unspecified."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{parameter} must be timezone-aware")
    return value


def assume_timezone(value: datetime, timezone_name: str) -> datetime:
    """Attach an explicit timezone to a legacy naive datetime.

    This migration helper makes the assumption visible at its call site. Normal
    calculation paths should accept aware datetimes instead.
    """

    if value.tzinfo is not None and value.utcoffset() is not None:
        raise ValueError("assume_timezone accepts only a naive datetime")
    return value.replace(tzinfo=resolve_timezone(timezone_name))


def resolve_timezone(timezone_name: str = DEFAULT_CIVIL_TIMEZONE) -> tzinfo:
    """Resolve an IANA timezone name or raise a stable validation error."""

    normalized = timezone_name.strip() or DEFAULT_CIVIL_TIMEZONE
    try:
        return ZoneInfo(normalized)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {normalized}") from exc


def utc_now(*, clock: Clock = SYSTEM_CLOCK) -> datetime:
    """Read a clock and normalize its aware instant to UTC."""

    return require_aware_datetime(clock.now(), parameter="clock.now()").astimezone(timezone.utc)


def civil_date(
    *,
    clock: Clock = SYSTEM_CLOCK,
    timezone_name: str = DEFAULT_CIVIL_TIMEZONE,
) -> date:
    """Return the current civil date in the requested timezone."""

    return utc_now(clock=clock).astimezone(resolve_timezone(timezone_name)).date()


__all__ = [
    "Clock",
    "DEFAULT_CIVIL_TIMEZONE",
    "FixedClock",
    "SYSTEM_CLOCK",
    "SystemClock",
    "assume_timezone",
    "civil_date",
    "require_aware_datetime",
    "resolve_timezone",
    "utc_now",
]
