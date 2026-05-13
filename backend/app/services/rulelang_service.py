"""Safe structured RuleLang execution for institutional temporal rules."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    get_bs_month_name,
    gregorian_to_bs,
)
from app.core.source_metadata import (
    COMPLIANCE_BOUNDARY,
    ENTERPRISE_COMPLIANCE_PROFILES,
    PUBLIC_DATA_VERSION,
    PUBLIC_RELEASE_ID,
    build_bs_claim_meta,
)
from app.services.compliance_service import (
    PROFILES,
    add_working_days_payload,
    evaluate_date_payload,
    fiscal_period_payload,
    month_closing_day_payload,
    next_working_day_payload,
    previous_working_day_payload,
)
from app.services.enterprise_calendar_service import parse_ad_date, parse_bs_date
from app.services.timegraph_service import build_public_timegraph, trace_url_for_fact
from app.services.trust_infrastructure_service import active_release_id
from app.timegraph.fact_ids import (
    ad_bs_fact_id,
    bs_ad_fact_id,
    fiscal_period_fact_id,
    month_length_fact_id,
    weekday_fact_id,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_RULE_DIR = PROJECT_ROOT / "data" / "rules" / "public"
PRIVATE_RULE_DIR = PROJECT_ROOT / "data" / "rules" / "private"
RULELANG_CLAIM_BOUNDARY = COMPLIANCE_BOUNDARY
DEFAULT_RULELANG_MODE = "public"
DEFAULT_LOOP_MAX_ITERATIONS = 32
ABSOLUTE_LOOP_MAX_ITERATIONS = 366
MAX_STEPS = 128
MAX_TRACE_STEPS = 256
MAX_CONDITION_DEPTH = 16
MAX_INPUT_BYTES = 8192
RULE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]{2,95}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
VARIABLE_RE = re.compile(r"^\$(input|var|rule)\.[a-zA-Z_][a-zA-Z0-9_]*$")

RULE_STATUSES = {
    "public_preview",
    "enterprise_preview",
    "active",
    "deprecated",
    "private",
    "fixture_only",
}
PUBLIC_RULE_STATUSES = {"public_preview", "enterprise_preview", "active", "deprecated", "fixture_only"}
INPUT_TYPES = {"bs_date", "ad_date", "date", "bs_month", "ad_month", "profile_id", "integer", "string", "boolean", "enum"}
OUTPUT_TYPES = {"date", "object", "string", "integer", "boolean", "fiscal_period"}
STEP_TYPES = {"set", "if", "while", "return", "call"}
OPERATORS = {
    "and",
    "or",
    "not",
    "equals",
    "not_equals",
    "greater_than",
    "less_than",
    "greater_or_equal",
    "less_or_equal",
    "in",
    "not_in",
}
FORBIDDEN_FUNCTIONS = {
    "eval",
    "exec",
    "shell",
    "subprocess",
    "import",
    "open",
    "read_file",
    "write_file",
    "network",
    "http",
    "env",
    "os",
    "os.environ",
}
CONFIDENCE_ORDER = {
    "unknown": 0,
    "unsupported": 0,
    "fixture": 1,
    "research_preview": 1,
    "calculated": 2,
    "source_backed": 3,
    "official_verified": 4,
}


class RuleLangError(ValueError):
    """Raised when a RuleLang rule cannot be validated or executed safely."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "RULE_EXECUTION_FAILED",
        status_code: int = 400,
        details: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details or [message]


@dataclass
class FunctionOutcome:
    value: Any
    function: str
    arguments: dict[str, Any]
    fact_ids: list[str] = field(default_factory=list)
    confidence: str = "source_backed"
    warnings: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    trace_url: str | None = None


@dataclass
class RuleExecutionContext:
    rule: dict[str, Any]
    original_input: dict[str, Any]
    input: dict[str, Any]
    release_id: str
    trace_id: str
    variables: dict[str, Any] = field(default_factory=dict)
    trace_steps: list[dict[str, Any]] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fact_ids: list[str] = field(default_factory=list)
    confidences: list[str] = field(default_factory=list)
    step_counter: int = 0


def rulelang_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "parva_rulelang",
        "status": "public_preview",
        "rulelang_mode": rulelang_mode(),
        "publication_status": "computed_prediction_not_official",
        "claim_boundary": RULELANG_CLAIM_BOUNDARY,
        "public_surfaces": [
            "capabilities",
            "public_rule_registry",
            "rule_validation",
            "bounded_rule_execution",
            "rule_explanation_trace",
            "rule_test_runner",
        ],
        "rule_statuses": sorted(RULE_STATUSES),
        "public_rule_statuses": sorted(PUBLIC_RULE_STATUSES),
        "step_types": sorted(STEP_TYPES),
        "operators": sorted(OPERATORS),
        "input_types": sorted(INPUT_TYPES),
        "builtins": sorted(ALLOWED_FUNCTIONS),
        "safety_limits": {
            "max_steps": MAX_STEPS,
            "default_loop_max_iterations": DEFAULT_LOOP_MAX_ITERATIONS,
            "absolute_loop_max_iterations": ABSOLUTE_LOOP_MAX_ITERATIONS,
            "max_trace_steps": MAX_TRACE_STEPS,
            "max_condition_depth": MAX_CONDITION_DEPTH,
            "max_input_bytes": MAX_INPUT_BYTES,
        },
        "not_allowed": [
            "eval",
            "exec",
            "shell_commands",
            "arbitrary_imports",
            "filesystem_access",
            "network_access",
            "environment_access",
            "unbounded_loops",
            "private_rules_in_public_mode",
        ],
        "not_claimed": [
            "legal_authority",
            "tax_authority",
            "banking_contract_final_authority",
            "official_calendar_publication",
        ],
        "reason_codes": REASON_CODE_CATALOG,
    }


def rulelang_mode() -> str:
    mode = os.getenv("PARVA_RULELANG_MODE", DEFAULT_RULELANG_MODE).strip().lower()
    return mode or DEFAULT_RULELANG_MODE


def private_rules_enabled() -> bool:
    return os.getenv("PARVA_ENABLE_PRIVATE_RULES", "0").strip().lower() in {"1", "true", "yes"}


def list_rules_payload(*, include_private: bool = False) -> dict[str, Any]:
    rules = [
        _public_rule_summary(rule)
        for rule in load_rules(include_private=include_private)
    ]
    return {
        "rules": rules,
        "count": len(rules),
        "meta": _rulelang_meta(
            confidence="source_backed",
            warnings=["public_rule_registry_is_preview_decision_support"],
        ),
    }


def get_rule_payload(rule_id: str, *, include_private: bool = False) -> dict[str, Any]:
    rule = get_rule_definition(rule_id, include_private=include_private)
    return {
        "rule": _redact_rule_for_public(rule),
        "validation": validate_rule_payload(rule),
        "meta": _rulelang_meta(confidence="source_backed", warnings=[]),
    }


def validate_rule_payload(rule: dict[str, Any]) -> dict[str, Any]:
    issues = validate_rule(rule)
    return {
        "valid": not issues,
        "reason_codes": ["RULE_VALIDATED"] if not issues else ["RULE_VALIDATION_FAILED"],
        "errors": issues,
        "meta": _rulelang_meta(confidence="source_backed", warnings=[]),
    }


