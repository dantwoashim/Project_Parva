from __future__ import annotations

from copy import deepcopy

from app.workflows.date_risk_audit import (
    audit_date_rows,
    build_date_risk_timepack,
    verify_date_risk_timepack,
)


def test_date_risk_audit_emits_row_proofs_and_findings() -> None:
    rows = [
        {"bs_date": "2082-01-01", "workflow_type": "payroll", "actual_ad_date": "2025-04-14"},
        {"bs_date": "2082-01-32", "workflow_type": "payroll"},
    ]

    results = audit_date_rows(rows, include_proofs=True)

    assert results[0]["status"] == "review_required"
    assert "holiday_conflict" in results[0]["issues"]
    assert len(results[0]["proof_packs"]) == 4
    assert results[1]["status"] == "review_required"
    assert "invalid_bs_date" in results[1]["issues"]


def test_date_risk_timepack_verifies_and_tamper_fails() -> None:
    timepack = build_date_risk_timepack([{"bs_date": "2082-01-02", "workflow_type": "payroll"}])

    assert verify_date_risk_timepack(timepack) == (True, "verified")

    tampered = deepcopy(timepack)
    tampered["aggregate_witness_hash"] = "sha256:wrong"

    assert verify_date_risk_timepack(tampered) == (False, "timepack_aggregate_hash_mismatch")
