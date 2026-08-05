#!/usr/bin/env python3
"""Research bounded high-trust public source paths and cache/log attempts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.high_trust_acquisition import research_and_collect_high_trust_sources  # noqa: E402,I001


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-urls-per-family", type=int, default=20)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()
    payload = research_and_collect_high_trust_sources(
        max_urls_per_family=args.max_urls_per_family,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
