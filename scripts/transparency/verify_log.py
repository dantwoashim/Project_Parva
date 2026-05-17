#!/usr/bin/env python3
"""Verify sample transparency log."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.transparency.log import verify_log  # noqa: E402


def main() -> int:
    ok = verify_log(PROJECT_ROOT / "data" / "transparency" / "log.jsonl")
    print("Transparency log verified." if ok else "Transparency log failed.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
