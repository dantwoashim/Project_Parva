#!/usr/bin/env python3
"""Normalize extracted public evidence rows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.evidence.normalization import normalize_source_rows  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows_json")
    args = parser.parse_args()
    rows = json.loads(Path(args.rows_json).read_text(encoding="utf-8"))
    print(json.dumps(normalize_source_rows(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

