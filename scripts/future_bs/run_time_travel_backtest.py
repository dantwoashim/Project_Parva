#!/usr/bin/env python3
"""Run future-BS time-travel backtests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.backtest import rolling_validation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default="official_only")
    parser.add_argument("--train-start", type=int, default=2000)
    parser.add_argument("--start", type=int, default=2078)
    parser.add_argument("--end", type=int, default=2083)
    parser.add_argument("--out", type=Path, default=Path("data/future_bs/reports/time_travel_v7.json"))
    args = parser.parse_args()

    result = rolling_validation(
        args.train_start,
        args.start,
        args.end,
        source_policy=args.source_policy,
        model="solar_statistical_stack_holdout",
    )
    result["publication_status"] = "computed_prediction_not_official"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "months_tested": result["months_tested"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
