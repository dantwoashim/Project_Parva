from __future__ import annotations

import json
from pathlib import Path

from app.services.protocol_service import (
    issue_calendar_credential_payload,
    offline_bundle_manifest_payload,
    protocol_capabilities_payload,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_CREDENTIAL_CLAIMS = (
    "production-grade signature",
    "W3C certified credential",
    "official credential",
    "government-approved credential",
)


def test_issued_calendar_credential_is_hash_only_preview() -> None:
    credential = issue_calendar_credential_payload(
        {"claim_type": "date_conversion", "bs_date": "2083-01-01"}
    )["credential"]

    assert credential["status"] == "hash_only_preview"
    assert credential["proof"]["type"] == "sha256_content_hash"
    assert "hash_only_preview_not_production_signature" in credential["warnings"]


def test_protocol_and_offline_surfaces_keep_unsigned_preview_labels() -> None:
    capabilities = protocol_capabilities_payload()
    offline_manifest = offline_bundle_manifest_payload()

    assert "hash_only_preview_credentials" in capabilities["capabilities"]
    assert offline_manifest["signature_status"] == "unsigned_preview"
    assert offline_manifest["signature"] is None


def test_offline_bundle_manifest_payload_is_deterministic() -> None:
    first = offline_bundle_manifest_payload()
    second = offline_bundle_manifest_payload()

    assert first == second
    assert first["meta"]["trace_id"] == "offline_bundle_manifest"


def test_public_protocol_docs_do_not_overclaim_credentials() -> None:
    paths = [
        PROJECT_ROOT / "docs" / "PROTOCOL_CREDENTIALS.md",
        PROJECT_ROOT / "docs" / "PROTOCOL_SECURITY.md",
        PROJECT_ROOT / "specs" / "parva-protocol" / "PTS-012-verifiable-calendar-credential.md",
        PROJECT_ROOT / "schemas" / "parva-protocol" / "calendar-credential.schema.json",
    ]
    combined = "\n".join(
        path.read_text(encoding="utf-8") if path.suffix != ".json" else json.dumps(json.loads(path.read_text(encoding="utf-8")))
        for path in paths
    )

    assert "hash_only_preview" in combined
    for claim in FORBIDDEN_CREDENTIAL_CLAIMS:
        assert claim not in combined
