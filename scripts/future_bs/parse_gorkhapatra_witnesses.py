#!/usr/bin/env python3
"""Record public newspaper masthead acquisition status."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.data_acquisition import record_external_blocker_attempts  # noqa: E402


def main() -> int:
    _, failures = record_external_blocker_attempts()
    rows = [row for row in failures if "Gorkhapatra" in row["source_name"]]
    print(json.dumps({"rows": 0, "newspaper_blockers": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
