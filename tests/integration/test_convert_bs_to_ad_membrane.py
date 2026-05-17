from __future__ import annotations

from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.membranes.verifier import verify_membrane


def test_convert_bs_to_ad_membrane_contains_required_proof_surface() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)
    assert membrane["result"]["ad_date"] == "2025-04-14"
    assert membrane["identity_hash"].startswith("parva:id:v1:sha256:")
    assert membrane["witness_hash"].startswith("parva:wit:v1:sha256:")
    assert "boundary" in membrane
    assert "field_provenance" in membrane
    assert membrane["source_docket_ids"]
    assert verify_membrane(membrane)[0]
