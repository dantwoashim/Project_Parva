"""Agent-safe deterministic temporal tooling for Project Parva."""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from app.calendar.bikram_sambat import bs_to_gregorian
from app.services.calendar_conversion_service import (
    build_bs_to_gregorian_payload,
    build_conversion_payload,
    parse_iso_date,
)
from app.services.compliance_service import evaluate_date_payload, fiscal_period_payload
from app.services.impact_service import simulate_change_set_payload
from app.services.rulelang_service import (
    evaluate_rule_payload,
    explain_rule_payload,
    validate_rule_payload,
)
from app.services.timegraph_service import trace_fact_payload
from app.services.trust_infrastructure_service import (
    build_date_conversion_evidence_packet,
    now_utc,
    resolve_release_id,
)

AGENT_CLAIM_BOUNDARY = "agent_temporal_reasoning_not_legal_authority"
MAX_CLAIM_LENGTH = 2000
MAX_SCHEDULE_ITEMS = 400
MAX_TOOL_CALLS = 20
MAX_EXPLANATION_CHARS = 4000
SUPPORTED_SCHEDULE_RULE = "last_working_day_of_nepali_month"

AGENT_STATUSES = {"approved", "review_required", "blocked", "unsupported", "failed"}
AGENT_REASON_CODES = {
    "TEMPORAL_INTENT_RESOLVED",
    "TEMPORAL_INTENT_AMBIGUOUS",
    "TOOL_SELECTED",
    "TOOL_EXECUTED",
    "TOOL_UNAVAILABLE",
    "INPUT_VALIDATED",
    "INVALID_INPUT",
    "UNSUPPORTED_DATE_RANGE",
    "SOURCE_CONFIDENCE_TOO_LOW",
    "RESEARCH_PREVIEW_BLOCKED",
    "DISPUTED_FACT_REVIEW_REQUIRED",
    "FUTURE_DATE_REVIEW_REQUIRED",
    "PAYROLL_ACTION_REQUIRES_REVIEW",
    "BANKING_ACTION_REQUIRES_REVIEW",
    "LEGAL_ACTION_NOT_AUTHORIZED",
    "EVIDENCE_PACKET_GENERATED",
    "EVIDENCE_PACKET_REQUIRED",
    "RULE_DRAFT_REQUIRES_VALIDATION",
    "RULE_EXECUTION_REVIEW_REQUIRED",
    "IMPACT_SIMULATION_LIMITED",
    "HUMAN_REVIEW_REQUIRED",
    "PRIVATE_DATA_UNAVAILABLE",
    "CLAIM_VERIFIED",
    "CLAIM_DISPUTED",
    "CLAIM_UNSUPPORTED",
    "CLAIM_FALSE",
    "CLAIM_NEEDS_REVIEW",
}

BS_AD_CLAIM_RE = re.compile(
    r"(?P<bs>\d{4}-\d{2}-\d{2})\s*(?:BS|B\.S\.|Bikram Sambat)?\s*"
    r"(?:maps? to|is|=|corresponds to)\s*"
    r"(?P<ad>\d{4}-\d{2}-\d{2})\s*(?:AD|A\.D\.|Gregorian)?",
    re.IGNORECASE,
)


class AgentError(ValueError):
    """Raised when an agent-safe request cannot be fulfilled."""

    def __init__(self, message: str, *, code: str = "INVALID_INPUT", status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def agent_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "agentic_temporal_intelligence",
        "status": "public_preview",
        "active_release_id": resolve_release_id(None),
        "public_tools": [tool["name"] for tool in agent_tools_payload()["tools"]],
        "limits": {
            "max_claim_length": MAX_CLAIM_LENGTH,
            "max_schedule_items": MAX_SCHEDULE_ITEMS,
            "max_internal_tool_calls": MAX_TOOL_CALLS,
            "max_explanation_chars": MAX_EXPLANATION_CHARS,
        },
        "claim_boundary": AGENT_CLAIM_BOUNDARY,
        "not_claimed": [
            "generic_chatbot_truth",
            "legal_or_tax_final_authority",
            "official_future_calendar_publication",
        ],
        "meta": _agent_meta()["meta"],
    }


