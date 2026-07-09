#!/usr/bin/env python3
"""Generate a residual analysis markdown report for future-BS validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.backtest import backtest_model  # noqa: E402
from app.research.future_bs.claim_readiness import claim_readiness_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/future_bs/reports/residual_report_v7.md"))
    args = parser.parse_args()
    backtest = backtest_model(2000, 2077, 2078, 2083, source_policy="official_only")
    readiness = claim_readiness_report()
    mismatches = backtest.get("mismatch_details", [])
    lines = [
        "# Future BS Residual Report v7",
        "",
        "Publication status: `computed_prediction_not_official`.",
        "",
        "## Summary",
        "",
        f"- Month cases: {backtest.get('months_tested')}",
        f"- Overall top1 accuracy: {backtest.get('overall_top1_accuracy')}",
        f"- Green-zone accuracy: {backtest.get('green_zone_accuracy')}",
        f"- Green-zone coverage: {backtest.get('green_zone_coverage')}",
        f"- False-green rate: {readiness.get('false_green_rate')}",
        f"- Claim ready: {readiness.get('claim_ready_99_green_zone')}",
        "",
        "## Mismatches",
        "",
    ]
    if not mismatches:
        lines.append("No mismatches in this official-only holdout window.")
    else:
        for mismatch in mismatches:
            lines.append(
                f"- {json.dumps(mismatch, ensure_ascii=False)} | classification: confidence_calibration_or_method_regime_issue"
            )
    lines.extend(
        [
            "",
            "## Active Learning Blockers",
            "",
        ]
    )
    for blocker in readiness.get("claim_blockers", []):
        lines.append(f"- {blocker}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "mismatches": len(mismatches)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
