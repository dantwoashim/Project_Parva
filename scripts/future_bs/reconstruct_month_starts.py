#!/usr/bin/env python3
"""Reconstruct BS month starts and month lengths from witnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.data_acquisition import (  # noqa: E402
    reconstruct_month_lengths,
    reconstruct_month_starts,
)


def main() -> int:
    starts, _ = reconstruct_month_starts()
    lengths = reconstruct_month_lengths(starts)
    print(json.dumps({"month_starts": len(starts), "month_lengths": len(lengths)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
