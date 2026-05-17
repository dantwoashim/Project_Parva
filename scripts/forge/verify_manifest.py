#!/usr/bin/env python3
"""Verify static index manifest."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.forge.verify import verify_manifest  # noqa: E402


def main() -> int:
    ok = verify_manifest(PROJECT_ROOT / "static" / "parva-index")
    print("Static manifest verified." if ok else "Static manifest verification failed.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
