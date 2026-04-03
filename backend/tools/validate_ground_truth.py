#!/usr/bin/env python3
"""Validate merged ground-truth datasets and fail on integrity regressions."""

from __future__ import annotations

import argparse
import json

from app.sources.loader import JsonSourceLoader


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate merged ground-truth payloads")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the validation summary as JSON.",
    )
    args = parser.parse_args()

    loader = JsonSourceLoader()
    payload = loader.load_ground_truth()
    summary = payload.get("_meta", {}).get("validation", {})

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("Ground truth validation")
        print(f"  Status: {summary.get('status')}")
        print(f"  Gate passed: {summary.get('gate_passed')}")
        print(f"  Total records: {summary.get('total_records')}")
        print(f"  Duplicates: {summary.get('duplicate_record_count')}")
        print(f"  Missing core fields: {summary.get('missing_core_fields')}")
        print(f"  Unsupported years: {summary.get('unsupported_year_count')}")
        print(f"  Missing source lineage: {summary.get('missing_source_lineage_count')}")
        print(f"  Declared conflicts: {summary.get('declared_conflict_count')}")
        print(f"  Undeclared authority mismatches: {summary.get('authority_mismatch_count')}")

    return 0 if summary.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
