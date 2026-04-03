"""Validation helpers for ground-truth source payloads."""

from __future__ import annotations

from typing import Any


def validate_ground_truth_payload(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("records", []) if isinstance(payload, dict) else []
    meta = payload.get("_meta", {}) if isinstance(payload, dict) else {}
    supported_years = {
        int(year)
        for year in meta.get("bs_years", [])
        if isinstance(year, int) or (isinstance(year, str) and year.strip().isdigit())
    }
    duplicate_keys: set[tuple[Any, ...]] = set()
    seen_keys: set[tuple[Any, ...]] = set()
    duplicate_examples: list[dict[str, Any]] = []
    declared_conflict_records: list[dict[str, Any]] = []
    undeclared_mismatch_records: list[dict[str, Any]] = []
    unsupported_year_records: list[dict[str, Any]] = []
    missing_source_lineage_records: list[dict[str, Any]] = []
    missing_core_fields = 0

    for row in records:
        if not isinstance(row, dict):
            missing_core_fields += 1
            continue

        festival_id = row.get("festival_id")
        bs_year = row.get("bs_year")
        bs_month = row.get("bs_month")
        bs_day = row.get("bs_day")
        gregorian_date = row.get("gregorian_date")
        key = (festival_id, bs_year, bs_month, bs_day, gregorian_date)

        if not festival_id or bs_year is None or gregorian_date is None:
            missing_core_fields += 1
            continue

        if key in seen_keys:
            duplicate_keys.add(key)
            if len(duplicate_examples) < 10:
                duplicate_examples.append(
                    {
                        "festival_id": festival_id,
                        "bs_year": bs_year,
                        "bs_month": bs_month,
                        "bs_day": bs_day,
                        "gregorian_date": gregorian_date,
                    }
                )
        else:
            seen_keys.add(key)

        if supported_years and bs_year not in supported_years:
            unsupported_year_records.append(
                {
                    "festival_id": festival_id,
                    "bs_year": bs_year,
                    "gregorian_date": gregorian_date,
                }
            )

        override_date = row.get("override_date")
        override_source = override_date.get("source") if isinstance(override_date, dict) else None
        if not row.get("source_file") and not row.get("source_citation") and not override_source:
            missing_source_lineage_records.append(
                {
                    "festival_id": festival_id,
                    "bs_year": bs_year,
                    "gregorian_date": gregorian_date,
                }
            )

        override_start = override_date.get("start") if isinstance(override_date, dict) else None
        if override_start and override_start != gregorian_date:
            mismatch = {
                "festival_id": festival_id,
                "bs_year": bs_year,
                "bs_month": bs_month,
                "bs_day": bs_day,
                "gregorian_date": gregorian_date,
                "override_start": override_start,
            }
            if row.get("override_match") is False:
                declared_conflict_records.append(mismatch)
            else:
                undeclared_mismatch_records.append(mismatch)

    status = "ok"
    has_errors = bool(
        missing_core_fields
        or duplicate_keys
        or unsupported_year_records
        or missing_source_lineage_records
        or undeclared_mismatch_records
    )
    if has_errors:
        status = "error"

    return {
        "status": status,
        "gate_passed": not has_errors,
        "total_records": len(records),
        "duplicate_record_count": len(duplicate_keys),
        "duplicate_examples": duplicate_examples[:10],
        "missing_core_fields": missing_core_fields,
        "supported_years": sorted(supported_years),
        "unsupported_year_count": len(unsupported_year_records),
        "unsupported_year_examples": unsupported_year_records[:10],
        "missing_source_lineage_count": len(missing_source_lineage_records),
        "missing_source_lineage_examples": missing_source_lineage_records[:10],
        "declared_conflict_count": len(declared_conflict_records),
        "declared_conflict_examples": declared_conflict_records[:10],
        "authority_mismatch_count": len(undeclared_mismatch_records),
        "authority_mismatch_examples": undeclared_mismatch_records[:10],
    }
