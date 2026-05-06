"""Source-labeled historical BS month-length corpus."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_LENGTHS, BS_MONTH_NAMES
from app.calendar.provenance import get_bs_year_provenance

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CORPUS_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "verified_month_lengths.csv"
CORPUS_ID = "verified_month_lengths_2000_2099_v1"
CORPUS_VERSION = "verified_corpus_2000_2099_v1"
MONTH_COLUMNS = [name.lower() for name in BS_MONTH_NAMES]


@dataclass(frozen=True)
class CorpusRow:
    bs_year: int
    months: list[int]
    source_type: str
    source_reference: str
    verification_status: str

    @property
    def source_quality(self) -> float:
        if self.source_type == "official_verified" and self.verification_status == "verified":
            return 1.0
        if self.source_type == "approved_patro":
            return 0.82
        if self.source_type == "physical_patro_verified":
            return 0.9
        if self.source_type == "internal_reference":
            return 0.72
        if self.source_type == "third_party_reference":
            return 0.55
        return 0.35

    def payload(self) -> dict[str, Any]:
        return {
            "bs_year": self.bs_year,
            "months": self.months,
            "source_type": self.source_type,
            "source_reference": self.source_reference,
            "verification_status": self.verification_status,
            "source_quality": self.source_quality,
        }


def _fallback_row(bs_year: int) -> CorpusRow:
    provenance = get_bs_year_provenance(bs_year)
    if provenance.confidence == "official":
        source_type = "official_verified"
        source_reference = "structured_official_repo_artifact"
        verification_status = "verified"
    elif provenance.source_status.startswith("archived_official"):
        source_type = "approved_patro"
        source_reference = "archived_official_pdf_repo_artifact"
        verification_status = "archived_unstructured_needs_review"
    else:
        source_type = "third_party_reference"
        source_reference = "legacy_static_lookup_table"
        verification_status = "needs_review"
    return CorpusRow(
        bs_year=bs_year,
        months=list(BS_MONTH_LENGTHS[bs_year]),
        source_type=source_type,
        source_reference=source_reference,
        verification_status=verification_status,
    )


@lru_cache(maxsize=1)
def load_corpus() -> dict[int, CorpusRow]:
    if not CORPUS_PATH.exists():
        return {year: _fallback_row(year) for year in sorted(BS_MONTH_LENGTHS)}

    rows: dict[int, CorpusRow] = {}
    with CORPUS_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            bs_year = int(raw["bs_year"])
            months = [int(raw[column]) for column in MONTH_COLUMNS]
            if len(months) != 12 or any(days < 29 or days > 32 for days in months):
                raise ValueError(f"Invalid month lengths in corpus row {bs_year}.")
            rows[bs_year] = CorpusRow(
                bs_year=bs_year,
                months=months,
                source_type=raw["source_type"],
                source_reference=raw["source_reference"],
                verification_status=raw["verification_status"],
            )
    return rows


def corpus_rows() -> list[CorpusRow]:
    return [load_corpus()[year] for year in sorted(load_corpus())]


def is_known_year(bs_year: int) -> bool:
    return bs_year in load_corpus()


def get_corpus_row(bs_year: int) -> CorpusRow:
    try:
        return load_corpus()[bs_year]
    except KeyError as exc:
        raise ValueError(f"BS year {bs_year} is outside corpus range {corpus_range_label()}.") from exc


def known_months(bs_year: int) -> list[int]:
    return list(get_corpus_row(bs_year).months)


def corpus_range_label() -> str:
    years = sorted(load_corpus())
    if not years:
        return f"{BS_MIN_YEAR}-{BS_MAX_YEAR} BS"
    return f"{years[0]}-{years[-1]} BS"


def source_label_for_year(bs_year: int) -> str:
    if is_known_year(bs_year):
        return get_corpus_row(bs_year).source_type
    return "computed_prediction"


def corpus_summary() -> dict[str, Any]:
    rows = corpus_rows()
    counts: dict[str, int] = {}
    verification_counts: dict[str, int] = {}
    for row in rows:
        counts[row.source_type] = counts.get(row.source_type, 0) + 1
        verification_counts[row.verification_status] = verification_counts.get(row.verification_status, 0) + 1
    return {
        "corpus_id": CORPUS_ID,
        "corpus_version": CORPUS_VERSION,
        "range": corpus_range_label(),
        "years": len(rows),
        "source_type_counts": counts,
        "verification_status_counts": verification_counts,
        "official_claim_boundary": (
            "Only rows labeled official_verified/verified should be treated as official-source "
            "calibration evidence."
        ),
    }
