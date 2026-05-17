#!/usr/bin/env python3
"""Build the public static index for one BS year."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.forge.static_bundle import build_year_bundle  # noqa: E402


def main() -> int:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2082
    build_year_bundle(year, PROJECT_ROOT / "static" / "parva-index")
    print(f"Built static index for {year}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
