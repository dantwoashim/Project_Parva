from __future__ import annotations

import json
from pathlib import Path

from app.bootstrap.access_control import classify_request
from app.provenance import transparency
from app.security.audit import emit_security_audit_event


class _Request:
    url = type("Url", (), {"path": "/v3/api/provenance/transparency/append"})()
    state = type(
        "State",
        (),
        {
            "principal": type("Principal", (), {"principal_id": "admin", "principal_type": "admin"})(),
            "request_id": "req-123",
            "client_ip": "203.0.113.10",
        },
    )()


def test_security_audit_event_is_persisted_with_state_hashes(tmp_path: Path, monkeypatch):
    log_path = tmp_path / "security-audit.jsonl"
    monkeypatch.setenv("PARVA_SECURITY_AUDIT_LOG", str(log_path))

    emitted = emit_security_audit_event(
        _Request(),
        action="provenance.transparency.append",
        object_type="transparency_entry",
        object_id="tle_1",
        before={"head_hash": "old"},
        after={"head_hash": "new", "email": "person@example.com"},
        metadata={"email": "person@example.com"},
    )

    rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert rows == [emitted]
    assert rows[0]["actor_principal"] == "admin"
    assert rows[0]["request_id"] == "req-123"
    assert rows[0]["before_hash"].startswith("sha256:")
    assert rows[0]["after_hash"].startswith("sha256:")
    assert "person@example.com" not in log_path.read_text(encoding="utf-8")


def test_provenance_mutations_are_admin_only():
    requirement = classify_request("/v3/api/provenance/transparency/append", "POST")

    assert requirement.required is True
    assert requirement.admin_only is True
    assert requirement.policy_name == "provenance_admin"


def test_transparency_anchor_payloads_keep_hash_chain_state(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(transparency, "TRANSPARENCY_DIR", tmp_path)
    monkeypatch.setattr(transparency, "TRANSPARENCY_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(transparency, "ANCHOR_LOG", tmp_path / "anchors.jsonl")

    transparency.append_entry("manual_event", {"note": "ok"})
    anchor = transparency.record_anchor("0xabc", "testnet")

    assert anchor["payload"]["head_hash"]
    assert anchor["payload"]["total_entries"] == 1
