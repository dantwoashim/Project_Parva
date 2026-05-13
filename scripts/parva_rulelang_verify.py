#!/usr/bin/env python3
"""Verify Project Parva RuleLang rules and safety gates."""

# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.rulelang_service import (  # noqa: E402
    ABSOLUTE_LOOP_MAX_ITERATIONS,
    ALLOWED_FUNCTIONS,
    RuleLangError,
    evaluate_custom_rule_payload,
    evaluate_rule_payload,
    load_rules,
    rulelang_capabilities_payload,
    run_all_rule_tests_payload,
    validate_rule_payload,
)


def _assert_forbidden_function_rejected() -> None:
    invalid = {
        "rule_id": "invalid_eval_rule",
        "version": "1.0.0",
        "label": "Invalid eval",
        "description": "Invalid rule used by verifier.",
        "status": "fixture_only",
        "inputs": {"bs_date": {"type": "bs_date", "required": True}},
        "outputs": {"result": {"type": "object"}},
        "steps": [
            {
                "set": {
                    "name": "bad",
                    "value": {"call": "eval", "args": {"code": "1 + 1"}},
                }
            },
            {"return": {"result": "$var.bad"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": "source_backed",
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }
    validation = validate_rule_payload(invalid)
    if validation["valid"]:
        raise RuleLangError("forbidden eval function was accepted")


def _assert_loop_limit_blocks() -> None:
    rule = {
        "rule_id": "fixture_loop_limit_rule",
        "version": "1.0.0",
        "label": "Loop limit fixture",
        "description": "Verifier fixture for bounded loop failure.",
        "status": "fixture_only",
        "inputs": {"bs_date": {"type": "bs_date", "required": True}},
        "outputs": {"result": {"type": "object"}},
        "steps": [
            {"set": {"name": "candidate", "value": "$input.bs_date"}},
            {
                "while": {
                    "condition": True,
                    "max_iterations": 1,
                    "do": [
                        {
                            "set": {
                                "name": "candidate",
                                "value": {
                                    "call": "subtract_days",
                                    "args": {"date": "$var.candidate", "days": 1},
                                },
                            }
                        }
                    ],
                }
            },
            {"return": {"result": "$var.candidate"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": "source_backed",
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }
    result = evaluate_custom_rule_payload(rule, {"bs_date": "2082-04-04"})
    if result["decision"]["status"] != "failed":
        raise RuleLangError("unbounded loop fixture did not fail")
    if "MAX_ITERATIONS_EXCEEDED" not in result["decision"]["reason_codes"]:
        raise RuleLangError("loop limit failure did not include MAX_ITERATIONS_EXCEEDED")


def _assert_disputed_fact_blocks() -> None:
    rule = {
        "rule_id": "fixture_disputed_fact_rule",
        "version": "1.0.0",
        "label": "Disputed fact fixture",
        "description": "Verifier fixture for TimeGraph dispute policy.",
        "status": "fixture_only",
        "inputs": {"marker": {"type": "string", "required": False, "default": "fixture"}},
        "outputs": {"disputed": {"type": "boolean"}},
        "steps": [
            {
                "set": {
                    "name": "disputed",
                    "value": {
                        "call": "fact_is_disputed",
                        "args": {"fact_id": "fact_fixture_conflict_candidate_a"},
                    },
                }
            },
            {"return": {"disputed": "$var.disputed"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": "fixture",
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }
    result = evaluate_custom_rule_payload(rule, {})
    if result["decision"]["status"] != "blocked":
        raise RuleLangError("disputed TimeGraph fact did not block")
    if "DISPUTED_FACT_BLOCKED" not in result["decision"]["reason_codes"]:
        raise RuleLangError("disputed TimeGraph fact missing reason code")


def main() -> int:
    try:
        rules = load_rules(include_private=False)
        if len(rules) < 3:
            raise RuleLangError("expected at least three public RuleLang rules")
        capabilities = rulelang_capabilities_payload()
        if "eval" in capabilities["builtins"]:
            raise RuleLangError("eval leaked into RuleLang builtins")
        if ABSOLUTE_LOOP_MAX_ITERATIONS > 366:
            raise RuleLangError("absolute loop limit is too wide")
        tests = run_all_rule_tests_payload()
        if not tests["ok"]:
            raise RuleLangError("embedded RuleLang tests failed")
        sample = evaluate_rule_payload(
            "last_working_day_of_nepali_month",
            {"bs_month": "2082-04", "profile_id": "nepal_private_company_default"},
        )
        if sample["decision"]["status"] != "approved":
            raise RuleLangError("sample public rule did not approve historical source-backed input")
        if not sample["trace"]["steps"]:
            raise RuleLangError("sample public rule did not include a trace")
        if not sample["fact_ids"]:
            raise RuleLangError("sample public rule did not include TimeGraph fact ids")
        _assert_forbidden_function_rejected()
        _assert_loop_limit_blocks()
        _assert_disputed_fact_blocks()
    except Exception as exc:  # noqa: BLE001
        print(f"Project Parva RuleLang verification failed: {exc}", file=sys.stderr)
        return 1

    print("Project Parva RuleLang verification")
    print(
        json.dumps(
            {
                "ok": True,
                "rule_count": len(rules),
                "builtins": sorted(ALLOWED_FUNCTIONS),
                "embedded_tests": tests["results"],
                "sample_decision": sample["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print("rulelang verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
