#!/usr/bin/env python3
"""Run future BS model backtests from the command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.backtest import (  # noqa: E402
    backtest_model,
    full_replay_backtest,
    rolling_validation,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["holdout", "full", "rolling"], default="holdout")
    parser.add_argument("--train-start", type=int, default=2040)
    parser.add_argument("--train-end", type=int, default=2075)
    parser.add_argument("--test-start", type=int, default=2076)
    parser.add_argument("--test-end", type=int, default=2083)
    args = parser.parse_args()
    if args.mode == "full":
        payload = full_replay_backtest(args.test_start, args.test_end)
    elif args.mode == "rolling":
        payload = rolling_validation(args.train_start, args.test_start, args.test_end)
    else:
        payload = backtest_model(args.train_start, args.train_end, args.test_start, args.test_end)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
