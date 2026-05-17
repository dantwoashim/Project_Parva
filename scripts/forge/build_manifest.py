#!/usr/bin/env python3
"""Rebuild static bundle manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.forge.manifest import build_manifest  # noqa: E402


def main() -> int:
    root = PROJECT_ROOT / "static" / "parva-index"
    manifest = build_manifest(root)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {root / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
