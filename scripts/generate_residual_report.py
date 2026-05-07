#!/usr/bin/env python3
"""Generate a markdown residual-analysis report for future-BS backtests."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.residual_analysis import residual_summary  # noqa: E402


def _table(rows: list[dict]) -> str:
    if not rows:
        return "No mismatches.\n"
    lines = [
        "| BS year | Month | Official | Predicted | Boundary | Rule | Alternative |",
        "|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {bs_year} | {month} | {actual_days} | {predicted_days} | {boundary_risk} | "
            "{selected_rule} | {alternative_rule_that_would_have_worked} |".format(**row)
        )
    return "\n".join(lines) + "\n"


def render_report(payload: dict) -> str:
    metrics = payload.get("accuracy_metrics", {})
    return f"""# Future BS Residual Analysis

Generated: {datetime.now(timezone.utc).isoformat()}

## Scope

- Train range: {payload["train_range"]}
- Test range: {payload["test_range"]}
- Source policy: {payload.get("source_policy", "all_reference")}
- Method version: {payload["method_version"]}

## Month-Level Metrics

- Overall top-1 accuracy: {metrics.get("overall_top1_accuracy", 0)}%
- Green-zone accuracy: {metrics.get("green_zone_accuracy", 0)}%
- Green-zone coverage: {metrics.get("green_zone_coverage", 0)}%
- Boundary cases flagged: {metrics.get("boundary_case_accuracy", 0)}%
- Ready for 99% claim: {metrics.get("claim_readiness", {}).get("ready_for_99_percent_green_zone_claim", False)}

## Residual Clusters

- Mismatches by BS month: `{json.dumps(payload.get("mismatches_by_month", {}), sort_keys=True)}`
- Mismatches by ingress hour: `{json.dumps(payload.get("mismatch_by_ingress_hour", {}), sort_keys=True)}`
- Mismatches by boundary distance: `{json.dumps(payload.get("mismatch_by_boundary_distance", {}), sort_keys=True)}`
- Mismatches by source type: `{json.dumps(payload.get("mismatches_by_source_type", {}), sort_keys=True)}`
- Alternative rules that would have worked: `{json.dumps(payload.get("alternative_rules_that_would_have_worked", {}), sort_keys=True)}`

## Mismatch Table

{_table(payload.get("mismatch_details", []))}

## Claim Boundary

This report is a technical evaluation artifact. It is not an official future Nepali calendar publication and must not be used to market a 99%+ claim unless the readiness flag is true on a source-strict official/printed benchmark.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-start", type=int, default=2040)
    parser.add_argument("--train-end", type=int, default=2075)
    parser.add_argument("--test-start", type=int, default=2076)
    parser.add_argument("--test-end", type=int, default=2083)
    parser.add_argument(
        "--source-policy",
        choices=["all_reference", "official_only", "official_plus_printed", "train_allowed"],
        default="all_reference",
    )
    parser.add_argument("--output", type=Path, default=Path("data/future_bs/reports/residual_report.md"))
    args = parser.parse_args()
    payload = residual_summary(
        args.train_start,
        args.train_end,
        args.test_start,
        args.test_end,
        source_policy=args.source_policy,
    )
    report = render_report(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
