#!/usr/bin/env python3
"""Fail build when differential drift exceeds configured threshold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Differential drift gate checker")
    parser.add_argument("--report", default="reports/differential_report.json")
    parser.add_argument("--max-drift", type=float, default=2.0)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Missing differential report: {report_path}")
        return 2

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    result = payload.get("result", {})
    taxonomy = result.get("taxonomy", {})
    drift = float(result.get("drift_percent", 0.0))
    major = int(taxonomy.get("major_difference", 0))

    failed = drift > args.max_drift or (args.strict and major > 0)
    print(f"drift={drift}% major={major} max_drift={args.max_drift} strict={args.strict}")
    print("gate=FAIL" if failed else "gate=PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
