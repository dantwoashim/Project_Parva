#!/usr/bin/env python3
"""Run deterministic public agent benchmark cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.agent_service import (  # noqa: E402
    check_human_review_payload,
    plan_schedule_payload,
    resolve_intent_payload,
    run_tool_payload,
    verify_temporal_claim_payload,
)


def main() -> int:
    cases = [
        ("claim_verified", lambda: verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-14 AD.")["status"] == "verified"),
        ("claim_false", lambda: verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-15 AD.")["status"] == "false"),
        (
            "claim_unsupported",
            lambda: verify_temporal_claim_payload("Tell me if this legal contract date is official.")["decision"]["requires_human_review"] is True,
        ),
        (
            "future_official_review_required",
            lambda: verify_temporal_claim_payload("Is 2090-01-01 official for this operational decision?")["decision"]["requires_human_review"] is True,
        ),
        (
            "payroll_sensitive_review_required",
            lambda: check_human_review_payload({"use_case": "payroll", "confidence": "source_backed"})["requires_human_review"] is True,
        ),
        (
            "banking_sensitive_review_required",
            lambda: check_human_review_payload({"use_case": "banking", "confidence": "source_backed"})["requires_human_review"] is True,
        ),
        (
            "private_data_unavailable_review_required",
            lambda: check_human_review_payload({"confidence": "unknown", "reason_codes": ["PRIVATE_DATA_UNAVAILABLE"]})["decision"][
                "reason_codes"
            ]
            and check_human_review_payload({"confidence": "unknown", "reason_codes": ["PRIVATE_DATA_UNAVAILABLE"]})[
                "requires_human_review"
            ]
            is True,
        ),
        (
            "source_conflict_review_required",
            lambda: check_human_review_payload({"confidence": "disputed", "reason_codes": ["DISPUTED_FACT_REVIEW_REQUIRED"]})[
                "requires_human_review"
            ]
            is True,
        ),
        (
            "official_source_missing_review_required",
            lambda: verify_temporal_claim_payload("Is 2091-01-01 official without a public official source?")["decision"][
                "requires_human_review"
            ]
            is True,
        ),
        (
            "ambiguous_intent_requires_confirmation",
            lambda: resolve_intent_payload("Convert this fiscal payroll claim for 2083-01-01 BS.")["requires_confirmation"] is True,
        ),
        (
            "fiscal_lookup_tool",
            lambda: run_tool_payload("parva.get_fiscal_period", {"bs_date": "2083-01-01"})["decision"]["status"] == "approved",
        ),
        ("schedule_public", lambda: len(plan_schedule_payload(schedule_type="payroll", bs_year=2082, months=[1])["items"]) == 1),
        (
            "impact_reasoning_tool",
            lambda: run_tool_payload(
                "parva.simulate_impact",
                {
                    "change_set": {
                        "change_set_id": "agent_benchmark_fact_change",
                        "changes": [
                            {
                                "change_type": "FACT_CHANGED",
                                "entity_type": "temporal_fact",
                                "entity_id": "fact_month_length_bs_2082_04",
                            }
                        ],
                    }
                },
            )["result"]["summary"]["impacts_found"] >= 1,
        ),
    ]
    results = []
    for case_id, runner in cases:
        ok = bool(runner())
        results.append({"case_id": case_id, "status": "pass" if ok else "fail"})
    failed = [result for result in results if result["status"] != "pass"]
    report = {
        "benchmark": "agent_temporal_reasoning_public",
        "cases": results,
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "status": "pass" if not failed else "fail",
    }
    print(json.dumps(report, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
