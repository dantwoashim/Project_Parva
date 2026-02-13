#!/usr/bin/env python3
"""Generate canonical festival_rules_v4.json from canonical ingestion pipeline.

Compatibility wrapper retained for older docs/scripts. Prefer:
`python3 scripts/rules/ingest_rule_sources.py`
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rules.catalog_v4 import CATALOG_V4_PATH, build_canonical_catalog  # noqa: E402


def main() -> int:
    catalog = build_canonical_catalog()
    CATALOG_V4_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_V4_PATH.write_text(
        json.dumps(catalog.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {CATALOG_V4_PATH}")
    print(f"Total rules: {catalog.total_rules}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
