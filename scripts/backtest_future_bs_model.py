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
    parser.add_argument(
        "--validation-mode",
        choices=[
            "last_5_year_holdout",
            "last_10_year_holdout",
            "rolling_forward_backtest",
            "source_strict_official_only",
            "leave_one_year_out",
        ],
        default=None,
    )
    parser.add_argument(
        "--source-policy",
        choices=["all_reference", "official_only", "official_plus_printed", "train_allowed"],
        default="all_reference",
    )
    parser.add_argument("--corpus", type=Path, default=PROJECT_ROOT / "data/future_bs/corpus/verified_month_lengths.csv")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--train-start", type=int, default=2040)
    parser.add_argument("--train-end", type=int, default=2075)
    parser.add_argument("--test-start", type=int, default=2076)
    parser.add_argument("--test-end", type=int, default=2083)
    args = parser.parse_args()

    source_policy = args.source_policy
    if args.validation_mode == "source_strict_official_only":
        source_policy = "official_only"
    if args.validation_mode == "last_5_year_holdout":
        args.train_end = args.test_end - 5
        args.test_start = args.train_end + 1
    elif args.validation_mode == "last_10_year_holdout":
        args.train_end = args.test_end - 10
        args.test_start = args.train_end + 1
    elif args.validation_mode == "rolling_forward_backtest":
        args.mode = "rolling"
    elif args.validation_mode == "leave_one_year_out":
        payload = {
            "mode": "leave_one_year_out",
            "source_policy": source_policy,
            "runs": [
                backtest_model(
                    args.train_start,
                    year - 1,
                    year,
                    year,
                    source_policy=source_policy,
                )
                for year in range(args.test_start, args.test_end + 1)
                if year > args.train_start
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.mode == "full":
        payload = full_replay_backtest(args.test_start, args.test_end, source_policy=source_policy)
    elif args.mode == "rolling":
        payload = rolling_validation(
            args.train_start,
            args.test_start,
            args.test_end,
            source_policy=source_policy,
        )
    else:
        payload = backtest_model(
            args.train_start,
            args.train_end,
            args.test_start,
            args.test_end,
            source_policy=source_policy,
        )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
