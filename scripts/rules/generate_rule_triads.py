#!/usr/bin/env python3
"""Generate rule/evidence/validation triad artifacts for v4 catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rules.triad_pipeline import generate_rule_triads, triad_integrity_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate v4 rule triads")
    parser.add_argument("--computed-only", action="store_true", help="Generate triads only for computed rules.")
    parser.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing triad files.")
    parser.add_argument(
        "--report-out",
        default=str(PROJECT_ROOT / "reports" / "rule_triad_report.json"),
        help="Output path for triad integrity report JSON.",
    )
    args = parser.parse_args()

    summary = generate_rule_triads(overwrite=not args.no_overwrite, computed_only=args.computed_only)
    integrity = triad_integrity_report()

    payload = {
        "summary": {
            "total_rules": summary.total_rules,
            "rule_files_written": summary.rule_files_written,
            "evidence_files_written": summary.evidence_files_written,
            "validation_files_written": summary.validation_files_written,
            "computed_with_cases": summary.computed_with_cases,
        },
        "integrity": integrity,
    }

    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
