#!/usr/bin/env python3
"""Merge high-trust witness rows into the reconstructed witness corpus."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.high_trust_acquisition import merge_high_trust_witnesses  # noqa: E402


def main() -> int:
    payload = merge_high_trust_witnesses()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
