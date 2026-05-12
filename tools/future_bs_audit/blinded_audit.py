#!/usr/bin/env python3
"""Aggregate-only blinded audit for external BS month assumptions."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.risk import FutureBSRiskInput, aggregate_blinded_audit  # noqa: E402

REQUIRED_COLUMNS = {"bs_year", "bs_month", "month_length"}


class BlindedAuditError(ValueError):
    """Raised when a blinded audit input cannot be safely processed."""


def _parse_int(raw: str, *, row_number: int, field: str) -> int:
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError) as exc:
        raise BlindedAuditError(f"row {row_number}: {field} must be an integer") from exc


def load_external_sheet(path: Path) -> list[FutureBSRiskInput]:
    """Load an external CSV into public-safe risk assumptions."""

    if not path.exists():
        raise BlindedAuditError(f"input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise BlindedAuditError(f"missing required columns: {', '.join(sorted(missing))}")

        assumptions: list[FutureBSRiskInput] = []
        seen_months: set[tuple[int, int]] = set()
        for row_number, row in enumerate(reader, start=2):
            bs_year = _parse_int(row.get("bs_year", ""), row_number=row_number, field="bs_year")
            bs_month = _parse_int(row.get("bs_month", ""), row_number=row_number, field="bs_month")
            month_length = _parse_int(
                row.get("month_length", ""),
                row_number=row_number,
                field="month_length",
            )
            key = (bs_year, bs_month)
            if key in seen_months:
                raise BlindedAuditError(
                    f"row {row_number}: duplicate bs_year and bs_month pair {bs_year}-{bs_month:02d}"
                )
            seen_months.add(key)
            assumptions.append(
                FutureBSRiskInput(
                    bs_year=bs_year,
                    bs_month=bs_month,
                    month_length=month_length,
                    source_policy="external_shadow_review",
                    synthetic_example=bs_year >= 9000,
                )
            )

    if not assumptions:
        raise BlindedAuditError("input file contains no data rows")
    return assumptions


def run_blinded_audit(path: Path) -> dict[str, object]:
    """Run the aggregate-only audit."""

    assumptions = load_external_sheet(path)
    report = aggregate_blinded_audit(assumptions)
    report["input_rows_loaded"] = len(assumptions)
    report["corrected_values_included"] = False
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a public-safe aggregate-only future-BS blinded audit."
    )
    parser.add_argument("csv_path", help="CSV with bs_year, bs_month, month_length columns")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args(argv)

    try:
        report = run_blinded_audit(Path(args.csv_path))
    except BlindedAuditError as exc:
        print(f"blinded audit failed: {exc}", file=sys.stderr)
        return 1

    body = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(body + "\n", encoding="utf-8")
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
