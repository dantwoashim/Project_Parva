#!/usr/bin/env python3
"""Collect source-labeled AD/BS witness rows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.data_acquisition import collect_witnesses  # noqa: E402


def main() -> int:
    payload = collect_witnesses(fetch_rat32=True)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