def evaluate_rule_payload(
    rule_id: str,
    input_payload: dict[str, Any],
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    include_private: bool = False,
    include_evidence: bool = False,
) -> dict[str, Any]:
    rule = get_rule_definition(rule_id, include_private=include_private)
    return execute_rule(
        rule,
        input_payload,
        release_id=release_id,
        trace_id=trace_id,
        include_evidence=include_evidence,
    )


def evaluate_custom_rule_payload(
    rule: dict[str, Any],
    input_payload: dict[str, Any],
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    include_evidence: bool = False,
) -> dict[str, Any]:
    return execute_rule(
        rule,
        input_payload,
        release_id=release_id,
        trace_id=trace_id,
        include_evidence=include_evidence,
    )


def explain_rule_payload(
    rule_id: str,
    input_payload: dict[str, Any],
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    include_private: bool = False,
) -> dict[str, Any]:
    result = evaluate_rule_payload(
        rule_id,
        input_payload,
        release_id=release_id,
        trace_id=trace_id,
        include_private=include_private,
    )
    return {
        "rule_id": result["rule_id"],
        "rule_version": result["rule_version"],
        "decision": result["decision"],
        "output": result["output"],
        "trace": result["trace"],
        "fact_ids": result["fact_ids"],
        "explanation": {
            "summary": _explanation_summary(result),
            "claim_boundary": result["meta"]["claim_boundary"],
            "warnings": result["meta"]["warnings"],
        },
        "meta": result["meta"],
    }


