"""Bikram Sambat <-> Gregorian.  A table and two cumulative sums.  No dependencies.

Conversion uses a community month-length table. Published-calendar fixtures cover
BS 2078-2083; later years are provisional. Source labels describe evidence, not
government endorsement of the entire table.

    >>> to_bs(date(2026, 4, 14))
    BS(year=2083, month=1, day=1)
    >>> to_ad(2083, 3, 32)
    datetime.date(2026, 7, 16)
"""

from __future__ import annotations

import hashlib
import json
from bisect import bisect_right
from datetime import date, timedelta
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import NamedTuple

_TABLE = json.loads((files("parva") / "data" / "bs_months.json").read_text("utf-8"))

DATA_VERSION: str = _TABLE["version"]
MONTHS: dict[int, tuple[int, ...]] = {int(y): tuple(m) for y, m in _TABLE["months"].items()}
YEARS: tuple[int, ...] = tuple(sorted(MONTHS))
MIN_YEAR, MAX_YEAR = YEARS[0], YEARS[-1]

NAMES = (
    "Baishakh",
    "Jestha",
    "Ashadh",
    "Shrawan",
    "Bhadra",
    "Ashwin",
    "Kartik",
    "Mangsir",
    "Poush",
    "Magh",
    "Falgun",
    "Chaitra",
)
NAMES_NE = ("वैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज", "कात्तिक", "मंसिर", "पुस", "माघ", "फागुन", "चैत")
WEEKDAYS_NE = ("सोमबार", "मङ्गलबार", "बुधबार", "बिहीबार", "शुक्रबार", "शनिबार", "आइतबार")  # Monday first
_DIGITS_NE = str.maketrans("0123456789", "०१२३४५६७८९")


def _year_starts() -> dict[int, date]:
    """Gregorian date of 1 Baishakh for every year, walked out from the anchor."""
    (anchor_year, _, _), anchor_ad = _TABLE["anchor"]["bs"], date.fromisoformat(_TABLE["anchor"]["ad"])
    starts = {anchor_year: anchor_ad}
    for y in range(anchor_year + 1, MAX_YEAR + 1):
        starts[y] = starts[y - 1] + timedelta(days=sum(MONTHS[y - 1]))
    for y in range(anchor_year - 1, MIN_YEAR - 1, -1):
        starts[y] = starts[y + 1] - timedelta(days=sum(MONTHS[y]))
    return starts


START: dict[int, date] = _year_starts()
END: date = START[MAX_YEAR] + timedelta(days=sum(MONTHS[MAX_YEAR]))  # exclusive
_STARTS = [START[y] for y in YEARS]
_SOURCES = {y: tuple(r["sources"]) for r in _TABLE["sources"] for y in range(r["years"][0], r["years"][1] + 1)}


def _data_sha256() -> str:
    """sha256 over every file under parva/data: `relpath\n` + bytes, sorted by posix relpath."""
    found: list[tuple[str, Traversable]] = []

    def walk(d: Traversable, prefix: str) -> None:
        for c in d.iterdir():
            walk(c, f"{prefix}{c.name}/") if c.is_dir() else found.append((f"{prefix}{c.name}", c))

    walk(files("parva") / "data", "")
    h = hashlib.sha256()
    for name, f in sorted(found):
        h.update(f"{name}\n".encode())
        h.update(f.read_bytes())
    return h.hexdigest()


DATA_SHA256: str = _data_sha256()


class BS(NamedTuple):
    """A Bikram Sambat calendar date."""

    year: int
    month: int
    day: int

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    @property
    def month_name(self) -> str:
        return NAMES[self.month - 1]

    @property
    def month_name_ne(self) -> str:
        return NAMES_NE[self.month - 1]

    @property
    def sources(self) -> tuple[str, ...]:
        """Source ids (see data/SOURCES.json) that back this year's month lengths."""
        return _SOURCES.get(self.year, ())

    @property
    def ad(self) -> date:
        return to_ad(*self)

    def nepali(self) -> str:
        """'२०८३ असोज २७, आइतबार'"""
        return f"{self.year} {self.month_name_ne} {self.day}, {WEEKDAYS_NE[self.ad.weekday()]}".translate(_DIGITS_NE)


def month_days(year: int, month: int) -> int:
    """Number of days in a BS month (29-32)."""
    if year not in MONTHS:
        raise ValueError(f"BS {year} is outside the table ({MIN_YEAR}-{MAX_YEAR})")
    if not 1 <= month <= 12:
        raise ValueError(f"month must be 1-12, got {month}")
    return MONTHS[year][month - 1]


def is_valid(year: int, month: int, day: int) -> bool:
    if any(type(value) is not int for value in (year, month, day)):
        return False
    try:
        return 1 <= day <= month_days(year, month)
    except ValueError:
        return False


def to_ad(year: int, month: int, day: int) -> date:
    """BS -> Gregorian.  Raises ValueError for a date that does not exist."""
    if not is_valid(year, month, day):
        raise ValueError(f"BS {year:04d}-{month:02d}-{day:02d} does not exist")
    return START[year] + timedelta(days=sum(MONTHS[year][: month - 1]) + day - 1)


def to_bs(d: date) -> BS:
    """Gregorian -> BS.  Raises ValueError outside the table."""
    i = bisect_right(_STARTS, d) - 1
    if i < 0 or d >= END:
        raise ValueError(f"{d.isoformat()} is outside the table ({START[MIN_YEAR]} to {END - timedelta(days=1)})")
    year, n = YEARS[i], (d - START[YEARS[i]]).days
    for month, length in enumerate(MONTHS[year], start=1):
        if n < length:
            return BS(year, month, n + 1)
        n -= length
    raise AssertionError("unreachable: the year's month lengths sum to its span")


def parse(text: str) -> BS:
    """'2083-06-27' or '२०८३-०६-२७' -> BS.  Validates."""
    try:
        y, m, d = (int(p) for p in text.strip().translate(str.maketrans("०१२३४५६७८९", "0123456789")).split("-"))
    except ValueError:
        raise ValueError(f"BS date must look like YYYY-MM-DD, got {text!r}") from None
    if not is_valid(y, m, d):
        raise ValueError(f"BS {y:04d}-{m:02d}-{d:02d} does not exist")
    return BS(y, m, d)


def parse_ad(text: str) -> BS:
    """Parse an explicitly Gregorian ISO date, including Devanagari digits."""
    normalized = text.strip().translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    try:
        value = date.fromisoformat(normalized)
    except ValueError:
        raise ValueError(f"AD date must look like YYYY-MM-DD, got {text!r}") from None
    return to_bs(value)


def parse_either(text: str, force_bs: bool = False) -> BS:
    """Compatibility helper: explicit BS when requested, otherwise Gregorian."""
    return parse(text) if force_bs else parse_ad(text)
