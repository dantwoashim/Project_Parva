"""Known BS month-length corpus helpers."""

from __future__ import annotations

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_LENGTHS
from app.calendar.provenance import get_bs_year_provenance


def is_known_year(bs_year: int) -> bool:
    return bs_year in BS_MONTH_LENGTHS


def known_months(bs_year: int) -> list[int]:
    return list(BS_MONTH_LENGTHS[bs_year])


def corpus_range_label() -> str:
    return f"{BS_MIN_YEAR}-{BS_MAX_YEAR} BS"


def source_label_for_year(bs_year: int) -> str:
    provenance = get_bs_year_provenance(bs_year)
    if provenance.confidence == "official":
        return "official_verified"
    if provenance.source_status.startswith("archived_official"):
        return "approved_calendar"
    return "third_party_reference"
