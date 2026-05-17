from __future__ import annotations

import pytest
from app.trust.taint import AuthorityTaint, TaintedValue, authority_join
from app.trust.upgrade import ReviewWitness, apply_review_upgrade


def test_authority_join_is_monotone_to_weaker_authority() -> None:
    assert (
        authority_join(AuthorityTaint.STRUCTURED_OFFICIAL, AuthorityTaint.STATIC_REFERENCE)
        == AuthorityTaint.STATIC_REFERENCE
    )


def test_authority_upgrade_requires_matching_review_witness() -> None:
    value = TaintedValue("31", AuthorityTaint.STATIC_REFERENCE)
    with pytest.raises(ValueError):
        apply_review_upgrade(value, AuthorityTaint.COMPUTED_CERTIFIED, ReviewWitness.create(
            scope={"field": "other"},
            from_taint=AuthorityTaint.USER_SUPPLIED,
            to_taint=AuthorityTaint.COMPUTED_CERTIFIED,
            reviewer="maintainer",
            checklist_hash="sha256:demo",
        ))

    witness = ReviewWitness.create(
        scope={"field": "month_lengths"},
        from_taint=AuthorityTaint.STATIC_REFERENCE,
        to_taint=AuthorityTaint.COMPUTED_CERTIFIED,
        reviewer="maintainer",
        checklist_hash="sha256:demo",
    )
    assert apply_review_upgrade(value, AuthorityTaint.COMPUTED_CERTIFIED, witness).authority == AuthorityTaint.COMPUTED_CERTIFIED
