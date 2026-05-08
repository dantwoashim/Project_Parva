"""Strict source-policy separation for future-BS accuracy claims."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = PROJECT_ROOT / "data" / "future_bs" / "corpus"

PUBLICATION_STATUS = "computed_prediction_not_official"

POLICIES: dict[str, dict[str, Any]] = {
    "official_strict": {
        "allowed_best_tiers": {1},
        "allowed_source_types": {"official_verified"},
        "claim_scope": "official-grade claim-readiness only",
        "tier_5_6_allowed": False,
    },
    "medium_high_training": {
        "allowed_best_tiers": {1, 2, 3, 4},
        "allowed_source_types": {"official_verified", "printed_verified", "public_daily_witness", "publisher_reference"},
        "claim_scope": "training/calibration and non-official benchmarking",
        "tier_5_6_allowed": False,
    },
    "all_witness_experimental": {
        "allowed_best_tiers": {1, 2, 3, 4, 5, 6},
        "allowed_source_types": {
            "official_verified",
            "printed_verified",
            "public_daily_witness",
            "publisher_reference",
            "software_table_reference",
            "third_party_reference",
        },
        "claim_scope": "experimental weak-signal analysis only",
        "tier_5_6_allowed": True,
    },
}

INVALID_RECONSTRUCTED_ROWS = {
    (2091, 8),
    (2091, 12),
    (2092, 9),
    (2095, 8),
    (2095, 12),
}


def read_reconstructed_lengths(path: Path | None = None) -> list[dict[str, str]]:
    source = path or CORPUS_DIR / "reconstructed_month_lengths.csv"
    if not source.exists():
        return []
    with source.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def row_is_invalid(row: dict[str, Any]) -> bool:
    try:
        key = (int(row["bs_year"]), int(row["bs_month"]))
        length = int(row["month_length"])
    except (KeyError, ValueError):
        return True
    return key in INVALID_RECONSTRUCTED_ROWS or length not in {29, 30, 31, 32}


def row_allowed(row: dict[str, Any], policy: str) -> bool:
    cfg = POLICIES[policy]
    if row_is_invalid(row):
        return False
    best_tier = int(row.get("best_source_tier") or 99)
    if best_tier not in cfg["allowed_best_tiers"]:
        return False
    if policy == "official_strict":
        return row.get("usable_for_official_claim") == "true"
    return row.get("usable_for_training") == "true"


def policy_rows(policy: str, rows: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    if policy not in POLICIES:
        raise ValueError(f"Unknown source policy: {policy}")
    source_rows = rows if rows is not None else read_reconstructed_lengths()
    return [row for row in source_rows if row_allowed(row, policy)]


def policy_metrics(policy: str, rows: list[dict[str, str]] | None = None) -> dict[str, Any]:
    source_rows = rows if rows is not None else read_reconstructed_lengths()
    allowed = policy_rows(policy, source_rows)
    years = sorted({int(row["bs_year"]) for row in allowed})
    invalid = [row for row in source_rows if row_is_invalid(row)]
    best_tiers = Counter(str(row.get("best_source_tier", "")) for row in allowed)
    return {
        "publication_status": PUBLICATION_STATUS,
        "policy": policy,
        "claim_scope": POLICIES[policy]["claim_scope"],
        "month_cases": len(allowed),
        "years_with_any_case": len(years),
        "years": years,
        "best_tier_distribution": dict(best_tiers),
        "invalid_rows_excluded": len(invalid),
        "tier_5_6_allowed": POLICIES[policy]["tier_5_6_allowed"],
        "official_claim_ready_cases": len(allowed) if policy == "official_strict" else 0,
        "required_official_cases": 528,
        "claim_ready_with_sufficient_corpus": bool(policy == "official_strict" and len(allowed) >= 528),
    }


def explain_official_witness_mismatch(witness_rows: int, official_claim_rows: int) -> str:
    excluded = max(0, int(witness_rows) - int(official_claim_rows))
    return (
        f"{excluded} official-labeled witness rows are not official-claim usable because "
        "source policy excludes conflicts, unverified status, or invalid reconstructed month rows."
    )


__all__ = [
    "INVALID_RECONSTRUCTED_ROWS",
    "POLICIES",
    "policy_metrics",
    "policy_rows",
    "read_reconstructed_lengths",
    "row_allowed",
    "row_is_invalid",
    "explain_official_witness_mismatch",
]
