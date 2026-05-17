from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any, Callable

import pytest
from app.membranes.capsule import (
    build_ad_to_bs_capsule,
    build_bs_months_capsule,
    build_fiscal_year_capsule,
    build_holiday_capsule,
    build_validate_bs_date_capsule,
    build_working_day_capsule,
)
from app.membranes.verifier import verify_membrane
from app.sources.hashing import canonical_json_hash
from app.witnesses.hashing import witness_hash


def _make_wrong_but_self_consistent(membrane: dict[str, Any], wrong_result: dict[str, Any]) -> dict[str, Any]:
    tampered = deepcopy(membrane)
    tampered["result"] = wrong_result
    tampered["proof_pack"]["steps"][-1]["output_hash"] = f"sha256:{canonical_json_hash(wrong_result)}"
    tampered["witness"]["output_hash"] = f"sha256:{canonical_json_hash(wrong_result)}"
    witness_without_id = {key: value for key, value in tampered["witness"].items() if key != "witness_id"}
    new_witness_id = witness_hash(witness_without_id)
    tampered["witness"]["witness_id"] = new_witness_id
    tampered["witness_hash"] = new_witness_id
    return tampered


BUILDERS: list[tuple[str, Callable[[], dict[str, Any]], dict[str, Any]]] = [
    (
        "ad_to_bs",
        lambda: build_ad_to_bs_capsule(date(2025, 4, 14)),
        {"bs_date": "2082-01-02", "year": 2082, "month": 1, "day": 2},
    ),
    (
        "validate_bs_date",
        lambda: build_validate_bs_date_capsule(2082, 1, 1),
        {"valid": False, "bs_date": "2082-01-01", "reason": "wrong", "year": 2082, "month": 1, "day": 1, "max_day": 30},
    ),
    (
        "holiday",
        lambda: build_holiday_capsule(2082, 1, 1),
        {
            "bs_date": "2082-01-01",
            "profile_id": "nepal_public_general",
            "is_holiday": False,
            "holiday": None,
            "source_set": "public_fixed_date_corpus",
            "membership_key": "01-01",
            "membership_proof": {"claim_index_hash": "sha256:wrong", "proof_type": "non_membership"},
        },
    ),
    (
        "working_day",
        lambda: build_working_day_capsule(2082, 1, 1),
        {
            "bs_date": "2082-01-01",
            "ad_date": "2025-04-14",
            "profile_id": "nepal_private_company_default",
            "decision_intent": "general",
            "is_working_day": True,
            "is_business_day": True,
            "requires_human_review": False,
            "reason_codes": ["WEEKDAY"],
            "holiday": None,
        },
    ),
    (
        "fiscal_year",
        lambda: build_fiscal_year_capsule(2082),
        {"fiscal_year": "FY 2082/83", "start": {"bs": "2082-04-02", "ad": "2025-07-18"}, "end": {}, "basis": "wrong"},
    ),
    (
        "bs_months",
        lambda: build_bs_months_capsule(2082),
        {
            "bs_year": 2082,
            "requested_mode": "canonical",
            "selected_method": "wrong",
            "total_days": 1,
            "months": [],
            "branch_set": None,
            "branches": None,
            "policy_decision": {},
        },
    ),
]


@pytest.mark.parametrize(("operation", "builder", "_wrong"), BUILDERS)
def test_civil_membrane_good_artifact_verifies(
    operation: str,
    builder: Callable[[], dict[str, Any]],
    _wrong: dict[str, Any],
) -> None:
    membrane = builder()

    assert membrane["canonical_query"]["operation"] == operation
    assert membrane["identity_hash"].startswith("parva:id:v1:sha256:")
    assert membrane["witness_hash"].startswith("parva:wit:v1:sha256:")
    assert membrane["boundary"]["claim_boundary"]
    assert membrane["policy_trace"]["operation"] == operation
    assert set(membrane["result"]).issubset(membrane["field_provenance"])
    assert verify_membrane(membrane) == (True, "verified")


@pytest.mark.parametrize(("operation", "builder", "wrong"), BUILDERS)
def test_civil_membrane_wrong_but_self_consistent_artifact_fails(
    operation: str,
    builder: Callable[[], dict[str, Any]],
    wrong: dict[str, Any],
) -> None:
    del operation
    membrane = _make_wrong_but_self_consistent(builder(), wrong)

    assert verify_membrane(membrane) == (False, "replayed_result_mismatch")


@pytest.mark.parametrize(("operation", "builder", "_wrong"), BUILDERS)
def test_civil_membrane_source_snapshot_mismatch_fails(
    operation: str,
    builder: Callable[[], dict[str, Any]],
    _wrong: dict[str, Any],
) -> None:
    del operation
    membrane = deepcopy(builder())
    membrane["source_snapshot_hash"] = "sha256:wrong"

    assert verify_membrane(membrane) == (False, "source_snapshot_hash_mismatch")


def test_no_sample_docket_confers_authority_to_future_core_operations() -> None:
    for membrane in (
        build_validate_bs_date_capsule(2099, 1, 1),
        build_holiday_capsule(2099, 1, 1),
        build_working_day_capsule(2099, 1, 1),
        build_bs_months_capsule(2099),
    ):
        assert "sample-2082" not in " ".join(membrane["source_docket_ids"])
        assert membrane["boundary"]["authority"] != "structured_official"
        assert membrane["boundary"]["review_state"] == "required"


def test_invalid_bs_date_emits_negative_replayable_membrane() -> None:
    membrane = build_validate_bs_date_capsule(2082, 1, 32)

    assert membrane["membrane_kind"] == "negative"
    assert membrane["result"]["valid"] is False
    assert verify_membrane(membrane) == (True, "verified")
