"""Holiday evidence and conservative working-day decisions.

A recorded closure can establish a non-working day. An incomplete calendar cannot
establish a working day. Employer policy and later notices remain separate inputs.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, timedelta
from functools import cache
from typing import Literal, NotRequired, TypedDict

from . import bs
from .evidence import read_data

SATURDAY = frozenset({5})
FRIDAY_SATURDAY = frozenset({4, 5})
MAX_SEARCH_DAYS = 370
MAX_INTERVAL_DAYS = 3660


class Holiday(TypedDict):
    id: str
    name: str
    bs: str
    ad: str
    days: int
    scope: str
    weekday_verified: bool
    text: str
    scopes: NotRequired[list[str]]
    source_page: NotRequired[int]
    review: NotRequired[str]
    closure: NotRequired[bool]
    note: NotRequired[str]


class Gazette(TypedDict):
    bs_year: int
    source: str | None
    coverage: Literal["missing", "partial", "complete"]
    coverage_note: str
    days: list[Holiday]


@dataclass(frozen=True)
class WorkingDay:
    """A decision under the supplied weekend and scope policy, not payroll approval."""

    day: date
    working: bool | None
    reason: str
    source: str | None
    coverage: str
    weekend: bool
    holidays: tuple[Holiday, ...]

    @property
    def status(self) -> str:
        if self.working is None:
            return "unknown"
        return "working" if self.working else "non_working"


@cache
def _gazette(year: int) -> Gazette:
    payload = read_data(f"holidays/{year}.json", missing_ok=True)
    if payload is None:
        return {
            "bs_year": year,
            "source": None,
            "coverage": "missing",
            "coverage_note": "No holiday source is included for this year.",
            "days": [],
        }
    return Gazette(
        bs_year=year,
        source=payload["source"],
        coverage=payload["coverage"],
        coverage_note=payload["coverage_note"],
        days=payload["days"],
    )


def covered_years() -> list[int]:
    return list(read_data("release.json")["holiday_years"])


def source(year: int) -> str | None:
    return _gazette(year)["source"]


def coverage(year: int) -> str:
    return _gazette(year)["coverage"]


def coverage_note(year: int) -> str:
    return _gazette(year)["coverage_note"]


def scopes() -> tuple[str, ...]:
    return tuple(read_data("release.json")["scopes"])


def validate_scope(scope: str, *, listing: bool = False) -> tuple[str, ...]:
    """Comma-separated scopes form a union with national closures."""
    selected = tuple(part.strip() for part in scope.split(","))
    if listing and selected == ("all",):
        return selected
    if not selected or any(part not in scopes() for part in selected):
        raise ValueError(f"Unknown scope {scope!r}. Supported scopes: {', '.join(scopes())}")
    return selected


def of_year(year: int, scope: str = "national") -> list[Holiday]:
    selected = validate_scope(scope, listing=True)
    rows = _gazette(year)["days"]
    if selected == ("all",):
        return deepcopy(rows)
    applicable = {"national", *selected}
    return deepcopy([row for row in rows if applicable.intersection(row.get("scopes", [row["scope"]]))])


def on(day: date, scope: str = "national") -> list[Holiday]:
    return [
        row
        for row in of_year(bs.to_bs(day).year, scope)
        if row.get("closure", True) and 0 <= (day - date.fromisoformat(row["ad"])).days < row["days"]
    ]


def evaluate(day: date, *, weekend: frozenset[int] = SATURDAY, scope: str = "national") -> WorkingDay:
    validate_scope(scope)
    if any(type(value) is not int or not 0 <= value <= 6 for value in weekend):
        raise ValueError("Weekend values must be weekday integers from 0 to 6.")
    year = bs.to_bs(day).year
    matches = tuple(on(day, scope))
    is_weekend = day.weekday() in weekend
    if is_weekend:
        working, reason = False, "weekend"
    elif any(row.get("review") == "source_checked" for row in matches):
        working, reason = False, "reviewed_holiday"
    elif matches:
        working, reason = None, "holiday_needs_source_review"
    elif coverage(year) == "complete":
        working, reason = True, "no_closure_in_complete_source"
    else:
        working, reason = None, "incomplete_holiday_coverage"
    return WorkingDay(day, working, reason, source(year), coverage(year), is_weekend, matches)


def is_working_day(day: date, *, weekend: frozenset[int] = SATURDAY, scope: str = "national") -> bool | None:
    """True, False, or None when evidence cannot establish a working-day answer."""
    return evaluate(day, weekend=weekend, scope=scope).working


def _search(day: date, direction: int, weekend: frozenset[int], scope: str) -> date | None:
    validate_scope(scope)
    bs.to_bs(day)
    for _ in range(MAX_SEARCH_DAYS):
        day += timedelta(days=direction)
        if not bs.START[bs.MIN_YEAR] <= day < bs.END:
            return None
        result = evaluate(day, weekend=weekend, scope=scope)
        if result.working is None:
            return None
        if result.working:
            return day
    return None


def next_working_day(day: date, *, weekend: frozenset[int] = SATURDAY, scope: str = "national") -> date | None:
    return _search(day, 1, weekend, scope)


def previous_working_day(day: date, *, weekend: frozenset[int] = SATURDAY, scope: str = "national") -> date | None:
    return _search(day, -1, weekend, scope)


def working_days(start: date, end: date, *, weekend: frozenset[int] = SATURDAY, scope: str = "national") -> int | None:
    """Count an inclusive interval, or return None if any decision is unknown."""
    span = (end - start).days + 1
    if not 1 <= span <= MAX_INTERVAL_DAYS:
        raise ValueError(f"Interval must contain 1-{MAX_INTERVAL_DAYS} days.")
    bs.to_bs(start)
    bs.to_bs(end)
    count = 0
    for offset in range(span):
        result = evaluate(start + timedelta(days=offset), weekend=weekend, scope=scope)
        if result.working is None:
            return None
        count += result.working
    return count


def gazetted(holiday_id: str, ad_year: int) -> Holiday | None:
    for year in (ad_year + 56, ad_year + 57):
        for row in _gazette(year)["days"]:
            if row["id"] == holiday_id and row["ad"].startswith(str(ad_year)):
                return deepcopy(row)
    return None


from .fiscal import fiscal_year as fiscal_year  # noqa: E402
