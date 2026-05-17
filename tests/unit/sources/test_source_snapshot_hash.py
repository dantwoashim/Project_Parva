from __future__ import annotations

import json
from pathlib import Path

from app.sources.snapshot import build_source_snapshot, load_json_files


def test_source_snapshot_hash_is_deterministic() -> None:
    dockets = load_json_files(list(Path("data/sources/dockets").glob("*.json")))
    receipts = load_json_files(list(Path("data/sources/extraction_receipts").glob("*.json")))
    first = build_source_snapshot(dockets, receipts)
    second = build_source_snapshot(dockets, receipts)
    assert first == second
    assert first["snapshot_hash"].startswith("sha256:")
    recorded = json.loads(Path("data/sources/source_snapshot.json").read_text(encoding="utf-8"))
    assert recorded["snapshot_hash"] == first["snapshot_hash"]
