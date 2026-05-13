#!/usr/bin/env python3
"""Generate the month-start inversion workbench artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.month_start.inversion_workbench import (  # noqa: E402
    DEFAULT_MAX_YEAR,
    DEFAULT_OUTPUT_DIR,
    run_month_start_inversion_workbench,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build historical month-start inversion diagnostics from source-labeled rows.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where workbench artifacts are written.",
    )
    parser.add_argument(
        "--max-year",
        type=int,
        default=DEFAULT_MAX_YEAR,
        help="Maximum BS year to include. Defaults to 2083 to avoid future-output leakage.",
    )
    parser.add_argument(
        "--trusted-only",
        action="store_true",
        help="Include only official/printed training candidates instead of weak review targets.",
    )
    parser.add_argument(
        "--top-target-limit",
        type=int,
        default=100,
        help="Maximum number of verification targets to write.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_month_start_inversion_workbench(
        output_dir=args.output_dir,
        max_year=args.max_year,
        include_reference_targets=not args.trusted_only,
        top_target_limit=args.top_target_limit,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

