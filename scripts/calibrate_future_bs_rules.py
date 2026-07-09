#!/usr/bin/env python3
"""Run civil-rule cutoff and ayanamsha candidate artifact generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.calibration import (  # noqa: E402
    calibrate_month_cutoffs,
    write_calibration_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-start", type=int, default=2000)
    parser.add_argument("--train-end", type=int, default=2083)
    parser.add_argument(
        "--source-policy",
        choices=["all_reference", "official_only", "official_plus_printed", "train_allowed"],
        default="train_allowed",
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = calibrate_month_cutoffs(args.train_start, args.train_end, source_policy=args.source_policy)
    if args.write:
        result["written_files"] = write_calibration_artifacts(
            args.train_start,
            args.train_end,
            source_policy=args.source_policy,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
