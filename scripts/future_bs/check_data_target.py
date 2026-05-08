#!/usr/bin/env python3
"""Fail unless the reconstructed witness corpus reaches a defined target."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.data_acquisition import check_data_target  # noqa: E402


def main() -> int:
    result = check_data_target()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["target_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