def test_rule_payload(
    rule_id: str,
    *,
    include_private: bool = False,
    release_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    rule = get_rule_definition(rule_id, include_private=include_private)
    return run_rule_tests(rule, release_id=release_id, trace_id=trace_id)


def run_all_rule_tests_payload() -> dict[str, Any]:
    rules = load_rules(include_private=False)
    results = [run_rule_tests(rule) for rule in rules]
    failed = sum(result["summary"]["failed"] for result in results)
    return {
        "ok": failed == 0,
        "rule_count": len(rules),
        "results": results,
        "meta": _rulelang_meta(confidence="source_backed", warnings=[]),
    }


def execute_rule(
    rule: dict[str, Any],
    input_payload: dict[str, Any],
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    include_evidence: bool = False,
) -> dict[str, Any]:
    issues = validate_rule(rule)
    if issues:
        raise RuleLangError("Rule validation failed.", code="RULE_VALIDATION_FAILED", details=issues)
    _assert_public_rule_allowed(rule)
    normalized_input = _normalize_input_payload(rule, input_payload)
    selected_release = release_id or active_release_id()
    context = RuleExecutionContext(
        rule=rule,
        original_input=input_payload,
        input=normalized_input,
        release_id=selected_release,
        trace_id=trace_id or f"rule_trace_{uuid4().hex[:16]}",
    )
    context.reason_codes.extend(["RULE_VALIDATED", "INPUT_VALIDATED"])
    try:
        output = _execute_steps(context, rule["steps"])
        if output is None:
            raise RuleLangError("Rule completed without a return step.", code="RULE_EXECUTION_FAILED")
        decision = _decision_for_context(context)
    except RuleLangError as exc:
        context.reason_codes.extend([exc.code, "RULE_EXECUTION_FAILED"])
        context.warnings.extend(exc.details)
        output = {}
        decision = {
            "status": "failed",
            "requires_human_review": True,
            "reason_codes": _dedupe(context.reason_codes),
        }

    evidence_packet_id = None
    if include_evidence and decision["status"] != "failed":
        try:
            from app.services.trust_infrastructure_service import (  # noqa: PLC0415
                build_evidence_packet,
            )

            packet = build_evidence_packet(
                packet_type="rule_execution",
                input_payload={
                    "rule_id": rule["rule_id"],
                    "input": input_payload,
                },
                result={
                    "rule_id": rule["rule_id"],
                    "rule_version": rule["version"],
                    "profile_id": _profile_id_for_rule(rule, normalized_input),
                    "input": normalized_input,
                    "output": output,
                    "decision": decision,
                    "trace": {"steps": context.trace_steps},
                    "fact_ids": _dedupe(context.fact_ids),
                    "meta": _rulelang_meta(
                        release_id=selected_release,
                        trace_id=context.trace_id,
                        confidence=_lowest_confidence(context.confidences),
                        warnings=context.warnings,
                    ),
                },
                release_id=selected_release,
                trace_id=context.trace_id,
            )
            evidence_packet_id = packet["packet_id"]
        except Exception as exc:  # noqa: BLE001
            context.warnings.append(f"rule_evidence_packet_unavailable: {exc}")

    return {
        "rule_id": rule["rule_id"],
        "rule_version": rule["version"],
        "profile_id": _profile_id_for_rule(rule, normalized_input),
        "input": normalized_input,
        "output": output,
        "decision": decision,
        "trace": {
            "steps": context.trace_steps,
            "bounded": True,
            "max_trace_steps": MAX_TRACE_STEPS,
        },
        "fact_ids": _dedupe(context.fact_ids),
        "evidence_packet_id": evidence_packet_id,
        "release_id": selected_release,
        "trace_id": context.trace_id,
        "confidence": _lowest_confidence(context.confidences),
        "claim_boundary": RULELANG_CLAIM_BOUNDARY,
        "warnings": _dedupe(context.warnings),
        "meta": _rulelang_meta(
            release_id=selected_release,
            trace_id=context.trace_id,
            confidence=_lowest_confidence(context.confidences),
            warnings=context.warnings,
        ),
    }


def load_rules(*, include_private: bool = False) -> list[dict[str, Any]]:
    rules = _load_rules_from_dir(PUBLIC_RULE_DIR)
    if include_private and private_rules_enabled():
        rules.extend(_load_rules_from_dir(PRIVATE_RULE_DIR))
    return sorted(rules, key=lambda item: str(item.get("rule_id")))


def get_rule_definition(rule_id: str, *, include_private: bool = False) -> dict[str, Any]:
    for rule in load_rules(include_private=include_private):
        if rule.get("rule_id") == rule_id:
            return rule
    raise RuleLangError(f"Unknown rule id: {rule_id}", code="RULE_NOT_FOUND", status_code=404)


def validate_rule(rule: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(rule, dict):
        return ["rule must be an object"]
    required = ["rule_id", "version", "label", "description", "status", "inputs", "outputs", "steps", "risk_policy", "claim_boundary"]
    for field_name in required:
        if field_name not in rule:
            issues.append(f"missing required field: {field_name}")
    if issues:
        return issues
    rule_id = str(rule.get("rule_id") or "")
    if not RULE_ID_RE.match(rule_id):
        issues.append("rule_id must be a stable lowercase slug")
    if not SEMVER_RE.match(str(rule.get("version") or "")):
        issues.append("version must be semver-like, for example 1.0.0")
    if rule.get("status") not in RULE_STATUSES:
        issues.append("status is not supported")
    if rule.get("claim_boundary") != RULELANG_CLAIM_BOUNDARY:
        issues.append(f"claim_boundary must be {RULELANG_CLAIM_BOUNDARY}")
    _validate_inputs(rule.get("inputs"), issues)
    _validate_outputs(rule.get("outputs"), issues)
    _validate_risk_policy(rule.get("risk_policy"), issues)
    steps = rule.get("steps")
    if not isinstance(steps, list) or not steps:
        issues.append("steps must be a non-empty list")
    else:
        _validate_steps(steps, issues, path="steps")
    tests = rule.get("tests", [])
    if tests is not None and not isinstance(tests, list):
        issues.append("tests must be a list when provided")
    return issues


def run_rule_tests(
    rule: dict[str, Any],
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    tests = rule.get("tests") or []
    results: list[dict[str, Any]] = []
    for test_case in tests:
        name = str(test_case.get("name") or "unnamed")
        try:
            result = execute_rule(
                rule,
                test_case.get("input") or {},
                release_id=release_id,
                trace_id=trace_id,
            )
            assertions = _evaluate_expectations(result, test_case.get("expect") or {})
            passed = all(assertion["passed"] for assertion in assertions)
            results.append(
                {
                    "name": name,
                    "passed": passed,
                    "assertions": assertions,
                    "decision_status": result["decision"]["status"],
                    "reason_codes": result["decision"]["reason_codes"],
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "name": name,
                    "passed": False,
                    "assertions": [],
                    "error": str(exc),
                }
            )
    failed = sum(1 for row in results if not row["passed"])
    return {
        "rule_id": rule.get("rule_id"),
        "rule_version": rule.get("version"),
        "summary": {
            "total": len(results),
            "passed": len(results) - failed,
            "failed": failed,
        },
        "results": results,
        "meta": _rulelang_meta(confidence="source_backed", warnings=[]),
    }


def _execute_steps(context: RuleExecutionContext, steps: list[dict[str, Any]]) -> Any:
    for step in steps:
        context.step_counter += 1
        if context.step_counter > MAX_STEPS:
            raise RuleLangError("Rule exceeded max step count.", code="MAX_ITERATIONS_EXCEEDED")
        if "set" in step:
            payload = step["set"]
            name = str(payload.get("name") or "")
            if not name:
                raise RuleLangError("set step requires name", code="RULE_EXECUTION_FAILED")
            context.variables[name] = _eval_value(context, payload.get("value"))
            _append_trace(
                context,
                operation="set",
                result={name: _safe_trace_value(context.variables[name])},
                reason_codes=["FUNCTION_EXECUTED"],
            )
            continue
        if "call" in step:
            payload = step["call"]
            args = {
                str(key): _eval_value(context, raw_value)
                for key, raw_value in (payload.get("args") or {}).items()
            }
            outcome = _call_function(context, str(payload.get("function") or ""), args)
            if payload.get("save_as"):
                context.variables[str(payload["save_as"])] = outcome.value
            continue
        if "if" in step:
            payload = step["if"]
            branch = payload.get("then") if _eval_condition(context, payload.get("condition")) else payload.get("else", [])
            returned = _execute_steps(context, list(branch or []))
            if returned is not None:
                return returned
            continue
        if "while" in step:
            payload = step["while"]
            max_iterations = _bounded_loop_iterations(payload.get("max_iterations"))
            iterations = 0
            while _eval_condition(context, payload.get("condition")):
                iterations += 1
                if iterations > max_iterations:
                    raise RuleLangError("while loop exceeded max_iterations", code="MAX_ITERATIONS_EXCEEDED")
                returned = _execute_steps(context, list(payload.get("do") or []))
                if returned is not None:
                    return returned
            _append_trace(
                context,
                operation="while",
                result={"iterations": iterations, "max_iterations": max_iterations},
                reason_codes=["FUNCTION_EXECUTED"],
            )
            continue
        if "return" in step:
            payload = step["return"]
            result = {str(key): _eval_value(context, value) for key, value in payload.items()}
            _append_trace(
                context,
                operation="return",
                result=_safe_trace_value(result),
                reason_codes=["FUNCTION_EXECUTED"],
            )
            return result
    return None


def _eval_value(context: RuleExecutionContext, value: Any) -> Any:
    if isinstance(value, str) and value.startswith("$"):
        return _resolve_variable(context, value)
    if isinstance(value, dict):
        if "call" in value:
            function_name = str(value.get("call"))
            args = {
                str(key): _eval_value(context, raw_value)
                for key, raw_value in (value.get("args") or {}).items()
            }
            return _call_function(context, function_name, args).value
        return {str(key): _eval_value(context, raw_value) for key, raw_value in value.items()}
    if isinstance(value, list):
        return [_eval_value(context, item) for item in value]
    return value


def _eval_condition(context: RuleExecutionContext, value: Any, *, depth: int = 0) -> bool:
    if depth > MAX_CONDITION_DEPTH:
        raise RuleLangError("condition depth exceeds limit", code="RULE_EXECUTION_FAILED")
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        if "call" in value:
            return bool(_eval_value(context, value))
        if "and" in value:
            return all(_eval_condition(context, item, depth=depth + 1) for item in list(value["and"]))
        if "or" in value:
            return any(_eval_condition(context, item, depth=depth + 1) for item in list(value["or"]))
        if "not" in value:
            return not _eval_condition(context, value["not"], depth=depth + 1)
        for operator in OPERATORS - {"and", "or", "not"}:
            if operator in value:
                left, right = _condition_pair(context, value[operator])
                return _compare_values(operator, left, right)
    return bool(_eval_value(context, value))


def _condition_pair(context: RuleExecutionContext, payload: Any) -> tuple[Any, Any]:
    if not isinstance(payload, list) or len(payload) != 2:
        raise RuleLangError("comparison operators require two-item lists", code="RULE_EXECUTION_FAILED")
    return _eval_value(context, payload[0]), _eval_value(context, payload[1])


def _compare_values(operator: str, left: Any, right: Any) -> bool:
    if operator == "equals":
        return left == right
    if operator == "not_equals":
        return left != right
    if operator == "greater_than":
        return left > right
    if operator == "less_than":
        return left < right
    if operator == "greater_or_equal":
        return left >= right
    if operator == "less_or_equal":
        return left <= right
    if operator == "in":
        return left in right
    if operator == "not_in":
        return left not in right
    raise RuleLangError(f"unsupported operator: {operator}", code="RULE_EXECUTION_FAILED")


def _call_function(context: RuleExecutionContext, function_name: str, args: dict[str, Any]) -> FunctionOutcome:
    if function_name in FORBIDDEN_FUNCTIONS:
        raise RuleLangError(
            f"Function is forbidden: {function_name}",
            code="FUNCTION_UNSUPPORTED",
        )
    function = ALLOWED_FUNCTIONS.get(function_name)
    if function is None:
        raise RuleLangError(f"Unsupported RuleLang function: {function_name}", code="FUNCTION_UNSUPPORTED")
    try:
        outcome = function(context, args)
    except RuleLangError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RuleLangError(str(exc), code="RULE_EXECUTION_FAILED") from exc
    context.fact_ids.extend(outcome.fact_ids)
    context.warnings.extend(outcome.warnings)
    context.reason_codes.extend(outcome.reason_codes or ["FUNCTION_EXECUTED"])
    context.confidences.append(outcome.confidence)
    _append_trace(
        context,
        operation="call",
        function=function_name,
        arguments=args,
        result=outcome.value,
        fact_ids=outcome.fact_ids,
        confidence=outcome.confidence,
        warnings=outcome.warnings,
        reason_codes=outcome.reason_codes or ["FUNCTION_EXECUTED"],
    )
    return outcome


def _builtin_convert_bs_to_ad(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    bs_date = _date_from_arg(args.get("bs_date") or args.get("date"))
    year, month, day = _parse_bs_tuple(bs_date["bs"])
    ad = bs_to_gregorian(year, month, day)
    meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_convert_bs_to_ad")
    fact_id = bs_ad_fact_id(year, month, day)
    return FunctionOutcome(
        value={"bs": bs_date["bs"], "ad": ad.isoformat()},
        function="convert_bs_to_ad",
        arguments=args,
        fact_ids=[fact_id, fiscal_period_fact_id(year, month, day)],
        confidence=str(meta["confidence"]),
        warnings=list(meta.get("warnings", [])),
        reason_codes=["FUNCTION_EXECUTED"],
        trace_url=trace_url_for_fact(fact_id),
    )


def _builtin_convert_ad_to_bs(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    ad_raw = args.get("ad_date") or args.get("date")
    ad = _ad_date_from_arg(ad_raw)
    year, month, day = gregorian_to_bs(ad)
    meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_convert_ad_to_bs")
    fact_id = ad_bs_fact_id(ad)
    return FunctionOutcome(
        value={"bs": _format_bs(year, month, day), "ad": ad.isoformat()},
        function="convert_ad_to_bs",
        arguments=args,
        fact_ids=[fact_id, bs_ad_fact_id(year, month, day), fiscal_period_fact_id(year, month, day)],
        confidence=str(meta["confidence"]),
        warnings=list(meta.get("warnings", [])),
        reason_codes=["FUNCTION_EXECUTED"],
        trace_url=trace_url_for_fact(fact_id),
    )


def _builtin_validate_date(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    try:
        date_block = _date_from_arg(args.get("date") or args)
        year, month, day = _parse_bs_tuple(date_block["bs"])
        meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_validate_date")
        value = {"valid": True, "date": date_block}
        reason_codes = ["FUNCTION_EXECUTED"]
        warnings = list(meta.get("warnings", []))
        confidence = str(meta["confidence"])
        fact_ids = [bs_ad_fact_id(year, month, day)]
    except Exception as exc:  # noqa: BLE001
        value = {"valid": False, "error": str(exc)}
        reason_codes = ["INVALID_INPUT"]
        warnings = [str(exc)]
        confidence = "unsupported"
        fact_ids = []
    return FunctionOutcome(
        value=value,
        function="validate_date",
        arguments=args,
        fact_ids=fact_ids,
        confidence=confidence,
        warnings=warnings,
        reason_codes=reason_codes,
    )


def _builtin_get_weekday(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    ad = parse_ad_date(date_block["ad"])
    return FunctionOutcome(
        value=ad.strftime("%A").upper(),
        function="get_weekday",
        arguments=args,
        fact_ids=[weekday_fact_id(ad)],
        confidence="calculated",
        warnings=["weekday_is_computed_from_gregorian_calendar"],
        reason_codes=["FUNCTION_EXECUTED"],
    )


def _builtin_is_weekend(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = evaluate_date_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        decision_intent="general",
        trace_id=context.trace_id,
    )
    value = not bool(result["decision"]["is_working_day"])
    return _compliance_outcome("is_weekend", args, result, value=value)


def _builtin_is_working_day(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = evaluate_date_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        decision_intent=str(args.get("decision_intent") or "general"),
        trace_id=context.trace_id,
    )
    return _compliance_outcome(
        "is_working_day",
        args,
        result,
        value=bool(result["decision"]["is_working_day"]),
    )


def _builtin_is_holiday(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = evaluate_date_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        decision_intent="general",
        trace_id=context.trace_id,
    )
    holiday = result["decision"].get("holiday")
    return _compliance_outcome("is_holiday", args, result, value=bool(holiday))


def _builtin_next_working_day(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = next_working_day_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        include_input=bool(args.get("include_input", False)),
        trace_id=context.trace_id,
    )
    return _compliance_outcome(
        "next_working_day",
        args,
        result,
        value=result["date"],
        reason_codes=["NEXT_WORKING_DAY_SELECTED"],
    )


def _builtin_previous_working_day(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = previous_working_day_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        include_input=bool(args.get("include_input", False)),
        trace_id=context.trace_id,
    )
    return _compliance_outcome(
        "previous_working_day",
        args,
        result,
        value=result["date"],
        reason_codes=["PREVIOUS_WORKING_DAY_SELECTED"],
    )


def _builtin_add_days(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    days = int(args.get("days") or 0)
    ad = parse_ad_date(date_block["ad"]) + timedelta(days=days)
    year, month, day = gregorian_to_bs(ad)
    meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_add_days")
    return FunctionOutcome(
        value={"bs": _format_bs(year, month, day), "ad": ad.isoformat()},
        function="add_days",
        arguments=args,
        fact_ids=[ad_bs_fact_id(ad), bs_ad_fact_id(year, month, day)],
        confidence=str(meta["confidence"]),
        warnings=list(meta.get("warnings", [])),
        reason_codes=["FUNCTION_EXECUTED"],
    )


def _builtin_subtract_days(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    args = {**args, "days": -int(args.get("days") or 0)}
    return _builtin_add_days(context, args)


def _builtin_add_working_days(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = add_working_days_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        working_days=int(args.get("working_days") if "working_days" in args else args.get("n", 0)),
        trace_id=context.trace_id,
    )
    return _compliance_outcome("add_working_days", args, result, value=result["date"])


def _builtin_last_day_of_nepali_month(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    year, month = _parse_bs_month(str(args.get("bs_month") or ""))
    last_day = days_in_bs_month(year, month)
    ad = bs_to_gregorian(year, month, last_day)
    meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_last_day_of_month")
    fact_id = month_length_fact_id(year, month)
    return FunctionOutcome(
        value={
            "bs": _format_bs(year, month, last_day),
            "ad": ad.isoformat(),
            "month_name": get_bs_month_name(month),
            "days_in_month": last_day,
        },
        function="last_day_of_nepali_month",
        arguments=args,
        fact_ids=[fact_id, bs_ad_fact_id(year, month, last_day)],
        confidence=str(meta["confidence"]),
        warnings=list(meta.get("warnings", [])),
        reason_codes=["FUNCTION_EXECUTED"],
        trace_url=trace_url_for_fact(fact_id),
    )


def _builtin_first_day_of_nepali_month(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    year, month = _parse_bs_month(str(args.get("bs_month") or ""))
    ad = bs_to_gregorian(year, month, 1)
    meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_first_day_of_month")
    return FunctionOutcome(
        value={"bs": _format_bs(year, month, 1), "ad": ad.isoformat(), "month_name": get_bs_month_name(month)},
        function="first_day_of_nepali_month",
        arguments=args,
        fact_ids=[bs_ad_fact_id(year, month, 1), month_length_fact_id(year, month)],
        confidence=str(meta["confidence"]),
        warnings=list(meta.get("warnings", [])),
        reason_codes=["FUNCTION_EXECUTED"],
    )


def _builtin_last_working_day_of_nepali_month(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    year, month = _parse_bs_month(str(args.get("bs_month") or ""))
    profile_id = _profile_arg(context, args)
    result = month_closing_day_payload(
        profile_id=profile_id,
        bs_year=year,
        bs_month=month,
        trace_id=context.trace_id,
    )
    outcome = _compliance_outcome(
        "last_working_day_of_nepali_month",
        args,
        result,
        value=result["last_working_day"],
        reason_codes=["LAST_WORKING_DAY_SELECTED"],
    )
    outcome.fact_ids = _dedupe([month_length_fact_id(year, month), *outcome.fact_ids])
    return outcome


def _builtin_get_month_length(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    year, month = _parse_bs_month(str(args.get("bs_month") or ""))
    days = days_in_bs_month(year, month)
    meta = build_bs_claim_meta(year, trace_id=context.trace_id, result_class="rulelang_month_length")
    return FunctionOutcome(
        value=days,
        function="get_month_length",
        arguments=args,
        fact_ids=[month_length_fact_id(year, month)],
        confidence=str(meta["confidence"]),
        warnings=list(meta.get("warnings", [])),
        reason_codes=["FUNCTION_EXECUTED"],
    )


def _builtin_get_fiscal_period(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_block = _date_from_arg(args.get("date"))
    profile_id = _profile_arg(context, args)
    result = fiscal_period_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        trace_id=context.trace_id,
    )
    return _compliance_outcome(
        "get_fiscal_period",
        args,
        result,
        value=result["fiscal_period"],
        reason_codes=["FISCAL_PERIOD_SELECTED"],
    )


def _builtin_confidence_at_least(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    confidence = str(args.get("confidence") or _lowest_confidence(context.confidences))
    minimum = str(args.get("minimum") or "source_backed")
    value = _confidence_rank(confidence) >= _confidence_rank(minimum)
    return FunctionOutcome(
        value=value,
        function="confidence_at_least",
        arguments=args,
        confidence=confidence,
        warnings=[],
        reason_codes=["CONFIDENCE_POLICY_SATISFIED" if value else "SOURCE_CONFIDENCE_TOO_LOW"],
    )


def _builtin_requires_human_review(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    date_arg = args.get("date")
    if date_arg is None:
        value = any(code in context.reason_codes for code in {"HUMAN_REVIEW_REQUIRED", "SOURCE_CONFIDENCE_TOO_LOW"})
        return FunctionOutcome(
            value=value,
            function="requires_human_review",
            arguments=args,
            confidence=_lowest_confidence(context.confidences),
            reason_codes=["HUMAN_REVIEW_REQUIRED"] if value else ["FUNCTION_EXECUTED"],
        )
    date_block = _date_from_arg(date_arg)
    profile_id = _profile_arg(context, args)
    result = evaluate_date_payload(
        profile_id=profile_id,
        bs_date=date_block["bs"],
        decision_intent=str(args.get("decision_intent") or "general"),
        trace_id=context.trace_id,
    )
    return _compliance_outcome(
        "requires_human_review",
        args,
        result,
        value=bool(result["decision"]["requires_human_review"]),
    )


def _builtin_fact_is_disputed(context: RuleExecutionContext, args: dict[str, Any]) -> FunctionOutcome:
    fact_id = str(args.get("fact_id") or "")
    if not fact_id:
        raise RuleLangError("fact_id is required", code="INVALID_INPUT")
    graph = build_public_timegraph(context.release_id)
    disputed = any(fact_id in conflict.facts for conflict in graph.conflicts.values())
    warnings = ["fixture_conflict_not_real_calendar_claim"] if disputed and fact_id.startswith("fact_fixture_") else []
    return FunctionOutcome(
        value=disputed,
        function="fact_is_disputed",
        arguments={"fact_id": fact_id},
        fact_ids=[fact_id],
        confidence="fixture" if fact_id.startswith("fact_fixture_") else "source_backed",
        warnings=warnings,
        reason_codes=["DISPUTED_FACT_BLOCKED"] if disputed else ["FUNCTION_EXECUTED"],
    )


ALLOWED_FUNCTIONS = {
    "convert_bs_to_ad": _builtin_convert_bs_to_ad,
    "convert_ad_to_bs": _builtin_convert_ad_to_bs,
    "validate_date": _builtin_validate_date,
    "normalize_date": _builtin_validate_date,
    "get_weekday": _builtin_get_weekday,
    "is_weekend": _builtin_is_weekend,
    "is_working_day": _builtin_is_working_day,
    "is_business_day": _builtin_is_working_day,
    "is_holiday": _builtin_is_holiday,
    "is_known_public_holiday": _builtin_is_holiday,
    "next_working_day": _builtin_next_working_day,
    "previous_working_day": _builtin_previous_working_day,
    "add_days": _builtin_add_days,
    "subtract_days": _builtin_subtract_days,
    "add_working_days": _builtin_add_working_days,
    "last_day_of_nepali_month": _builtin_last_day_of_nepali_month,
    "first_day_of_nepali_month": _builtin_first_day_of_nepali_month,
    "last_working_day_of_nepali_month": _builtin_last_working_day_of_nepali_month,
    "get_month_length": _builtin_get_month_length,
    "get_fiscal_period": _builtin_get_fiscal_period,
    "get_fiscal_year": _builtin_get_fiscal_period,
    "confidence_at_least": _builtin_confidence_at_least,
    "requires_human_review": _builtin_requires_human_review,
    "fact_is_disputed": _builtin_fact_is_disputed,
}


def _validate_inputs(inputs: Any, issues: list[str]) -> None:
    if not isinstance(inputs, dict) or not inputs:
        issues.append("inputs must be a non-empty object")
        return
    for name, spec in inputs.items():
        if not isinstance(name, str) or not name:
            issues.append("input names must be strings")
        if not isinstance(spec, dict):
            issues.append(f"input {name}: schema must be an object")
            continue
        input_type = spec.get("type")
        if input_type not in INPUT_TYPES:
            issues.append(f"input {name}: unsupported type {input_type!r}")
        if input_type == "enum" and not isinstance(spec.get("values"), list):
            issues.append(f"input {name}: enum values are required")


def _validate_outputs(outputs: Any, issues: list[str]) -> None:
    if not isinstance(outputs, dict) or not outputs:
        issues.append("outputs must be a non-empty object")
        return
    for name, spec in outputs.items():
        if not isinstance(name, str) or not name:
            issues.append("output names must be strings")
        if not isinstance(spec, dict):
            issues.append(f"output {name}: schema must be an object")
            continue
        if spec.get("type") not in OUTPUT_TYPES:
            issues.append(f"output {name}: unsupported type {spec.get('type')!r}")


def _validate_risk_policy(policy: Any, issues: list[str]) -> None:
    if not isinstance(policy, dict):
        issues.append("risk_policy must be an object")
        return
    minimum = policy.get("require_confidence_at_least", "source_backed")
    if minimum not in CONFIDENCE_ORDER:
        issues.append("risk_policy.require_confidence_at_least is unsupported")
    for flag in ("block_research_preview", "block_disputed_facts", "payroll_requires_official_or_source_backed"):
        if flag in policy and not isinstance(policy[flag], bool):
            issues.append(f"risk_policy.{flag} must be boolean")
    for action_field in ("unsupported_result_action", "future_date_action"):
        if action_field in policy and policy[action_field] not in {"human_review_required", "blocked", "allow"}:
            issues.append(f"risk_policy.{action_field} is unsupported")


def _validate_steps(steps: list[Any], issues: list[str], *, path: str) -> None:
    for index, step in enumerate(steps):
        step_path = f"{path}[{index}]"
        if not isinstance(step, dict) or len(set(step) & STEP_TYPES) != 1:
            issues.append(f"{step_path}: step must contain exactly one supported step type")
            continue
        step_type = next(iter(set(step) & STEP_TYPES))
        payload = step[step_type]
        if not isinstance(payload, dict):
            issues.append(f"{step_path}.{step_type}: payload must be an object")
            continue
        if step_type == "set":
            if not isinstance(payload.get("name"), str) or not payload.get("name"):
                issues.append(f"{step_path}.set: name is required")
            _validate_expression(payload.get("value"), issues, path=f"{step_path}.set.value")
        elif step_type == "call":
            function_name = str(payload.get("function") or "")
            if function_name in FORBIDDEN_FUNCTIONS:
                issues.append(f"{step_path}.call: forbidden function {function_name}")
            elif function_name not in ALLOWED_FUNCTIONS:
                issues.append(f"{step_path}.call: unsupported function {function_name}")
            args = payload.get("args", {})
            if not isinstance(args, dict):
                issues.append(f"{step_path}.call.args must be an object")
            else:
                for arg_name, arg_value in args.items():
                    _validate_expression(arg_value, issues, path=f"{step_path}.call.args.{arg_name}")
            if "save_as" in payload and not isinstance(payload.get("save_as"), str):
                issues.append(f"{step_path}.call.save_as must be a string")
        elif step_type == "return":
            for key, value in payload.items():
                if not isinstance(key, str):
                    issues.append(f"{step_path}.return: keys must be strings")
                _validate_expression(value, issues, path=f"{step_path}.return.{key}")
        elif step_type == "if":
            _validate_condition(payload.get("condition"), issues, path=f"{step_path}.if.condition")
            _validate_steps(list(payload.get("then") or []), issues, path=f"{step_path}.if.then")
            _validate_steps(list(payload.get("else") or []), issues, path=f"{step_path}.if.else")
        elif step_type == "while":
            max_iterations = payload.get("max_iterations")
            if max_iterations is None:
                issues.append(f"{step_path}.while: max_iterations is required")
            else:
                try:
                    _bounded_loop_iterations(max_iterations)
                except RuleLangError as exc:
                    issues.append(f"{step_path}.while: {exc}")
            _validate_condition(payload.get("condition"), issues, path=f"{step_path}.while.condition")
            body = payload.get("do")
            if not isinstance(body, list) or not body:
                issues.append(f"{step_path}.while.do must be a non-empty list")
            else:
                _validate_steps(body, issues, path=f"{step_path}.while.do")


def _validate_expression(value: Any, issues: list[str], *, path: str) -> None:
    if isinstance(value, str) and value.startswith("$") and not VARIABLE_RE.match(value):
        issues.append(f"{path}: invalid variable reference {value!r}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_expression(item, issues, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        if "call" in value:
            function_name = str(value.get("call") or "")
            if function_name in FORBIDDEN_FUNCTIONS:
                issues.append(f"{path}: forbidden function {function_name}")
            elif function_name not in ALLOWED_FUNCTIONS:
                issues.append(f"{path}: unsupported function {function_name}")
            args = value.get("args", {})
            if not isinstance(args, dict):
                issues.append(f"{path}: args must be an object")
            else:
                for arg_name, arg_value in args.items():
                    _validate_expression(arg_value, issues, path=f"{path}.args.{arg_name}")
            return
        for key, nested in value.items():
            _validate_expression(nested, issues, path=f"{path}.{key}")


def _validate_condition(value: Any, issues: list[str], *, path: str) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, dict):
        if "call" in value:
            _validate_expression(value, issues, path=path)
            return
        known = set(value) & OPERATORS
        if len(known) != 1:
            issues.append(f"{path}: condition must use exactly one supported operator or call")
            return
        operator = next(iter(known))
        if operator in {"and", "or"}:
            items = value[operator]
            if not isinstance(items, list) or not items:
                issues.append(f"{path}.{operator}: requires a non-empty list")
            else:
                for index, item in enumerate(items):
                    _validate_condition(item, issues, path=f"{path}.{operator}[{index}]")
            return
        if operator == "not":
            _validate_condition(value[operator], issues, path=f"{path}.not")
            return
        payload = value[operator]
        if not isinstance(payload, list) or len(payload) != 2:
            issues.append(f"{path}.{operator}: requires a two-item list")
            return
        _validate_expression(payload[0], issues, path=f"{path}.{operator}[0]")
        _validate_expression(payload[1], issues, path=f"{path}.{operator}[1]")
        return
    _validate_expression(value, issues, path=path)


def _normalize_input_payload(rule: dict[str, Any], input_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(input_payload, dict):
        raise RuleLangError("input payload must be an object", code="INVALID_INPUT")
    if len(str(input_payload).encode("utf-8")) > MAX_INPUT_BYTES:
        raise RuleLangError("input payload exceeds RuleLang size limit", code="INVALID_INPUT")
    normalized: dict[str, Any] = {}
    for name, spec in rule["inputs"].items():
        required = bool(spec.get("required", False))
        value = input_payload.get(name, spec.get("default"))
        if value is None:
            if required:
                raise RuleLangError(f"missing required input: {name}", code="INVALID_INPUT")
            continue
        normalized[name] = _normalize_input_value(str(name), spec, value)
    return normalized


def _normalize_input_value(name: str, spec: dict[str, Any], value: Any) -> Any:
    input_type = spec["type"]
    try:
        if input_type == "bs_date":
            year, month, day = parse_bs_date(str(value))
            ad = bs_to_gregorian(year, month, day)
            return {"bs": _format_bs(year, month, day), "ad": ad.isoformat()}
        if input_type == "ad_date":
            ad = parse_ad_date(str(value))
            year, month, day = gregorian_to_bs(ad)
            return {"bs": _format_bs(year, month, day), "ad": ad.isoformat()}
        if input_type == "date":
            return _date_from_arg(value)
        if input_type == "bs_month":
            year, month = _parse_bs_month(str(value))
            return f"{year:04d}-{month:02d}"
        if input_type == "ad_month":
            text = str(value)
            if not re.match(r"^\d{4}-\d{2}$", text):
                raise ValueError("AD month must be YYYY-MM")
            return text
        if input_type == "profile_id":
            profile_id = str(value)
            if profile_id not in PROFILES:
                raise ValueError(f"Unknown compliance profile: {profile_id}")
            return profile_id
        if input_type == "integer":
            return int(value)
        if input_type == "boolean":
            if isinstance(value, bool):
                return value
            if str(value).lower() in {"true", "1", "yes"}:
                return True
            if str(value).lower() in {"false", "0", "no"}:
                return False
            raise ValueError("boolean input must be true or false")
        if input_type == "enum":
            if value not in spec.get("values", []):
                raise ValueError(f"input {name} must be one of {spec.get('values')}")
            return value
        return str(value)
    except Exception as exc:  # noqa: BLE001
        raise RuleLangError(f"invalid input {name}: {exc}", code="INVALID_INPUT") from exc


def _decision_for_context(context: RuleExecutionContext) -> dict[str, Any]:
    policy = context.rule.get("risk_policy") or {}
    status = "approved"
    requires_review = False
    reason_codes = list(context.reason_codes)
    confidence = _lowest_confidence(context.confidences)
    minimum = str(policy.get("require_confidence_at_least", "source_backed"))
    if _confidence_rank(confidence) < _confidence_rank(minimum):
        status = _policy_action_status(policy.get("unsupported_result_action"))
        requires_review = True
        reason_codes.append("SOURCE_CONFIDENCE_TOO_LOW")
    else:
        reason_codes.append("CONFIDENCE_POLICY_SATISFIED")
    if policy.get("block_research_preview") and (
        confidence == "research_preview" or "computed_prediction_not_official" in context.warnings
    ):
        status = "blocked"
        requires_review = True
        reason_codes.append("RESEARCH_PREVIEW_BLOCKED")
    if policy.get("block_disputed_facts") and _has_disputed_fact(context):
        status = "blocked"
        requires_review = True
        reason_codes.append("DISPUTED_FACT_BLOCKED")
    if _result_has_future_date(context):
        action = str(policy.get("future_date_action", "human_review_required"))
        if action == "blocked":
            status = "blocked"
            requires_review = True
        elif action == "human_review_required" and status == "approved":
            status = "review_required"
            requires_review = True
        if action != "allow":
            reason_codes.append("FUTURE_DATE_REVIEW_REQUIRED")
    if any(code in reason_codes for code in {"SOURCE_CONFIDENCE_TOO_LOW", "FUTURE_DATE_REVIEW_REQUIRED"}):
        if status == "approved":
            status = "review_required"
        requires_review = True
    if any(code in reason_codes for code in {"HUMAN_REVIEW_REQUIRED", "PAYROLL_REVIEW_REQUIRED"}):
        if status == "approved":
            status = "review_required"
        requires_review = True
    return {
        "status": status,
        "requires_human_review": requires_review,
        "reason_codes": _dedupe(reason_codes),
    }


def _policy_action_status(action: Any) -> str:
    if action == "blocked":
        return "blocked"
    return "review_required"


def _has_disputed_fact(context: RuleExecutionContext) -> bool:
    try:
        graph = build_public_timegraph(context.release_id)
    except Exception:  # noqa: BLE001
        context.warnings.append("timegraph_unavailable_for_dispute_check")
        return False
    conflict_fact_ids = {fact_id for conflict in graph.conflicts.values() for fact_id in conflict.facts}
    return bool(set(context.fact_ids) & conflict_fact_ids)


def _result_has_future_date(context: RuleExecutionContext) -> bool:
    today = date.today()
    for value in [context.input, context.variables]:
        if _payload_has_future_ad_date(value, today=today):
            return True
    return False


def _payload_has_future_ad_date(value: Any, *, today: date) -> bool:
    if isinstance(value, dict):
        ad = value.get("ad")
        if isinstance(ad, str):
            try:
                if parse_ad_date(ad) > today:
                    return True
            except ValueError:
                pass
        return any(_payload_has_future_ad_date(nested, today=today) for nested in value.values())
    if isinstance(value, list):
        return any(_payload_has_future_ad_date(item, today=today) for item in value)
    return False


def _compliance_outcome(
    function: str,
    args: dict[str, Any],
    result: dict[str, Any],
    *,
    value: Any,
    reason_codes: list[str] | None = None,
) -> FunctionOutcome:
    meta = result.get("meta") if isinstance(result.get("meta"), dict) else {}
    decision = result.get("decision") if isinstance(result.get("decision"), dict) else {}
    codes = list(reason_codes or [])
    codes.extend(str(code) for code in decision.get("reason_codes", []))
    if decision.get("requires_human_review"):
        codes.append("HUMAN_REVIEW_REQUIRED")
    return FunctionOutcome(
        value=value,
        function=function,
        arguments=args,
        fact_ids=list(result.get("fact_ids") or []),
        confidence=str(meta.get("confidence") or "source_backed"),
        warnings=list(meta.get("warnings") or []),
        reason_codes=_dedupe(codes or ["FUNCTION_EXECUTED"]),
        trace_url=result.get("trace_url"),
    )


def _append_trace(
    context: RuleExecutionContext,
    *,
    operation: str,
    function: str | None = None,
    arguments: dict[str, Any] | None = None,
    result: Any = None,
    fact_ids: list[str] | None = None,
    confidence: str | None = None,
    warnings: list[str] | None = None,
    reason_codes: list[str] | None = None,
) -> None:
    if len(context.trace_steps) >= MAX_TRACE_STEPS:
        context.warnings.append("rule_trace_truncated")
        return
    context.trace_steps.append(
        {
            "step_index": len(context.trace_steps) + 1,
            "operation": operation,
            "function": function,
            "arguments": _safe_trace_value(arguments or {}),
            "result": _safe_trace_value(result),
            "fact_ids": fact_ids or [],
            "confidence": confidence,
            "warnings": warnings or [],
            "reason_codes": reason_codes or [],
        }
    )


def _safe_trace_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _safe_trace_value(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [_safe_trace_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _resolve_variable(context: RuleExecutionContext, reference: str) -> Any:
    namespace, name = reference[1:].split(".", 1)
    if namespace == "input":
        if name not in context.input:
            raise RuleLangError(f"unknown input variable: {reference}", code="RULE_EXECUTION_FAILED")
        return context.input[name]
    if namespace == "var":
        if name not in context.variables:
            raise RuleLangError(f"unknown local variable: {reference}", code="RULE_EXECUTION_FAILED")
        return context.variables[name]
    if namespace == "rule":
        if name == "profile_id":
            return _profile_id_for_rule(context.rule, context.input)
        if name not in context.rule:
            raise RuleLangError(f"unknown rule field: {reference}", code="RULE_EXECUTION_FAILED")
        return context.rule[name]
    raise RuleLangError(f"unknown variable namespace: {reference}", code="RULE_EXECUTION_FAILED")


def _profile_id_for_rule(rule: dict[str, Any], normalized_input: dict[str, Any]) -> str:
    profile = normalized_input.get("profile_id") or rule.get("profile_id") or "nepal_private_company_default"
    return str(profile)


def _profile_arg(context: RuleExecutionContext, args: dict[str, Any]) -> str:
    profile_id = str(args.get("profile_id") or _profile_id_for_rule(context.rule, context.input))
    if profile_id not in PROFILES:
        raise RuleLangError(f"Unknown compliance profile: {profile_id}", code="INVALID_INPUT")
    return profile_id


def _date_from_arg(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        if isinstance(value.get("bs"), str) and isinstance(value.get("ad"), str):
            return {"bs": value["bs"], "ad": value["ad"]}
        if isinstance(value.get("bs_date"), str):
            year, month, day = parse_bs_date(value["bs_date"])
            return {"bs": _format_bs(year, month, day), "ad": bs_to_gregorian(year, month, day).isoformat()}
        if isinstance(value.get("ad_date"), str):
            ad = parse_ad_date(value["ad_date"])
            year, month, day = gregorian_to_bs(ad)
            return {"bs": _format_bs(year, month, day), "ad": ad.isoformat()}
    if isinstance(value, str):
        year, month, day = parse_bs_date(value)
        return {"bs": _format_bs(year, month, day), "ad": bs_to_gregorian(year, month, day).isoformat()}
    raise ValueError("date value must be a BS date string or a date object with bs/ad fields")


def _ad_date_from_arg(value: Any) -> date:
    if isinstance(value, dict):
        if isinstance(value.get("ad"), str):
            return parse_ad_date(value["ad"])
        if isinstance(value.get("ad_date"), str):
            return parse_ad_date(value["ad_date"])
    return parse_ad_date(str(value))


def _parse_bs_tuple(value: str) -> tuple[int, int, int]:
    year, month, day = parse_bs_date(value)
    return int(year), int(month), int(day)


def _parse_bs_month(value: str) -> tuple[int, int]:
    if not re.match(r"^\d{4}-\d{2}$", value):
        raise ValueError("bs_month must be YYYY-MM")
    year, month = (int(part) for part in value.split("-"))
    if month < 1 or month > 12:
        raise ValueError("bs_month month must be 01-12")
    days_in_bs_month(year, month)
    return year, month


def _format_bs(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def _bounded_loop_iterations(raw: Any) -> int:
    iterations = DEFAULT_LOOP_MAX_ITERATIONS if raw is None else int(raw)
    if iterations < 1:
        raise RuleLangError("max_iterations must be positive", code="RULE_VALIDATION_FAILED")
    if iterations > ABSOLUTE_LOOP_MAX_ITERATIONS:
        raise RuleLangError(
            f"max_iterations exceeds absolute limit {ABSOLUTE_LOOP_MAX_ITERATIONS}",
            code="RULE_VALIDATION_FAILED",
        )
    return iterations


def _load_rules_from_dir(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    rules: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        import json

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuleLangError(f"invalid rule JSON: {path.name}", code="RULE_VALIDATION_FAILED") from exc
        if not isinstance(payload, dict):
            raise RuleLangError(f"rule root must be an object: {path.name}", code="RULE_VALIDATION_FAILED")
        payload.setdefault("_source_file", str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"))
        _assert_public_rule_allowed(payload)
        rules.append(payload)
    return rules


def _assert_public_rule_allowed(rule: dict[str, Any]) -> None:
    if rulelang_mode() == "public" and rule.get("status") == "private":
        raise RuleLangError("Private rules are not available in public mode.", code="PRIVATE_RULE_NOT_AVAILABLE", status_code=404)


def _public_rule_summary(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": rule.get("rule_id"),
        "version": rule.get("version"),
        "label": rule.get("label"),
        "description": rule.get("description"),
        "status": rule.get("status"),
        "profile_id": rule.get("profile_id"),
        "input_names": sorted((rule.get("inputs") or {}).keys()),
        "output_names": sorted((rule.get("outputs") or {}).keys()),
        "tags": rule.get("tags", []),
        "claim_boundary": rule.get("claim_boundary"),
    }


def _redact_rule_for_public(rule: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "rule_id",
        "version",
        "label",
        "description",
        "profile_id",
        "status",
        "inputs",
        "outputs",
        "steps",
        "risk_policy",
        "claim_boundary",
        "tests",
        "tags",
        "owner",
    }
    return {key: value for key, value in rule.items() if key in allowed}


def _rulelang_meta(
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    confidence: str,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "source": ENTERPRISE_COMPLIANCE_PROFILES.as_dict(),
        "data_version": PUBLIC_DATA_VERSION,
        "release_id": release_id or active_release_id() or PUBLIC_RELEASE_ID,
        "confidence": confidence,
        "claim_boundary": RULELANG_CLAIM_BOUNDARY,
        "warnings": _dedupe([*warnings, "not_legal_tax_or_banking_contract_authority"]),
        "trace_id": trace_id,
        "result_class": "rulelang_execution",
    }


def _confidence_rank(confidence: str) -> int:
    return CONFIDENCE_ORDER.get(confidence, 0)


def _lowest_confidence(confidences: list[str]) -> str:
    if not confidences:
        return "source_backed"
    return min(confidences, key=_confidence_rank)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _evaluate_expectations(result: dict[str, Any], expectations: dict[str, Any]) -> list[dict[str, Any]]:
    assertions: list[dict[str, Any]] = []
    for path, expected in expectations.items():
        actual = _get_path(result, str(path))
        passed = _matches_expectation(actual, expected)
        assertions.append(
            {
                "path": path,
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
        )
    return assertions


def _get_path(payload: dict[str, Any], path: str) -> Any:
    value: Any = payload
    for part in path.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value


def _matches_expectation(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict) and expected.get("exists") is True:
        return actual is not None
    if isinstance(expected, dict) and expected.get("contains") is not None:
        return expected["contains"] in actual if isinstance(actual, list) else False
    return actual == expected


def _explanation_summary(result: dict[str, Any]) -> str:
    status = result["decision"]["status"]
    rule_id = result["rule_id"]
    codes = ", ".join(result["decision"]["reason_codes"][:4])
    return f"Rule {rule_id} completed with status {status}. Primary reason codes: {codes}."


REASON_CODE_CATALOG = {
    "RULE_VALIDATED": "The RuleLang definition passed structural validation.",
    "RULE_VALIDATION_FAILED": "The RuleLang definition failed schema or safety validation.",
    "INPUT_VALIDATED": "The provided input matched the declared input schema.",
    "INVALID_INPUT": "Input did not match the declared schema or supported calendar range.",
    "FUNCTION_UNSUPPORTED": "A rule attempted to call a function outside the allowlist.",
    "FUNCTION_EXECUTED": "A built-in RuleLang function executed successfully.",
    "LAST_WORKING_DAY_SELECTED": "The selected result is the last working day for the requested BS month.",
    "NEXT_WORKING_DAY_SELECTED": "The selected result moved forward to a working day.",
    "PREVIOUS_WORKING_DAY_SELECTED": "The selected result moved backward to a working day.",
    "FISCAL_PERIOD_SELECTED": "The result includes a Nepali fiscal period classification.",
    "WEEKEND_SKIPPED": "A weekend day was skipped during a bounded working-day search.",
    "HOLIDAY_SKIPPED": "A public-corpus holiday was skipped during a bounded working-day search.",
    "BANKING_HOLIDAY_SKIPPED": "A banking holiday placeholder was considered but requires institutional source review.",
    "MAX_ITERATIONS_EXCEEDED": "A loop or search exceeded its configured safety bound.",
    "OUTSIDE_SUPPORTED_RANGE": "The requested date falls outside the supported public calendar range.",
    "SOURCE_CONFIDENCE_TOO_LOW": "The source confidence did not satisfy the rule risk policy.",
    "DISPUTED_FACT_BLOCKED": "The rule referenced a TimeGraph fact currently represented as disputed.",
    "RESEARCH_PREVIEW_BLOCKED": "The rule policy blocks research-preview results.",
    "FUTURE_DATE_REVIEW_REQUIRED": "The rule policy requires review for future-dated results.",
    "UNSUPPORTED_RESULT_REVIEW_REQUIRED": "Unsupported or weak results require human review.",
    "CONFIDENCE_POLICY_SATISFIED": "The result confidence satisfied the rule risk policy.",
    "HUMAN_REVIEW_REQUIRED": "The result is not auto-approvable and requires human review.",
    "PAYROLL_REVIEW_REQUIRED": "Payroll-style use needs stronger institutional source review.",
    "RULE_EXECUTION_FAILED": "The rule failed during deterministic execution.",
}


__all__ = [
    "ABSOLUTE_LOOP_MAX_ITERATIONS",
    "ALLOWED_FUNCTIONS",
    "DEFAULT_LOOP_MAX_ITERATIONS",
    "MAX_STEPS",
    "MAX_TRACE_STEPS",
    "REASON_CODE_CATALOG",
    "RULELANG_CLAIM_BOUNDARY",
    "RuleLangError",
    "evaluate_custom_rule_payload",
    "evaluate_rule_payload",
    "execute_rule",
    "explain_rule_payload",
    "get_rule_definition",
    "get_rule_payload",
    "list_rules_payload",
    "load_rules",
    "rulelang_capabilities_payload",
    "run_all_rule_tests_payload",
    "run_rule_tests",
    "test_rule_payload",
    "validate_rule",
    "validate_rule_payload",
]
