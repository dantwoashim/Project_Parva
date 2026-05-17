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
    assert membrane["source_snapshot_hash"].startswith("sha256:")
    assert membrane["proof_pack"]["source_artifacts"]["source_snapshot_hash"] == membrane["source_snapshot_hash"]
    assert membrane["witness"]["method_parameters"]["source_snapshot_hash"] == membrane["source_snapshot_hash"]
    assert membrane["source_docket_ids"]
    assert verify_membrane(membrane)[0]


def test_convert_bs_to_ad_membrane_tamper_detection_covers_result_and_witness() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)

    tampered_result = dict(membrane)
    tampered_result["result"] = {"ad_date": "2025-04-15"}
    assert verify_membrane(tampered_result) == (False, "witness_output_hash_mismatch")

    tampered_witness = dict(membrane)
    tampered_witness["witness"] = {**membrane["witness"], "verifier_version": "2.0.0"}
    assert verify_membrane(tampered_witness) == (False, "witness_hash_mismatch")