def agent_tools_payload() -> dict[str, Any]:
    tools = [
        _tool("parva.get_today", "Return deterministic public today metadata.", {}, "public"),
        _tool("parva.convert_date", "Convert a BS or AD date using public calendar services.", {"date": "string", "direction": "string"}, "public"),
        _tool("parva.validate_date", "Validate a BS date.", {"bs_date": "string"}, "public"),
        _tool("parva.get_fiscal_period", "Return fiscal period for a BS or AD date.", {"date": "string"}, "public"),
        _tool("parva.evaluate_compliance_date", "Evaluate a working-day/compliance decision under a profile.", {"date": "string", "profile_id": "string"}, "public"),
        _tool("parva.evaluate_rule", "Execute a validated public RuleLang rule.", {"rule_id": "string", "input": "object"}, "public"),
        _tool("parva.explain_rule_execution", "Explain a public RuleLang execution trace.", {"rule_id": "string", "input": "object"}, "public"),
        _tool("parva.generate_evidence_packet", "Generate a public evidence packet for supported deterministic answers.", {"bs_date": "string"}, "public"),
        _tool("parva.trace_fact", "Trace a TimeGraph fact id.", {"fact_id": "string"}, "public"),
        _tool("parva.verify_temporal_claim", "Verify supported temporal claims without hallucinating.", {"claim": "string"}, "public"),
        _tool("parva.plan_schedule", "Plan a bounded public/demo schedule using RuleLang.", {"schedule_type": "string", "bs_year": "integer"}, "public"),
        _tool("parva.simulate_impact", "Run bounded public impact simulation.", {"change_set": "object"}, "public"),
        _tool("parva.check_human_review_required", "Evaluate human review gates for an agent decision.", {"decision": "object"}, "public"),
        _tool("parva.get_capabilities", "Return agent-safe capabilities.", {}, "public"),
    ]
    return {"tools": tools, "count": len(tools), "meta": _agent_meta()["meta"]}


