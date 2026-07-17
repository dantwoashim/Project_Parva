"""Pure helpers for reconciling rendered BS calendar evidence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class RenderedMonthEvidence:
    bs_year: int
    bs_month: int
    days: int
    start_ad: str
    end_ad: str
    source_url: str


def extract_rendered_month_evidence(
    html: str,
    *,
    bs_year: int,
    bs_month: int,
    source_url: str,
) -> RenderedMonthEvidence:
    pattern = re.compile(
        r'<li\s+onclick="openPopUp\(\'(?P<ad>\d{4}-\d{1,2}-\d{1,2})\'\)"'
        r'[\s\S]*?<span id="(?P<year>\d{4})-(?P<month>\d{1,2})-'
        r'(?P<day>\d{1,2})-usn"'
    )
    entries: dict[int, date] = {}
    for match in pattern.finditer(html):
        year = int(match.group("year"))
        month = int(match.group("month"))
        if (year, month) != (bs_year, bs_month):
            continue
        day = int(match.group("day"))
        ad = _parse_date_token(match.group("ad"))
        previous = entries.get(day)
        if previous is not None and previous != ad:
            raise RuntimeError(
                f"Conflicting rendered dates for BS {bs_year}-{bs_month:02d}-{day:02d}."
            )
        entries[day] = ad

    if not entries:
        raise RuntimeError(f"No rendered calendar rows found for BS {bs_year}-{bs_month:02d}.")
    expected_days = list(range(1, max(entries) + 1))
    if sorted(entries) != expected_days:
        raise RuntimeError(
            f"Rendered calendar rows are not contiguous for BS {bs_year}-{bs_month:02d}."
        )
    for day in expected_days[1:]:
        if entries[day] != entries[day - 1] + timedelta(days=1):
            raise RuntimeError(
                f"Rendered AD dates are not contiguous for BS {bs_year}-{bs_month:02d}."
            )
    return RenderedMonthEvidence(
        bs_year=bs_year,
        bs_month=bs_month,
        days=len(entries),
        start_ad=entries[1].isoformat(),
        end_ad=entries[len(entries)].isoformat(),
        source_url=source_url,
    )


def reconcile_rendered_evidence(
    embedded: dict[int, list[int]],
    rendered: list[RenderedMonthEvidence],
) -> tuple[dict[int, list[int]], list[dict[str, object]]]:
    reconciled = {year: list(months) for year, months in embedded.items()}
    drift: list[dict[str, object]] = []
    for item in rendered:
        if item.bs_year not in reconciled:
            raise RuntimeError(
                f"Rendered BS year {item.bs_year} is absent from the embedded month table."
            )
        embedded_days = reconciled[item.bs_year][item.bs_month - 1]
        if embedded_days != item.days:
            drift.append(
                {
                    "bs_year": item.bs_year,
                    "bs_month": item.bs_month,
                    "embedded_days": embedded_days,
                    "rendered_days": item.days,
                    "source_url": item.source_url,
                }
            )
        reconciled[item.bs_year][item.bs_month - 1] = item.days
    return reconciled, drift


def _parse_date_token(value: str) -> date:
    year, month, day = (int(part) for part in value.split("-"))
    return date(year, month, day)
