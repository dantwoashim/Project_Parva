#!/usr/bin/env python3
"""Research bounded high-trust public source paths and cache/log attempts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.high_trust_acquisition import research_and_collect_high_trust_sources  # noqa: E402,I001


def main() -> int:
    payload = research_and_collect_high_trust_sources()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
