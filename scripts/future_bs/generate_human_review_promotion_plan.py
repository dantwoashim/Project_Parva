#!/usr/bin/env python3
"""Generate the top-100 human review promotion plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.active_learning.promotion_plan import (  # noqa: E402
    build_human_review_promotion_plan,
    write_human_review_promotion_plan,
)


def main() -> int:
    rows = build_human_review_promotion_plan()
    paths = write_human_review_promotion_plan(rows)
    print(json.dumps({"rows": len(rows), "publication_status": "computed_prediction_not_official"}, indent=2))
    print(json.dumps({key: str(value) for key, value in paths.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
