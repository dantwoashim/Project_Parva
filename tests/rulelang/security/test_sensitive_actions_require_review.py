from __future__ import annotations

from app.services.agent_service import check_human_review_payload, verify_temporal_claim_payload


def test_agent_sensitive_payroll_use_case_requires_human_review():
    result = check_human_review_payload(
        {
            "use_case": "payroll",
            "confidence": "source_backed",
            "decision": {"requires_human_review": False, "reason_codes": []},
        }
    )

    assert result["requires_human_review"] is True
    assert result["decision"]["status"] == "review_required"
    assert "PAYROLL_ACTION_REQUIRES_REVIEW" in result["decision"]["reason_codes"]


def test_agent_unsupported_claims_require_human_review():
    result = verify_temporal_claim_payload("Tell me the official public holiday for 2099-01-01")

    assert result["status"] == "needs_review"
    assert result["decision"]["requires_human_review"] is True
    assert "HUMAN_REVIEW_REQUIRED" in result["decision"]["reason_codes"]
