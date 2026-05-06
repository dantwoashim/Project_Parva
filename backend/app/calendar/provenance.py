"""Source provenance boundaries for Bikram Sambat conversion data."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import BS_MAX_YEAR, BS_MIN_YEAR

STATIC_LOOKUP_RANGE = (BS_MIN_YEAR, BS_MAX_YEAR)
STRUCTURED_OFFICIAL_YEARS = frozenset(range(2078, 2084))
ARCHIVED_RAW_OFFICIAL_YEARS = frozenset({2076, 2077})
NPNS_PANCHANGA_SOURCE_YEARS = frozenset({2082, 2083})

STATIC_LOOKUP_RANGE_LABEL = f"{BS_MIN_YEAR}-{BS_MAX_YEAR} BS"
STRUCTURED_OFFICIAL_RANGE_LABEL = "2078-2083 BS"
ARCHIVED_RAW_OFFICIAL_RANGE_LABEL = "2076-2077 BS"


@dataclass(frozen=True)
class BSYearProvenance:
    bs_year: int
    confidence: str
    source_status: str
    source_range: str | None
    official_structured_range: str
    static_lookup_range: str
    note: str


def is_static_lookup_year(bs_year: int) -> bool:
    return BS_MIN_YEAR <= bs_year <= BS_MAX_YEAR


def is_structured_official_year(bs_year: int) -> bool:
    return bs_year in STRUCTURED_OFFICIAL_YEARS


def get_bs_year_provenance(bs_year: int) -> BSYearProvenance:
    if bs_year in STRUCTURED_OFFICIAL_YEARS:
        return BSYearProvenance(
            bs_year=bs_year,
            confidence="official",
            source_status="structured_official",
            source_range=STRUCTURED_OFFICIAL_RANGE_LABEL,
            official_structured_range=STRUCTURED_OFFICIAL_RANGE_LABEL,
            static_lookup_range=STATIC_LOOKUP_RANGE_LABEL,
            note="Year has structured official source artifacts in the repository.",
        )
    if bs_year in ARCHIVED_RAW_OFFICIAL_YEARS:
        return BSYearProvenance(
            bs_year=bs_year,
            confidence="static_lookup",
            source_status="archived_official_pdf_unstructured",
            source_range=STATIC_LOOKUP_RANGE_LABEL,
            official_structured_range=STRUCTURED_OFFICIAL_RANGE_LABEL,
            static_lookup_range=STATIC_LOOKUP_RANGE_LABEL,
            note=(
                "Official PDF is archived, but no accepted structured extraction "
                "backs this year yet."
            ),
        )
    if is_static_lookup_year(bs_year):
        return BSYearProvenance(
            bs_year=bs_year,
            confidence="static_lookup",
            source_status="static_table_unverified",
            source_range=STATIC_LOOKUP_RANGE_LABEL,
            official_structured_range=STRUCTURED_OFFICIAL_RANGE_LABEL,
            static_lookup_range=STATIC_LOOKUP_RANGE_LABEL,
            note="Year is served from the static lookup table without official structured provenance.",
        )
    return BSYearProvenance(
        bs_year=bs_year,
        confidence="estimated",
        source_status="estimated_outside_static_lookup",
        source_range=None,
        official_structured_range=STRUCTURED_OFFICIAL_RANGE_LABEL,
        static_lookup_range=STATIC_LOOKUP_RANGE_LABEL,
        note="Year is outside the static lookup table and uses the estimated conversion path.",
    )


def get_bs_year_confidence_from_provenance(bs_year: int) -> str:
    return get_bs_year_provenance(bs_year).confidence
