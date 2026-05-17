#!/usr/bin/env python3
"""Build deterministic source snapshot from checked-in public source artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.sources.snapshot import build_source_snapshot, load_json_files  # noqa: E402


def main() -> int:
    docket_paths = list((PROJECT_ROOT / "data" / "sources" / "dockets").glob("*.json"))
    receipt_paths = list((PROJECT_ROOT / "data" / "sources" / "extraction_receipts").glob("*.json"))
    snapshot = build_source_snapshot(load_json_files(docket_paths), load_json_files(receipt_paths))
    output = PROJECT_ROOT / "data" / "sources" / "source_snapshot.json"
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(PROJECT_ROOT)} {snapshot['snapshot_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
