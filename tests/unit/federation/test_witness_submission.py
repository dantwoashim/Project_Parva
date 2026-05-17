from __future__ import annotations

import pytest
from app.federation.challenge import challenge_object
from app.federation.witness_submission import WitnessSubmission


def test_external_witness_starts_pending_untrusted() -> None:
    witness = WitnessSubmission(
        submitter_id="community-a",
        claim={"date": "2082-01-01"},
        source_docket={"source_id": "community-source"},
        proof_pack={"level": "audit"},
        signature=None,
        authority_scope="community_specific",
    )
    assert witness.as_dict()["status"] == "pending_untrusted"


def test_external_witness_cannot_claim_final_authority() -> None:
    witness = WitnessSubmission("x", {}, {}, {}, None, "legal_final")
    with pytest.raises(ValueError):
        witness.as_dict()


def test_challenge_workflow_object_exists() -> None:
    challenge = challenge_object("w1", "conflicting_source", {"id": "w2"})
    assert challenge["status"] == "open"
    assert challenge["counter_witness"]["id"] == "w2"
