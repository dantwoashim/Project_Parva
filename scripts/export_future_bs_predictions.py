#!/usr/bin/env python3
"""Export future BS prediction rows from the API service layer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.future_bs_service import predictions_to_csv, predictions_to_xlsx  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2084)
    parser.add_argument("--end", type=int, default=2200)
    parser.add_argument("--format", choices=["csv", "xlsx"], default="csv")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "csv":
        args.output.write_text(predictions_to_csv(args.start, args.end), encoding="utf-8")
    else:
        args.output.write_bytes(predictions_to_xlsx(args.start, args.end))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
