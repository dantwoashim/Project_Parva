from __future__ import annotations

from app.boundary.labels import BoundaryLabel, no_authority_boundary
from app.forge.claim_indexes import ClaimIndexEntry, build_claim_index
from app.membranes.adversarial import authority_overclaim_probe, tamper_result_probe
from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.policy.lenses import PAYROLL_REVIEW_LENS
from app.policy.trace import PolicyTrace
from app.sources.hashing import canonical_json_hash


def test_claim_index_root_is_deterministic() -> None:
    capsule = build_convert_bs_to_ad_capsule(2082, 1, 1)
    entry = ClaimIndexEntry(
        claim_id="sample",
        identity_hash=capsule["identity_hash"],
        witness_hash=capsule["witness_hash"],
        source_snapshot_hash=capsule["source_snapshot_hash"],
        boundary=capsule["boundary"],
    )

    index = build_claim_index([entry])

    assert index["root_hash"] == f"sha256:{canonical_json_hash(index['leaf_hashes'])}"
    assert index["entries"][0]["claim_id"] == "sample"


def test_policy_lens_projects_without_mutating_claim() -> None:
    claim = {
        "bs_date": "2082-01-01",
        "working_day": False,
        "private_note": "do not expose",
    }

    view = PAYROLL_REVIEW_LENS.apply(claim)

    assert view["canonical_unchanged"] is True
    assert view["result"] == {"bs_date": "2082-01-01", "working_day": False}
    assert claim["private_note"] == "do not expose"


def test_policy_trace_records_ordered_steps() -> None:
    trace = PolicyTrace("canonical@0.1.0")
    trace.add("rank_candidates", count=2)

    payload = trace.as_dict()

    assert payload["kind"] == "policy_trace"
    assert payload["steps"][0]["event"] == "rank_candidates"


def test_boundary_label_returns_no_authority_boundary() -> None:
    payload = no_authority_boundary(BoundaryLabel.COMPUTED_NOT_OFFICIAL)

    assert payload["not_authority"] is True
    assert "legal_authority" in payload["forbidden_claims"]


def test_adversarial_probes_reject_tamper_and_overclaim() -> None:
    capsule = build_convert_bs_to_ad_capsule(2082, 1, 1)

    tamper = tamper_result_probe(capsule, "ad_date", "2025-04-15")
    overclaim = authority_overclaim_probe(capsule, "legal_final_authority")

    assert tamper["verified"] is False
    assert overclaim["accepted"] is False
