from __future__ import annotations

from copy import deepcopy

from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.membranes.verifier import verify_membrane
from app.sources.hashing import canonical_json_hash
from app.witnesses.hashing import witness_hash


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
    assert membrane["boundary"]["authority"] == "static_reference"
    assert membrane["source_resolution"]["coverage_status"] == "covered_by_reference_source_not_official"
    assert verify_membrane(membrane)[0]


def test_convert_bs_to_ad_membrane_tamper_detection_covers_result_and_witness() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)

    tampered_result = dict(membrane)
    tampered_result["result"] = {"ad_date": "2025-04-15"}
    assert verify_membrane(tampered_result) == (False, "witness_output_hash_mismatch")

    tampered_witness = dict(membrane)
    tampered_witness["witness"] = {**membrane["witness"], "verifier_version": "2.0.0"}
    assert verify_membrane(tampered_witness) == (False, "witness_hash_mismatch")


def test_wrong_but_self_consistent_membrane_fails() -> None:
    membrane = deepcopy(build_convert_bs_to_ad_capsule(2082, 1, 1))
    wrong_result = {"ad_date": "2025-04-15"}
    membrane["result"] = wrong_result
    membrane["proof_pack"]["steps"][-1]["output_hash"] = f"sha256:{canonical_json_hash(wrong_result)}"
    membrane["witness"]["output_hash"] = f"sha256:{canonical_json_hash(wrong_result)}"
    witness_without_id = {key: value for key, value in membrane["witness"].items() if key != "witness_id"}
    new_witness_id = witness_hash(witness_without_id)
    membrane["witness"]["witness_id"] = new_witness_id
    membrane["witness_hash"] = new_witness_id

    assert verify_membrane(membrane) == (False, "replayed_result_mismatch")


def test_convert_bs_to_ad_membrane_replays_successfully() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)

    assert verify_membrane(membrane) == (True, "verified")


def test_membrane_fails_when_result_modified() -> None:
    membrane = deepcopy(build_convert_bs_to_ad_capsule(2082, 1, 1))
    membrane["result"] = {"ad_date": "2025-04-15"}

    assert verify_membrane(membrane) == (False, "witness_output_hash_mismatch")


def test_membrane_fails_when_source_snapshot_mismatch() -> None:
    membrane = deepcopy(build_convert_bs_to_ad_capsule(2082, 1, 1))
    membrane["source_snapshot_hash"] = "sha256:wrong"

    assert verify_membrane(membrane) == (False, "source_snapshot_hash_mismatch")


def test_membrane_fails_when_static_bundle_modified() -> None:
    membrane = deepcopy(build_convert_bs_to_ad_capsule(2082, 1, 1))
    membrane["proof_pack"]["steps"][-1]["output_hash"] = "sha256:wrong"

    assert verify_membrane(membrane) == (False, "proof_pack_result_hash_mismatch")


def test_membrane_rejects_irrelevant_source_docket_for_2070() -> None:
    membrane = build_convert_bs_to_ad_capsule(2070, 1, 1)

    assert "sample-2082" not in " ".join(membrane["source_docket_ids"])
    assert membrane["boundary"]["authority"] == "computed_uncertified"
    assert membrane["boundary"]["review_state"] == "required"
    assert membrane["source_resolution"]["coverage_status"] == "no_eligible_source_coverage"


def test_membrane_rejects_sample_2082_docket_for_2099() -> None:
    membrane = build_convert_bs_to_ad_capsule(2099, 1, 1)

    assert membrane["source_docket_ids"] == []
    assert membrane["field_provenance"]["ad_date"]["source_docket_id"] is None
    assert membrane["boundary"]["authority"] != "structured_official"


def test_membrane_uses_official_docket_only_inside_covered_range() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)

    assert membrane["source_docket_ids"] == ["parva:src:v1:sample-2082-calendar-notice"]
    assert membrane["source_resolution"]["eligible_official"] is False
    assert membrane["boundary"]["authority"] == "static_reference"


def test_membrane_degrades_authority_outside_source_coverage() -> None:
    membrane = build_convert_bs_to_ad_capsule(2083, 1, 1)

    assert membrane["boundary"]["authority"] == "computed_uncertified"
    assert membrane["boundary"]["review_state"] == "required"
    assert "review_required" in membrane["field_provenance"]["ad_date"]["flags"]
