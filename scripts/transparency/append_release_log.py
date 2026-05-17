#!/usr/bin/env python3
"""Append a sample transparency log entry."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.transparency.log import append_log_entry  # noqa: E402


def main() -> int:
    entry = append_log_entry(
        PROJECT_ROOT / "data" / "transparency" / "log.jsonl",
        {"event": "phase_11_sample_release", "release_id": "phase-11-sample"},
    )
    print(entry["entry_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
