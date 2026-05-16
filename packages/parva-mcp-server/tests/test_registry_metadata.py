from __future__ import annotations

from parva_mcp_server.validate_registry_metadata import load_metadata, validate_metadata


def test_registry_metadata_is_valid_and_read_only():
    metadata = load_metadata()

    assert validate_metadata() == []
    assert metadata["read_only"] is True
    assert metadata["transport"] == "stdio"
    assert metadata["claim_boundary"] == "decision_support_not_authority"


def test_registry_metadata_does_not_claim_acceptance_or_authority():
    serialized = str(load_metadata()).lower()

    assert "accepted registry" not in serialized
    assert "government approved" not in serialized
    assert "official future" not in serialized
