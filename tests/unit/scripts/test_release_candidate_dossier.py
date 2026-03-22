from __future__ import annotations

from scripts.release.generate_release_candidate_dossier import _public_attestation_key_id


def test_public_attestation_key_id_redacts_present_key_id():
    assert _public_attestation_key_id({"key_id": "local-release-ashim-20260320"}) == "redacted for public dossier"


def test_public_attestation_key_id_returns_none_when_missing():
    assert _public_attestation_key_id({}) is None
