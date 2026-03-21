from __future__ import annotations

from pathlib import Path

from app.provenance import attestation


def test_attestation_uses_configured_key_file(tmp_path: Path, monkeypatch):
    key_file = tmp_path / "attestation.key"
    key_id_file = tmp_path / "attestation.key_id"
    key_file.write_text("file-backed-secret", encoding="utf-8")
    key_id_file.write_text("pytest-file-key", encoding="utf-8")

    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY", raising=False)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID", raising=False)
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY_FILE", str(key_file))
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID_FILE", str(key_id_file))

    payload = {"snapshot_id": "snap_test", "dataset_hash": "abc"}
    built = attestation.build_attestation(payload)

    assert built["mode"] == "hmac-sha256"
    assert built["key_id"] == "pytest-file-key"
    assert attestation.verify_attestation(payload, built) is True
