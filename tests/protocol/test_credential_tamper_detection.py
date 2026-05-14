from __future__ import annotations

import copy

from app.services.protocol_service import (
    issue_calendar_credential_payload,
    verify_calendar_credential_payload,
)


def test_hash_only_preview_credential_tamper_detection() -> None:
    credential = issue_calendar_credential_payload(
        {"claim_type": "date_conversion", "bs_date": "2083-01-01"}
    )["credential"]

    assert credential["status"] == "hash_only_preview"
    assert credential["proof"]["type"] == "sha256_content_hash"
    assert verify_calendar_credential_payload(credential)["valid"] is True

    tampered = copy.deepcopy(credential)
    tampered["claim"]["object"]["date"] = "2026-04-15"

    result = verify_calendar_credential_payload(tampered)

    assert result["valid"] is False
    assert "credential_hash_mismatch" in result["issues"]
