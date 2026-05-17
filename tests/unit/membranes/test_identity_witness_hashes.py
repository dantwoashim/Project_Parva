from __future__ import annotations

from copy import deepcopy

from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.membranes.verifier import verify_membrane


def test_identity_stable_but_witness_changes_on_result_tamper() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)
    same = build_convert_bs_to_ad_capsule(2082, 1, 1)
    assert membrane["identity_hash"] == same["identity_hash"]
    assert membrane["witness_hash"] == same["witness_hash"]
    assert verify_membrane(membrane) == (True, "verified")

    tampered = deepcopy(membrane)
    tampered["result"]["ad_date"] = "2025-04-15"
    ok, reason = verify_membrane(tampered)
    assert not ok
    assert reason == "witness_output_hash_mismatch"
