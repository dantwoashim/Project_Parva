#!/usr/bin/env python3
"""Record archive.org panchanga extraction status.

No public archive seed list is currently configured, so this script creates the
required blocker artifacts through the main acquisition loop.
"""

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
    attempts, failures = record_external_blocker_attempts()
    archive = [row for row in failures if "Archive.org" in row["source_name"]]
    print(json.dumps({"rows": 0, "archive_blockers": archive, "attempts": len(attempts)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
