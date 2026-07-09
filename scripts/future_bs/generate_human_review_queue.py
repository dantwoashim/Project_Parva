#!/usr/bin/env python3
"""Generate the prioritized human review queue for weak/conflicting witnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.data_acquisition import generate_human_review_queue  # noqa: E402


def main() -> int:
    rows = generate_human_review_queue()
    print(json.dumps({"review_rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
