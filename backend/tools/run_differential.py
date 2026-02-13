#!/usr/bin/env python3
"""Run differential analysis between benchmark result reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.differential import compare_case_set

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT = PROJECT_ROOT / "benchmark" / "results" / "bs_conversion_v1_report.json"
DEFAULT_BASELINE = PROJECT_ROOT / "benchmark" / "results" / "baseline_2028Q1_bs_conversion.json"
OUT_JSON = PROJECT_ROOT / "reports" / "differential_report.json"
OUT_MD = PROJECT_ROOT / "reports" / "differential_report.md"
OUT_DATA = PROJECT_ROOT / "data" / "differential" / "disagreements.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Differential report generator")
    parser.add_argument("--current", default=str(DEFAULT_CURRENT))
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    parser.add_argument(
        "--max-drift",
        type=float,
        default=2.0,
        help="Maximum allowed major-difference drift percentage before failing.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any major differences exist, regardless of percentage.",
    )
    args = parser.parse_args()

    current = Path(args.current)
    baseline = Path(args.baseline)

    if not current.exists():
        raise SystemExit(f"Current report not found: {current}")
    if not baseline.exists():
        # bootstrap baseline from current if baseline missing
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_text(current.read_text(encoding="utf-8"), encoding="utf-8")

    diff = compare_case_set(current, baseline)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current": str(current),
        "baseline": str(baseline),
        "result": diff,
        "gate": {
            "max_drift": args.max_drift,
            "strict": args.strict,
            "passed": True,
        },
    }

    md = [
        "# Differential Test Report",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Current: `{payload['current']}`",
        f"- Baseline: `{payload['baseline']}`",
        "",
        "## Summary",
        "",
        f"- Total compared: **{diff['total_compared']}**",
        f"- Drift: **{diff['drift_percent']}%**",
        "",
        "## Taxonomy",
        "",
        "| Class | Count |",
        "|---|---:|",
    ]
    for k, v in diff["taxonomy"].items():
        md.append(f"| {k} | {v} |")

    major_count = diff["taxonomy"]["major_difference"]
    drift_percent = diff["drift_percent"]
    gate_failed = drift_percent > args.max_drift or (args.strict and major_count > 0)
    payload["gate"]["passed"] = not gate_failed
    payload["gate"]["major_count"] = major_count
    payload["gate"]["drift_percent"] = drift_percent

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md.extend(
        [
            "",
            "## Gate",
            "",
            f"- Max drift allowed: **{args.max_drift}%**",
            f"- Strict mode: **{args.strict}**",
            f"- Result: **{'PASS' if not gate_failed else 'FAIL'}**",
        ]
    )

    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({"drift_percent": diff["drift_percent"], "total_compared": diff["total_compared"]}, indent=2))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    if gate_failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
