from __future__ import annotations

import json
from pathlib import Path

from app.provenance import snapshot as snap


def test_hash_dataset_is_deterministic_for_json_key_order(tmp_path: Path):
    file_path = tmp_path / "dataset.json"
    file_path.write_text('{"b":2,"a":1}', encoding="utf-8")

    h1 = snap.hash_dataset([file_path])

    # Same JSON data, different key ordering should hash the same.
    file_path.write_text('{"a":1,"b":2}', encoding="utf-8")
    h2 = snap.hash_dataset([file_path])

    assert h1 == h2


def test_snapshot_verify_detects_tamper(tmp_path: Path, monkeypatch):
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps({"hello": "world"}), encoding="utf-8")

    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"rule": 1}), encoding="utf-8")

    backend_data = tmp_path / "backend_data"
    snapshots_dir = backend_data / "snapshots"
    backend_data.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(snap, "BACKEND_DATA_DIR", backend_data)
    monkeypatch.setattr(snap, "SNAPSHOT_DIR", snapshots_dir)
    monkeypatch.setattr(snap, "LATEST_POINTER", snapshots_dir / "latest.json")
    monkeypatch.setattr(snap, "LEGACY_FESTIVAL_SNAPSHOT", backend_data / "snapshot.json")
    monkeypatch.setattr(snap, "DEFAULT_DATASET_FILES", [dataset])
    monkeypatch.setattr(snap, "DEFAULT_RULE_FILES", [rules])

    record = snap.create_snapshot("snap_test")
    ok = snap.verify_snapshot(record.snapshot_id)
    assert ok["valid"] is True

    # Tamper with dataset file and ensure verification fails.
    dataset.write_text(json.dumps({"hello": "tampered"}), encoding="utf-8")
    bad = snap.verify_snapshot(record.snapshot_id)
    assert bad["valid"] is False
    assert bad["checks"]["dataset_hash_match"] is False
