#!/usr/bin/env python3
"""Build the public boundary-suite artifact from fixture-backed regression checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.reliability import get_boundary_suite

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = PROJECT_ROOT / "backend" / "data" / "public_artifacts" / "boundary_suite.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the boundary-suite artifact.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path.")
    args = parser.parse_args()

    payload = get_boundary_suite()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