def resolve_intent_payload(text: str, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise AgentError("text is required", code="INVALID_INPUT")
    lowered = text.lower()
    candidates: list[dict[str, Any]] = []

    def add_candidate(intent: str, tool: str) -> None:
        if not any(candidate["intent"] == intent for candidate in candidates):
            candidates.append({"intent": intent, "tool": tool})

    has_date_claim = BS_AD_CLAIM_RE.search(text) is not None
    if has_date_claim:
        add_candidate("verify_claim", "parva.verify_temporal_claim")
    elif "convert" in lowered:
        add_candidate("convert_date", "parva.convert_date")
    if "working day" in lowered or "holiday" in lowered:
        add_candidate("evaluate_working_day", "parva.evaluate_compliance_date")
    if "fiscal" in lowered:
        add_candidate("get_fiscal_period", "parva.get_fiscal_period")
    if "claim" in lowered or "maps to" in lowered or "official" in lowered:
        add_candidate("verify_claim", "parva.verify_temporal_claim")
    if "schedule" in lowered or "payroll" in lowered:
        add_candidate("plan_schedule", "parva.plan_schedule")
    if len(candidates) > 1:
        return {
            "intent": "unknown",
            "confidence": "low",
            "candidate_intents": [candidate["intent"] for candidate in candidates],
            "extracted_inputs": _extract_dates(text),
            "missing_inputs": ["target_operation"],
            "recommended_tool": None,
            "requires_confirmation": True,
            "warnings": ["temporal_intent_ambiguous"],
            "decision": _decision("review_required", True, ["TEMPORAL_INTENT_AMBIGUOUS", "HUMAN_REVIEW_REQUIRED"]),
            "meta": _agent_meta()["meta"],
        }
    if not candidates:
        return {
            "intent": "unknown",
            "confidence": "low",
            "candidate_intents": [],
            "extracted_inputs": _extract_dates(text),
            "missing_inputs": ["supported_temporal_intent"],
            "recommended_tool": None,
            "requires_confirmation": True,
            "warnings": ["unsupported_or_ambiguous_temporal_intent"],
            "decision": _decision("unsupported", True, ["CLAIM_UNSUPPORTED", "HUMAN_REVIEW_REQUIRED"]),
            "meta": _agent_meta()["meta"],
        }
    candidate = candidates[0]
    return {
        "intent": candidate["intent"],
        "confidence": "high",
        "candidate_intents": [candidate["intent"]],
        "extracted_inputs": {**_extract_dates(text), **(context or {})},
        "missing_inputs": [],
        "recommended_tool": candidate["tool"],
        "requires_confirmation": False,
        "warnings": [],
        "decision": _decision("approved", False, ["TEMPORAL_INTENT_RESOLVED", "TOOL_SELECTED"]),
        "meta": _agent_meta()["meta"],
    }


def verify_temporal_claim_payload(
    claim: str,
    *,
    context: dict[str, Any] | None = None,
    include_evidence: bool = False,
) -> dict[str, Any]:
    claim = (claim or "").strip()
    if not claim:
        raise AgentError("claim is required", code="INVALID_INPUT")
    if len(claim) > MAX_CLAIM_LENGTH:
        raise AgentError("claim is too long", code="INVALID_INPUT")
    context = context or {}
    match = BS_AD_CLAIM_RE.search(claim)
    if match:
        bs_date = match.group("bs")
        expected_ad = match.group("ad")
        year, month, day = _parse_bs_date(bs_date)
        actual_ad = bs_to_gregorian(year, month, day).isoformat()
        verified = actual_ad == expected_ad
        evidence_packet_id = None
        if include_evidence:
            packet = build_date_conversion_evidence_packet(bs_date=bs_date, trace_id=_new_trace_id())
            evidence_packet_id = packet["packet_id"]
        return {
            "claim": claim,
            "status": "verified" if verified else "false",
            "normalized_claim": {
                "claim_type": "date_conversion",
                "bs_date": bs_date,
                "expected_ad_date": expected_ad,
            },
            "result": {"bs": bs_date, "ad": actual_ad},
            "correction": None if verified else {"ad": actual_ad},
            "evidence": {
                "evidence_packet_id": evidence_packet_id,
                "fact_ids": [f"fact_bs_ad_{year:04d}_{month:02d}_{day:02d}"],
                "source_ids": ["parva_public_bs_ad_corpus"],
            },
            "decision": _decision(
                "approved" if verified else "review_required",
                not verified,
                ["CLAIM_VERIFIED"] if verified else ["CLAIM_FALSE", "HUMAN_REVIEW_REQUIRED"],
            ),
            "meta": _agent_meta()["meta"],
        }
    if "official" in claim.lower() and re.search(r"20[8-9]\d-\d{2}-\d{2}", claim):
        return _unsupported_claim(
            claim,
            "needs_review",
            ["CLAIM_NEEDS_REVIEW", "FUTURE_DATE_REVIEW_REQUIRED", "HUMAN_REVIEW_REQUIRED"],
            warning="future_or_official_claim_requires_source_review",
        )
    if "payroll" in claim.lower():
        dates = _extract_dates(claim)
        bs_date = dates.get("bs_date")
        if not bs_date:
            return _unsupported_claim(claim, "needs_review", ["CLAIM_NEEDS_REVIEW", "PAYROLL_ACTION_REQUIRES_REVIEW"])
        profile_id = str(context.get("profile_id") or "nepal_private_company_default")
        result = evaluate_date_payload(profile_id=profile_id, bs_date=bs_date, decision_intent="payroll")
        requires_review = bool(result.get("decision", {}).get("requires_human_review"))
        codes = ["CLAIM_VERIFIED"] if not requires_review else ["CLAIM_NEEDS_REVIEW", "PAYROLL_ACTION_REQUIRES_REVIEW"]
        return {
            "claim": claim,
            "status": "verified" if not requires_review else "needs_review",
            "normalized_claim": {"claim_type": "payroll_date_check", "bs_date": bs_date, "profile_id": profile_id},
            "result": result,
            "correction": None,
            "evidence": {"evidence_packet_id": None, "fact_ids": result.get("fact_ids", []), "source_ids": []},
            "decision": _decision("approved" if not requires_review else "review_required", requires_review, codes),
            "meta": _agent_meta(confidence=result.get("meta", {}).get("confidence", "source_backed"))["meta"],
        }
    return _unsupported_claim(claim, "unsupported", ["CLAIM_UNSUPPORTED"])


def plan_schedule_payload(
    *,
    schedule_type: str,
    bs_year: int,
    profile_id: str = "nepal_private_company_default",
    months: list[int] | None = None,
    include_evidence: bool = False,
) -> dict[str, Any]:
    if schedule_type not in {"payroll", "payroll_last_working_day"}:
        raise AgentError("only payroll_last_working_day schedule is supported in public preview", code="TOOL_UNAVAILABLE")
    months = months or list(range(1, 13))
    if len(months) > MAX_SCHEDULE_ITEMS:
        raise AgentError("schedule exceeds maximum item count", code="INVALID_INPUT")
    items: list[dict[str, Any]] = []
    for month in months:
        bs_month = f"{int(bs_year):04d}-{int(month):02d}"
        result = evaluate_rule_payload(
            SUPPORTED_SCHEDULE_RULE,
            {"bs_month": bs_month, "profile_id": profile_id},
            include_evidence=include_evidence,
        )
        items.append(
            {
                "period": bs_month,
                "date": result["output"].get("payroll_date"),
                "decision": result["decision"],
                "fact_ids": result.get("fact_ids", []),
                "evidence_packet_id": result.get("evidence_packet_id"),
                "warnings": result.get("warnings", []),
            }
        )
    summary = {
        status: sum(1 for item in items if item["decision"]["status"] == status)
        for status in AGENT_STATUSES
    }
    return {
        "schedule_id": f"sched_{uuid4().hex[:16]}",
        "schedule_type": "payroll",
        "profile_id": profile_id,
        "release_id": resolve_release_id(None),
        "items": items,
        "summary": summary,
        "decision": _decision(
            "review_required" if summary["review_required"] else "approved",
            bool(summary["review_required"]),
            ["PAYROLL_ACTION_REQUIRES_REVIEW", "HUMAN_REVIEW_REQUIRED"] if summary["review_required"] else ["TOOL_EXECUTED"],
        ),
        "meta": _agent_meta()["meta"],
    }


def explain_temporal_decision_payload(payload: dict[str, Any]) -> dict[str, Any]:
    explanation_type = str(payload.get("type") or "rule_execution")
    if explanation_type == "rule_execution":
        rule_id = str(payload.get("rule_id") or SUPPORTED_SCHEDULE_RULE)
        input_payload = payload.get("input") or {}
        result = explain_rule_payload(rule_id, input_payload)
        summary = result.get("explanation", {}).get("summary") or f"Rule {rule_id} returned {result['decision']['status']}."
        return {
            "explanation": summary[:MAX_EXPLANATION_CHARS],
            "trace": result.get("trace"),
            "sources": [],
            "decision": result.get("decision"),
            "evidence": {"fact_ids": result.get("fact_ids", []), "evidence_packet_id": None, "source_ids": []},
            "meta": result.get("meta") or _agent_meta()["meta"],
        }
    if explanation_type == "claim":
        result = verify_temporal_claim_payload(str(payload.get("claim") or ""))
        return {
            "explanation": f"Claim status is {result['status']}.",
            "trace": {"steps": []},
            "sources": result.get("evidence", {}).get("source_ids", []),
            "decision": result["decision"],
            "evidence": result["evidence"],
            "meta": result["meta"],
        }
    raise AgentError("unsupported explanation type", code="TOOL_UNAVAILABLE")


def check_human_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    reason_codes = list(payload.get("reason_codes") or payload.get("decision", {}).get("reason_codes") or [])
    use_case = str(payload.get("use_case") or "").lower()
    confidence = str(payload.get("confidence") or payload.get("meta", {}).get("confidence") or "unknown")
    requires = bool(payload.get("requires_human_review") or payload.get("decision", {}).get("requires_human_review"))
    if confidence in {"unknown", "unsupported", "research_preview", "fixture_only", "disputed"}:
        requires = True
        reason_codes.append("SOURCE_CONFIDENCE_TOO_LOW")
    if use_case in {"payroll", "banking", "legal", "fiscal"}:
        requires = True
        reason_codes.append({
            "payroll": "PAYROLL_ACTION_REQUIRES_REVIEW",
            "banking": "BANKING_ACTION_REQUIRES_REVIEW",
            "legal": "LEGAL_ACTION_NOT_AUTHORIZED",
            "fiscal": "HUMAN_REVIEW_REQUIRED",
        }[use_case])
    status = "review_required" if requires else "approved"
    return {
        "requires_human_review": requires,
        "decision": _decision(status, requires, _dedupe(reason_codes or ["TOOL_EXECUTED"])),
        "meta": _agent_meta(confidence=confidence if confidence != "unknown" else "source_backed")["meta"],
    }


def draft_rule_payload(text: str, *, profile_id: str = "nepal_private_company_default") -> dict[str, Any]:
    text = (text or "").strip().lower()
    if "next working day" in text and ("holiday" in text or "exam" in text):
        rule = {
            "rule_id": "draft_next_working_day_if_holiday",
            "version": "0.1.0",
            "label": "Draft next working day if holiday",
            "description": "Draft rule. If a date is a holiday, move to the next working day.",
            "status": "fixture_only",
            "profile_id": profile_id,
            "inputs": {"date": {"type": "date", "required": True}},
            "outputs": {"working_date": {"type": "date"}},
            "steps": [
                {
                    "if": {
                        "condition": {"call": "is_holiday", "args": {"date": "$input.date", "profile_id": "$rule.profile_id"}},
                        "then": [
                            {
                                "return": {
                                    "working_date": {
                                        "call": "next_working_day",
                                        "args": {"date": "$input.date", "profile_id": "$rule.profile_id"},
                                    }
                                }
                            }
                        ],
                        "else": [{"return": {"working_date": "$input.date"}}],
                    }
                }
            ],
            "risk_policy": {
                "require_confidence_at_least": "source_backed",
                "block_research_preview": True,
                "block_disputed_facts": True,
                "unsupported_result_action": "human_review_required",
                "future_date_action": "human_review_required",
            },
            "claim_boundary": "enterprise_decision_support_not_legal_authority",
            "tests": [],
        }
        validation = validate_rule_payload(rule)
        return {
            "draft_rule": rule,
            "validation": validation,
            "decision": _decision("review_required", True, ["RULE_DRAFT_REQUIRES_VALIDATION", "HUMAN_REVIEW_REQUIRED"]),
            "meta": _agent_meta()["meta"],
        }
    return {
        "draft_rule": None,
        "validation": {"valid": False, "errors": ["unsupported_or_ambiguous_rule_request"]},
        "decision": _decision("unsupported", True, ["RULE_DRAFT_REQUIRES_VALIDATION", "HUMAN_REVIEW_REQUIRED"]),
        "meta": _agent_meta()["meta"],
    }


def run_tool_payload(tool_name: str, input_payload: dict[str, Any]) -> dict[str, Any]:
    tools = {tool["name"] for tool in agent_tools_payload()["tools"]}
    if tool_name not in tools:
        raise AgentError(f"tool is unavailable: {tool_name}", code="TOOL_UNAVAILABLE", status_code=404)
    if tool_name == "parva.get_capabilities":
        result = agent_capabilities_payload()
    elif tool_name == "parva.verify_temporal_claim":
        result = verify_temporal_claim_payload(str(input_payload.get("claim") or ""), context=input_payload.get("context") or {})
    elif tool_name == "parva.plan_schedule":
        result = plan_schedule_payload(
            schedule_type=str(input_payload.get("schedule_type") or "payroll"),
            bs_year=int(input_payload.get("bs_year")),
            profile_id=str(input_payload.get("profile_id") or "nepal_private_company_default"),
            months=input_payload.get("months"),
        )
    elif tool_name == "parva.evaluate_rule":
        result = evaluate_rule_payload(str(input_payload.get("rule_id")), input_payload.get("input") or {})
    elif tool_name == "parva.explain_rule_execution":
        result = explain_temporal_decision_payload({"type": "rule_execution", **input_payload})
    elif tool_name == "parva.simulate_impact":
        result = simulate_change_set_payload(input_payload.get("change_set") or {})
    elif tool_name == "parva.trace_fact":
        result = trace_fact_payload(str(input_payload.get("fact_id") or ""))
    elif tool_name == "parva.generate_evidence_packet":
        result = build_date_conversion_evidence_packet(
            bs_date=input_payload.get("bs_date"),
            ad_date=input_payload.get("ad_date"),
            trace_id=_new_trace_id(),
        )
    elif tool_name == "parva.get_fiscal_period":
        result = fiscal_period_payload(
            profile_id=str(input_payload.get("profile_id") or "nepal_private_company_default"),
            bs_date=input_payload.get("bs_date"),
            ad_date=input_payload.get("ad_date"),
        )
    elif tool_name == "parva.validate_date":
        if not input_payload.get("bs_date"):
            raise AgentError("bs_date is required", code="INVALID_INPUT")
        year, month, day = _parse_bs_date(str(input_payload["bs_date"]))
        bs_to_gregorian(year, month, day)
        result = {
            "valid": True,
            "bs_date": f"{year:04d}-{month:02d}-{day:02d}",
            "decision": _decision("approved", False, ["INPUT_VALIDATED"]),
        }
    elif tool_name == "parva.evaluate_compliance_date":
        result = evaluate_date_payload(
            profile_id=str(input_payload.get("profile_id") or "nepal_private_company_default"),
            bs_date=input_payload.get("bs_date"),
            ad_date=input_payload.get("ad_date"),
            decision_intent=str(input_payload.get("decision_intent") or "general"),
        )
    elif tool_name == "parva.convert_date":
        result = _convert_tool(input_payload)
    elif tool_name == "parva.check_human_review_required":
        result = check_human_review_payload(input_payload)
    elif tool_name == "parva.get_today":
        result = build_conversion_payload(parse_iso_date(now_utc()[:10]))
    else:
        raise AgentError(f"tool is not implemented in public preview: {tool_name}", code="TOOL_UNAVAILABLE", status_code=404)
    return {
        "tool_name": tool_name,
        "result": result,
        "decision": _decision("approved", False, ["TOOL_EXECUTED"]),
        "meta": _agent_meta()["meta"],
    }


def agent_manifest_payload() -> dict[str, Any]:
    return {
        "manifest_version": "parva-agent-tools-0.1.0",
        "name": "Parva agent-safe temporal tools",
        "tools": agent_tools_payload()["tools"],
        "authentication": "public demo endpoints are unauthenticated; private deployments may require an API token",
        "risk_behavior": "tools return decision status, reason codes, evidence, confidence, warnings, and claim boundary",
        "claim_boundary": AGENT_CLAIM_BOUNDARY,
    }


def _convert_tool(input_payload: dict[str, Any]) -> dict[str, Any]:
    if input_payload.get("bs_date"):
        year, month, day = _parse_bs_date(str(input_payload["bs_date"]))
        return build_bs_to_gregorian_payload(year, month, day)
    if input_payload.get("ad_date"):
        return build_conversion_payload(parse_iso_date(str(input_payload["ad_date"])))
    raise AgentError("bs_date or ad_date is required", code="INVALID_INPUT")


def _unsupported_claim(claim: str, status: str, codes: list[str], *, warning: str | None = None) -> dict[str, Any]:
    return {
        "claim": claim,
        "status": status,
        "normalized_claim": {},
        "result": {},
        "correction": None,
        "evidence": {"evidence_packet_id": None, "fact_ids": [], "source_ids": []},
        "decision": _decision("review_required" if status == "needs_review" else "unsupported", status != "unsupported", codes),
        "meta": _agent_meta(warnings=[warning] if warning else [])["meta"],
    }


def _tool(name: str, description: str, input_schema: dict[str, Any], mode: str) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "input_schema": {"type": "object", "properties": {key: {"type": value} for key, value in input_schema.items()}},
        "output_schema": {
            "type": "object",
            "required": ["result", "decision", "meta"],
            "properties": {
                "result": {"type": "object"},
                "decision": {"type": "object"},
                "meta": {"type": "object"},
                "evidence": {"type": "object"},
            },
        },
        "supported_mode": mode,
        "risk_behavior": "review_required_or_unsupported_when_confidence_or_scope_is_insufficient",
        "evidence_behavior": "fact_ids_and_evidence_packet_ids_are_preserved_when_available",
        "claim_boundary": AGENT_CLAIM_BOUNDARY,
    }


