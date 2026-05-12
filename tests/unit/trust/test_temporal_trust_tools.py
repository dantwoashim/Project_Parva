from __future__ import annotations

import json
from pathlib import Path

from tools.trust.append_log_entry import append_log_entry
from tools.trust.common import DEFAULT_MANIFEST_PATH, DEFAULT_SIGNATURE_PATH, ROOT
from tools.trust.sign_release import sign_release
from tools.trust.verify_log import verify_log
from tools.trust.verify_release_signature import verify_release_signature
from tools.validate_schemas import validate_schema_file


def test_alpha_release_signature_verifies_current_public_demo_artifact():
    messages = verify_release_signature(DEFAULT_MANIFEST_PATH, DEFAULT_SIGNATURE_PATH)

    assert any("parva-bs-public-demo" in message for message in messages)
    payload = json.loads(DEFAULT_SIGNATURE_PATH.read_text(encoding="utf-8"))
    assert payload["signature_algorithm"] == "alpha_hash_only_sha256"
    assert payload["artifact_hash"].startswith("sha256:")


def test_sign_release_writes_hash_only_signature_to_repo_tmp():
    output = ROOT / "tmp" / "test-parva-signature.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        payload = sign_release(DEFAULT_MANIFEST_PATH, output, signed_at="2026-05-12T00:00:00Z")
        assert output.exists()
        assert payload == json.loads(output.read_text(encoding="utf-8"))
        assert payload["signature_algorithm"] == "alpha_hash_only_sha256"
    finally:
        output.unlink(missing_ok=True)


def test_log_append_and_verify_work_on_repo_tmp_log():
    log_path = ROOT / "tmp" / "test-parva-log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)
    try:
        entry = append_log_entry(
            DEFAULT_MANIFEST_PATH,
            DEFAULT_SIGNATURE_PATH,
            log_path,
            timestamp="2026-05-12T00:00:00Z",
        )
        assert entry["event"] == "calendar.release.published"
        result = verify_log(log_path)
        assert result["valid"] is True
        assert result["total_entries"] == 1
    finally:
        log_path.unlink(missing_ok=True)


def test_phase_6_schemas_parse_and_validate_examples():
    for relative in [
        "schemas/signature.schema.json",
        "schemas/transparency-log-entry.schema.json",
        "schemas/temporal-sbom.schema.json",
        "schemas/reconciliation-event.schema.json",
    ]:
        validate_schema_file(ROOT / relative)


def test_trust_alpha_files_do_not_include_private_future_markers():
    checked_paths = [
        ROOT / "tools" / "trust" / "README.md",
        ROOT / "docs" / "TRUST_INFRASTRUCTURE_ALPHA.md",
        ROOT / "docs" / "TEMPORAL_SBOM.md",
        ROOT / "docs" / "TRANSPARENCY_LOG.md",
        ROOT / "docs" / "future_bs" / "RECONCILIATION_WORKFLOW.md",
    ]
    forbidden = ["2084", "2099", "2200", "InfoDevelopers", "infodev"]
    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, str(path.relative_to(ROOT))
