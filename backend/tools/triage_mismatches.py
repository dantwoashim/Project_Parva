#!/usr/bin/env python3
"""Generate discrepancy register from evaluation_v4 output."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVAL_PATH = PROJECT_ROOT / "reports" / "evaluation_v4" / "evaluation_v4.json"
OUT_JSON = PROJECT_ROOT / "data" / "ground_truth" / "discrepancies.json"
OUT_MD = PROJECT_ROOT / "docs" / "DISCREPANCY_TRIAGE.md"


def classify_resolution(cause: str) -> str:
    mapping = {
        "boundary_shift": "rule_adjustment_candidate",
        "rule_or_source_mismatch": "investigate_rule_or_source",
        "calculation_error": "engine_bug",
        "missing_result": "missing_rule_or_data",
    }
    return mapping.get(cause, "n/a")


def main() -> None:
    if not EVAL_PATH.exists():
        raise SystemExit(f"Missing evaluation file: {EVAL_PATH}")

    payload = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    failures = [r for r in rows if not r.get("passed")]

    triaged = []
    for row in failures:
        cause = row.get("probable_cause", "unknown")
        triaged.append(
            {
                "festival_id": row.get("festival_id"),
                "year": row.get("year"),
                "expected": row.get("expected_date"),
                "calculated": row.get("calculated_date"),
                "variance_days": row.get("variance_days"),
                "rule_type": row.get("rule_type"),
                "source": row.get("source"),
                "probable_cause": cause,
                "resolution_track": classify_resolution(cause),
                "status": "open",
            }
        )

    summary = {
        "generated_from": str(EVAL_PATH),
        "total_rows": len(rows),
        "failure_count": len(triaged),
        "by_cause": dict(Counter(item["probable_cause"] for item in triaged)),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"summary": summary, "discrepancies": triaged}, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Discrepancy Triage",
        "",
        f"- Evaluated rows: **{summary['total_rows']}**",
        f"- Open discrepancies: **{summary['failure_count']}**",
        "",
        "## Cause Breakdown",
        "",
        "| Cause | Count |",
        "|---|---:|",
    ]

    if summary["by_cause"]:
        for cause, count in summary["by_cause"].items():
            lines.append(f"| {cause} | {count} |")
    else:
        lines.append("| (none) | 0 |")

    if triaged:
        lines += [
            "",
            "## Open Items",
            "",
            "| Festival | Year | Expected | Calculated | Cause | Resolution Track |",
            "|---|---:|---|---|---|---|",
        ]
        for row in triaged:
            lines.append(
                f"| {row['festival_id']} | {row['year']} | {row['expected']} | {row['calculated'] or 'N/A'} | {row['probable_cause']} | {row['resolution_track']} |"
            )

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
