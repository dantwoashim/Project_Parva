#!/usr/bin/env python3
"""Generate a public source/method coverage matrix for proof-supported surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.membranes.source_resolution import (
    resolve_ad_to_bs_source,
    resolve_bs_months_source,
    resolve_convert_bs_to_ad_source,
    resolve_fiscal_year_source,
    resolve_holiday_source,
    resolve_validate_bs_date_source,
    resolve_working_day_source,
)
from app.sources.hashing import canonical_json_hash

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = PROJECT_ROOT / "reports" / "source_coverage" / "coverage_matrix.json"
OUT_MD = PROJECT_ROOT / "reports" / "source_coverage" / "coverage_matrix.md"


def _row(operation: str, year: int, field: str, resolution: Any, *, method: str | None = None) -> dict[str, Any]:
    data = resolution.as_dict()
    return {
        "operation": operation,
        "year": year,
        "field": field,
        "authority": data["authority"],
        "coverage_status": data["coverage_status"],
        "source_docket_ids": data["source_docket_ids"],
        "method_docket_ids": [method] if method else [],
        "review_required": data["review_required"],
        "claim_boundary": data["claim_boundary"],
        "eligible_official": data["eligible_official"],
        "not_authority": True,
    }


def build_matrix() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for year in (2070, 2082, 2083, 2099):
        rows.extend(
            [
                _row("convert_bs_to_ad", year, "ad_date", resolve_convert_bs_to_ad_source(year, 1, 1)),
                _row("ad_to_bs", year, "bs_date", resolve_ad_to_bs_source(year, 1, 1)),
                _row("validate_bs_date", year, "validity", resolve_validate_bs_date_source(year, 1, 1)),
                _row("holiday", year, "membership", resolve_holiday_source(year, 1, 1)),
                _row("working_day", year, "working_day", resolve_working_day_source(year, 1, 2)),
                _row("fiscal_year", year, "fiscal_year", resolve_fiscal_year_source(year)),
                _row(
                    "bs_months",
                    year,
                    "month_lengths",
                    resolve_bs_months_source(year, "canonical"),
                    method="bs_month_canonical_policy_v0",
                ),
            ]
        )
    rows.append(
        {
            "operation": "panchanga_summary",
            "year": 2082,
            "field": "tithi/nakshatra/yoga/karana/sunrise",
            "authority": "computed_uncertified",
            "coverage_status": "method_backed_with_pinned_fixture",
            "source_docket_ids": [],
            "method_docket_ids": [
                "parva:method:sunrise:v1",
                "parva:method:tithi:v1",
                "parva:method:nakshatra:v1",
                "parva:method:yoga:v1",
                "parva:method:karana:v1",
            ],
            "review_required": True,
            "claim_boundary": "computed_ephemeris_not_panchanga_authority",
            "eligible_official": False,
            "not_authority": True,
            "ephemeris_fixture": "kathmandu_2025_04_14_lahiri",
        }
    )
    return {
        "schema": "parva-source-coverage-v1",
        "claim_boundary": "coverage_report_not_authority",
        "not_authority": True,
        "rows": rows,
        "matrix_hash": f"sha256:{canonical_json_hash(rows)}",
    }


def _write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Source and Method Coverage Matrix",
        "",
        "This report describes public proof coverage. It is not government, legal, tax, payroll, banking, or Panchanga authority.",
        "",
        f"- Matrix hash: `{payload['matrix_hash']}`",
        f"- Rows: {len(payload['rows'])}",
        "",
        "| Operation | Year | Field | Authority | Coverage | Review | Boundary |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['operation']} | {row['year']} | {row['field']} | {row['authority']} | "
            f"{row['coverage_status']} | {row['review_required']} | {row['claim_boundary']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if committed report differs.")
    args = parser.parse_args()
    payload = build_matrix()
    md = _write_markdown(payload)
    if args.check:
        if not OUT_JSON.exists() or not OUT_MD.exists():
            raise SystemExit("source coverage report missing; run without --check")
        current_json = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        current_md = OUT_MD.read_text(encoding="utf-8")
        if current_json != payload or current_md != md:
            raise SystemExit("source coverage report is stale; run scripts/release/generate_source_coverage_report.py")
        print("Source coverage report is current.")
        return 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(PROJECT_ROOT)} and {OUT_MD.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
