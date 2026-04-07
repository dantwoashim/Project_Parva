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
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY", raising=False)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY_FILE", raising=False)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID", raising=False)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID_FILE", raising=False)

    record = snap.create_snapshot("snap_test")
    assert record.attestation["mode"] == "unsigned"
    assert record.artifact_id == f"sha256:{record.manifest_hash}"
    assert record.artifact_root is not None
    assert "snapshot" in record.artifact_paths
    ok = snap.verify_snapshot(record.snapshot_id)
    assert ok["valid"] is True
    assert ok["checks"]["attestation_valid"] is True

    # Tamper with dataset file and ensure verification fails.
    dataset.write_text(json.dumps({"hello": "tampered"}), encoding="utf-8")
    bad = snap.verify_snapshot(record.snapshot_id)
    assert bad["valid"] is False
    assert bad["checks"]["dataset_hash_match"] is False


def test_snapshot_builds_hmac_attestation_when_key_configured(tmp_path: Path, monkeypatch):
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
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-attestation-key")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID", "pytest-key")

    record = snap.create_snapshot("snap_hmac")
    assert record.attestation["mode"] == "hmac-sha256"
    assert record.attestation["key_id"] == "pytest-key"
    assert record.artifact_paths["snapshot"].endswith("/snapshot.json")

    verification = snap.verify_snapshot(record.snapshot_id)
    assert verification["valid"] is True
    assert verification["checks"]["attestation_valid"] is True


def test_get_provenance_payload_exposes_immutable_artifact_identity(tmp_path: Path, monkeypatch):
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps({"hello": "world"}), encoding="utf-8")
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"rule": 1}), encoding="utf-8")

    backend_data = tmp_path / "backend_data"
    snapshots_dir = backend_data / "snapshots"
    backend_data.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(snap, "BACKEND_DATA_DIR", backend_data)
    monkeypatch.setattr(snap, "SNAPSHOT_DIR", snapshots_dir)
    monkeypatch.setattr(snap, "ARTIFACT_DIR", snapshots_dir / "artifacts")
    monkeypatch.setattr(snap, "LATEST_POINTER", snapshots_dir / "latest.json")
    monkeypatch.setattr(snap, "LEGACY_FESTIVAL_SNAPSHOT", backend_data / "snapshot.json")
    monkeypatch.setattr(snap, "DEFAULT_DATASET_FILES", [dataset])
    monkeypatch.setattr(snap, "DEFAULT_RULE_FILES", [rules])

    record = snap.create_snapshot("snap_artifact_identity")
    payload = snap.get_provenance_payload(verify_url="/v3/api/provenance/root")

    assert payload["artifact_id"] == f"sha256:{record.manifest_hash}"
    assert payload["artifact_root"] == record.artifact_root
    assert payload["artifact_paths"]["snapshot"] == record.artifact_paths["snapshot"]


def test_get_latest_snapshot_refreshes_stale_manifest_records(tmp_path: Path, monkeypatch):
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    stale_id = "snap_stale"
    stale_path = snapshots_dir / f"{stale_id}.json"
    stale_path.write_text(
        json.dumps(
            {
                "snapshot_id": stale_id,
                "created_at": "2026-03-01T00:00:00+00:00",
                "dataset_hash": "dataset",
                "rules_hash": "rules",
                "engine_version": "v3",
                "dataset_files": [],
                "rule_files": [],
                "festival_snapshot_path": None,
                "manifest_version": "legacy",
                "canonical_engine_id": "legacy-engine",
                "manifest_hash": None,
                "build_sha": "abc123",
                "dependency_lock_hash": "dep",
                "python_runtime": "3.11.4",
                "ephemeris_header": "legacy",
                "engine_manifest": {},
                "attestation": {},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    latest_pointer = snapshots_dir / "latest.json"
    latest_pointer.write_text(json.dumps({"snapshot_id": stale_id}), encoding="utf-8")

    monkeypatch.setattr(snap, "SNAPSHOT_DIR", snapshots_dir)
    monkeypatch.setattr(snap, "LATEST_POINTER", latest_pointer)

    created = snap.SnapshotRecord(
        snapshot_id="snap_fresh",
        created_at="2026-03-21T00:00:00+00:00",
        dataset_hash="dataset-fresh",
        rules_hash="rules-fresh",
        engine_version="v3",
        dataset_files=[],
        rule_files=[],
        manifest_version=snap.CANONICAL_MANIFEST_VERSION,
        canonical_engine_id=snap.CANONICAL_ENGINE_ID,
        manifest_hash="manifest-hash",
        build_sha="def456",
        dependency_lock_hash="dep",
        python_runtime="3.11.4",
        ephemeris_header="SE2",
        engine_manifest={"canonical_engine_id": snap.CANONICAL_ENGINE_ID},
        attestation={"mode": "unsigned", "algorithm": None, "key_id": None, "value": None},
    )
    monkeypatch.setattr(snap, "create_snapshot", lambda: created)

    latest = snap.get_latest_snapshot(create_if_missing=True)
    assert latest.snapshot_id == "snap_fresh"


def test_get_latest_snapshot_refreshes_invalid_attestation_records(tmp_path: Path, monkeypatch):
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    stale_id = "snap_invalid_attestation"
    stale_path = snapshots_dir / f"{stale_id}.json"
    stale_path.write_text(
        json.dumps(
            {
                "snapshot_id": stale_id,
                "created_at": "2026-03-01T00:00:00+00:00",
                "dataset_hash": "dataset",
                "rules_hash": "rules",
                "engine_version": "v3",
                "dataset_files": [],
                "rule_files": [],
                "festival_snapshot_path": None,
                "manifest_version": snap.CANONICAL_MANIFEST_VERSION,
                "canonical_engine_id": snap.CANONICAL_ENGINE_ID,
                "manifest_hash": "manifest-hash",
                "build_sha": "abc123",
                "dependency_lock_hash": "dep",
                "python_runtime": "3.11.4",
                "ephemeris_header": "SE2",
                "engine_manifest": {"canonical_engine_id": snap.CANONICAL_ENGINE_ID},
                "attestation": {
                    "mode": "hmac-sha256",
                    "algorithm": "hmac-sha256",
                    "key_id": "foreign-key",
                    "value": "invalid",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    latest_pointer = snapshots_dir / "latest.json"
    latest_pointer.write_text(json.dumps({"snapshot_id": stale_id}), encoding="utf-8")

    monkeypatch.setattr(snap, "SNAPSHOT_DIR", snapshots_dir)
    monkeypatch.setattr(snap, "LATEST_POINTER", latest_pointer)

    created = snap.SnapshotRecord(
        snapshot_id="snap_refreshed",
        created_at="2026-03-21T00:00:00+00:00",
        dataset_hash="dataset-fresh",
        rules_hash="rules-fresh",
        engine_version="v3",
        dataset_files=[],
        rule_files=[],
        manifest_version=snap.CANONICAL_MANIFEST_VERSION,
        canonical_engine_id=snap.CANONICAL_ENGINE_ID,
        manifest_hash="manifest-hash",
        build_sha="def456",
        dependency_lock_hash="dep",
        python_runtime="3.11.4",
        ephemeris_header="SE2",
        engine_manifest={"canonical_engine_id": snap.CANONICAL_ENGINE_ID},
        attestation={"mode": "unsigned", "algorithm": None, "key_id": None, "value": None},
    )
    monkeypatch.setattr(snap, "create_snapshot", lambda: created)

    latest = snap.get_latest_snapshot(create_if_missing=True)
    assert latest.snapshot_id == "snap_refreshed"
