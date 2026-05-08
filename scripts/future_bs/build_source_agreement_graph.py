#!/usr/bin/env python3
"""Build the source agreement graph from extracted witnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.data_acquisition import build_agreement_graph  # noqa: E402


def main() -> int:
    graph = build_agreement_graph()
    print(json.dumps({"nodes": len(graph["nodes"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
