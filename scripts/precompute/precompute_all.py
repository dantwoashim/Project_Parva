#!/usr/bin/env python3
"""Run all precompute jobs used by M29 zero-cost scale plan."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Precompute panchanga + festival artifacts")
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)
    args = parser.parse_args()

    _run(
        [
            "python3",
            "scripts/precompute/precompute_panchanga.py",
            "--start-year",
            str(args.start_year),
            "--end-year",
            str(args.end_year),
        ]
    )
    _run(
        [
            "python3",
            "scripts/precompute/precompute_festivals.py",
            "--start-year",
            str(args.start_year),
            "--end-year",
            str(args.end_year),
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
