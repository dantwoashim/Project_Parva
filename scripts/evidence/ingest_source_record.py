#!/usr/bin/env python3
"""Validate a public evidence source record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.evidence.ingestion import ingest_source_record  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_record")
    args = parser.parse_args()
    payload = json.loads(Path(args.source_record).read_text(encoding="utf-8"))
    record = ingest_source_record(payload)
    print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

