"""Bounded CSV date review with evidence attached to each result."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from typing import TypedDict

from . import bs, holidays

MAX_CSV_BYTES = 1_048_576
MAX_ROWS = 10_000


class ReviewRow(TypedDict):
    input: str
    ad: str | None
    bs: str | None
    source: str | None
    calendar_sources: list[str]
    coverage: str
    status: str
    flags: list[str]
    error: str | None


def read_dates(text: str, column: str | None = None) -> list[str]:
    if len(text.encode("utf-8")) > MAX_CSV_BYTES:
        raise ValueError("CSV exceeds the 1 MiB limit.")
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
    try:
        names = reader.fieldnames
        if not names or len(set(names)) != len(names) or any(not name for name in names):
            raise ValueError("CSV needs a header with unique, non-empty column names.")
        candidates = [name for name in names if "date" in name.casefold()]
        if column is None:
            if len(candidates) != 1:
                raise ValueError("Specify a date column; automatic selection requires exactly one date column.")
            column = candidates[0]
        if column not in names:
            raise ValueError(f"CSV column {column!r} does not exist.")
        values: list[str] = []
        for row in reader:
            if len(values) >= MAX_ROWS:
                raise ValueError(f"CSV exceeds the {MAX_ROWS:,}-row limit.")
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV record ending at line {reader.line_num} does not match its header.")
            values.append(row[column].strip())
        return values
    except csv.Error as exc:
        raise ValueError(f"Invalid CSV: {exc}") from exc


def review(dates: Iterable[str], force_bs: bool = False, *, scope: str = "national") -> list[ReviewRow]:
    holidays.validate_scope(scope)
    output: list[ReviewRow] = []
    for raw in dates:
        if len(output) >= MAX_ROWS:
            raise ValueError(f"Review exceeds the {MAX_ROWS:,}-row limit.")
        try:
            value = bs.parse(raw) if force_bs else bs.parse_ad(raw)
            result = holidays.evaluate(value.ad, scope=scope)
        except ValueError as exc:
            output.append(
                ReviewRow(
                    input=raw,
                    ad=None,
                    bs=None,
                    source=None,
                    calendar_sources=[],
                    coverage="missing",
                    status="invalid",
                    flags=[],
                    error=str(exc),
                )
            )
            continue
        flags = [row["id"] for row in result.holidays]
        if result.weekend:
            flags.append("saturday")
        if result.working is None:
            flags.append(result.reason)
        output.append(
            ReviewRow(
                input=raw,
                ad=value.ad.isoformat(),
                bs=str(value),
                source=result.source,
                calendar_sources=list(value.sources),
                coverage=result.coverage,
                status=result.status,
                flags=flags,
                error=None,
            )
        )
    return output