def _parse_bs_date(value: str) -> tuple[int, int, int]:
    parts = value.split("-")
    if len(parts) != 3:
        raise AgentError("BS date must be YYYY-MM-DD", code="INVALID_INPUT")
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as exc:
        raise AgentError("BS date must be YYYY-MM-DD", code="INVALID_INPUT") from exc


def _extract_dates(text: str) -> dict[str, Any]:
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    result: dict[str, Any] = {}
    if dates:
        result["date"] = dates[0]
        if "bs" in text.lower():
            result["bs_date"] = dates[0]
        if len(dates) > 1:
            result["comparison_date"] = dates[1]
    return result


def _decision(status: str, requires_review: bool, reason_codes: list[str]) -> dict[str, Any]:
    return {
        "status": status,
        "requires_human_review": requires_review,
        "reason_codes": _dedupe(reason_codes),
    }


def _agent_meta(*, confidence: str = "source_backed", warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "meta": {
            "release_id": resolve_release_id(None),
            "confidence": confidence,
            "claim_boundary": AGENT_CLAIM_BOUNDARY,
            "warnings": _dedupe([*(warnings or []), "agent_outputs_are_decision_support_not_legal_authority"]),
            "trace_id": _new_trace_id(),
            "data_mode": "public",
        }
    }


def _new_trace_id() -> str:
    return f"agent_trace_{uuid4().hex[:16]}"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
