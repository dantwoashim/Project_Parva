"""Deterministic temporal impact simulation for public Parva artifacts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.core.source_metadata import PUBLIC_RELEASE_ID
from app.services.rulelang_service import RuleLangError, evaluate_rule_payload, load_rules
from app.services.timegraph_service import build_public_timegraph
from app.services.trust_infrastructure_service import (
    TrustInfrastructureError,
    build_date_conversion_evidence_packet,
    diff_releases_payload,
    now_utc,
    resolve_release_id,
)

IMPACT_CLAIM_BOUNDARY = "impact_simulation_not_legal_authority"
MAX_CHANGES = 500
MAX_DEPENDENCIES = 10000
MAX_IMPACTS = 1000
DEFAULT_IMPACT_LIMIT = 100

CHANGE_TYPES = {
    "SOURCE_ADDED",
    "SOURCE_REMOVED",
    "SOURCE_CHANGED",
    "RELEASE_ADDED",
    "RELEASE_SUPERSEDED",
    "FACT_ADDED",
    "FACT_REMOVED",
    "FACT_CHANGED",
    "FACT_CONFIDENCE_CHANGED",
    "HOLIDAY_ADDED",
    "HOLIDAY_REMOVED",
    "HOLIDAY_DATE_CHANGED",
    "FESTIVAL_DATE_CHANGED",
    "MONTH_LENGTH_CHANGED",
    "FISCAL_PERIOD_CHANGED",
    "PROFILE_POLICY_CHANGED",
    "RULE_CHANGED",
    "RULE_VERSION_CHANGED",
    "RULE_EXECUTION_RESULT_CHANGED",
    "CONFLICT_DISCOVERED",
    "CONFLICT_RESOLVED",
    "EVIDENCE_SCHEMA_CHANGED",
}
SEVERITIES = ("info", "low", "medium", "high", "critical")
REASON_CODES = {
    "SUPPORTING_SOURCE_CHANGED",
    "SUPPORTING_FACT_CHANGED",
    "SOURCE_REMOVED",
    "RELEASE_SUPERSEDED",
    "FACT_CONFIDENCE_DOWNGRADED",
    "FACT_CONFIDENCE_UPGRADED",
    "FACT_NOW_DISPUTED",
    "CONFLICT_DISCOVERED",
    "CONFLICT_RESOLVED",
    "PROFILE_POLICY_CHANGED",
    "RULE_VERSION_CHANGED",
    "RULE_RESULT_MAY_CHANGE",
    "RULE_RESULT_CHANGED",
    "EVIDENCE_PACKET_STALE_FOR_CURRENT_USE",
    "EVIDENCE_PACKET_HISTORICALLY_VALID",
    "CALENDAR_FEED_REGENERATION_REQUIRED",
    "API_RESPONSE_MAY_CHANGE",
    "HUMAN_REVIEW_REQUIRED",
    "NO_REGISTERED_DEPENDENCIES",
    "IMPACT_SIMULATION_LIMITED_TO_PUBLIC_GRAPH",
    "SEMANTIC_DIFF_NOT_AVAILABLE",
}
RECOMMENDED_ACTIONS = {
    "NO_ACTION",
    "REGENERATE_EVIDENCE_PACKET",
    "RERUN_RULE",
    "RERUN_COMPLIANCE_DECISION",
    "REGENERATE_CALENDAR_FEED",
    "NOTIFY_SUBSCRIBERS",
    "REVIEW_BEFORE_PAYROLL_USE",
    "REVIEW_BEFORE_BANKING_USE",
    "PIN_OLD_RELEASE_FOR_HISTORICAL_RECORD",
    "MIGRATE_TO_NEW_RELEASE",
    "ESCALATE_TO_HUMAN_REVIEW",
}


class ImpactError(ValueError):
    """Raised when impact input cannot be analyzed safely."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def impact_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "temporal_impact_simulator",
        "status": "public_preview",
        "active_release_id": resolve_release_id(None),
        "supported_change_set_types": [
            "release_diff",
            "source_change",
            "fact_change",
            "rule_change",
            "profile_change",
            "confidence_change",
            "conflict_change",
            "manual_hypothetical",
        ],
        "supported_dependency_types": [
            "evidence_packet",
            "rule_execution",
            "profile_decision",
            "timegraph_fact",
            "release_artifact",
            "trust_log_entry",
        ],
        "limits": {
            "max_changes": MAX_CHANGES,
            "max_dependencies": MAX_DEPENDENCIES,
            "default_impact_limit": DEFAULT_IMPACT_LIMIT,
            "max_impact_limit": MAX_IMPACTS,
        },
        "claim_boundary": IMPACT_CLAIM_BOUNDARY,
        "warnings": [
            "Impact simulation is limited to registered public dependencies.",
            "Stale evidence remains historically valid for the release that generated it.",
        ],
    }


def semantic_release_diff_payload(
    from_release_id: str,
    to_release_id: str,
    *,
    include_fixture: bool = False,
) -> dict[str, Any]:
    from_release_id = resolve_release_id(from_release_id)
    to_release_id = resolve_release_id(to_release_id)
    if from_release_id == to_release_id and not include_fixture:
        return {
            "from_release_id": from_release_id,
            "to_release_id": to_release_id,
            "diff_level": "semantic_self_diff",
            "summary": {
                "facts_added": 0,
                "facts_removed": 0,
                "facts_changed": 0,
                "sources_changed": 0,
                "profiles_changed": 0,
                "rules_changed": 0,
                "confidence_changes": 0,
            },
            "changes": [],
            "warnings": ["Self-diff produced no semantic changes."],
            "meta": _impact_meta()["meta"],
        }
    if include_fixture:
        return _fixture_semantic_diff(from_release_id, to_release_id)
    try:
        trust_diff = diff_releases_payload(from_release_id, to_release_id)
    except TrustInfrastructureError as exc:
        raise ImpactError(str(exc), status_code=exc.status_code) from exc
    changes: list[dict[str, Any]] = []
    for source_id in trust_diff["changes"]["sources"]["changed"]:
        changes.append(
            _change(
                change_type="SOURCE_CHANGED",
                entity_type="source",
                entity_id=source_id,
                reason_codes=["SUPPORTING_SOURCE_CHANGED"],
            )
        )
    for artifact_id in trust_diff["changes"]["artifacts"]["changed"]:
        changes.append(
            _change(
                change_type="FACT_CHANGED",
                entity_type="release_artifact",
                entity_id=artifact_id,
                reason_codes=["SEMANTIC_DIFF_NOT_AVAILABLE"],
            )
        )
    return {
        "from_release_id": from_release_id,
        "to_release_id": to_release_id,
        "diff_level": trust_diff.get("diff_scope", "manifest_source_artifact_only"),
        "summary": {
            "facts_added": 0,
            "facts_removed": 0,
            "facts_changed": len(trust_diff["changes"]["artifacts"]["changed"]),
            "sources_changed": len(trust_diff["changes"]["sources"]["changed"]),
            "profiles_changed": 0,
            "rules_changed": 0,
            "confidence_changes": 0,
        },
        "changes": changes,
        "warnings": list(trust_diff.get("warnings") or []),
        "meta": _impact_meta()["meta"],
    }


def simulate_release_diff_payload(
    from_release_id: str,
    to_release_id: str,
    *,
    include_fixture: bool = False,
    limit: int = DEFAULT_IMPACT_LIMIT,
) -> dict[str, Any]:
    diff = semantic_release_diff_payload(from_release_id, to_release_id, include_fixture=include_fixture)
    change_set = {
        "change_set_id": f"changeset_{from_release_id}_to_{to_release_id}",
        "change_set_type": "release_diff",
        "from_release_id": from_release_id,
        "to_release_id": to_release_id,
        "created_at": now_utc(),
        "changes": diff["changes"],
        "meta": diff["meta"],
    }
    return simulate_change_set_payload(change_set, limit=limit)


def simulate_change_set_payload(change_set: dict[str, Any], *, limit: int = DEFAULT_IMPACT_LIMIT) -> dict[str, Any]:
    normalized = _normalize_change_set(change_set)
    dependencies = build_dependency_registry(release_id=normalized.get("to_release_id") or normalized.get("from_release_id"))
    impacts: list[dict[str, Any]] = []
    for change in normalized["changes"]:
        matches = _matching_dependencies(change, dependencies)
        for dependency in matches:
            impacts.append(_impact_item(change, dependency))
    if not impacts:
        impacts.append(
            {
                "impact_id": f"impact_item_{uuid4().hex[:12]}",
                "impact_type": "no_registered_dependency",
                "severity": "info",
                "affected_entity": {"entity_type": "none", "entity_id": "none"},
                "triggering_change_ids": [change["change_id"] for change in normalized["changes"]],
                "reason_codes": ["NO_REGISTERED_DEPENDENCIES", "IMPACT_SIMULATION_LIMITED_TO_PUBLIC_GRAPH"],
                "requires_human_review": False,
                "recommended_actions": ["NO_ACTION"],
                "trace": {"dependency_path": []},
                "meta": _impact_meta(confidence="source_backed")["meta"],
            }
        )
    bounded_limit = min(max(1, int(limit)), MAX_IMPACTS)
    impacts = impacts[:bounded_limit]
    severity_counts = {severity: sum(1 for item in impacts if item["severity"] == severity) for severity in SEVERITIES}
    stale_count = sum(1 for item in impacts if item["impact_type"] == "evidence_packet_stale")
    recommendations = _dedupe(action for item in impacts for action in item["recommended_actions"])
    return {
        "impact_run_id": f"impact_{uuid4().hex[:16]}",
        "created_at": now_utc(),
        "change_set_id": normalized["change_set_id"],
        "mode": "simulation",
        "change_set": normalized,
        "summary": {
            "changes_analyzed": len(normalized["changes"]),
            "dependencies_checked": min(len(dependencies), MAX_DEPENDENCIES),
            "impacts_found": len(impacts),
            **severity_counts,
            "human_review_required": sum(1 for item in impacts if item["requires_human_review"]),
            "stale_evidence_packets": stale_count,
        },
        "impacts": impacts,
        "recommendations": recommendations,
        "meta": _impact_meta()["meta"],
    }


def build_dependency_registry(*, release_id: str | None = None) -> list[dict[str, Any]]:
    selected = resolve_release_id(release_id)
    graph = build_public_timegraph(selected)
    dependencies: list[dict[str, Any]] = []
    for fact in list(graph.facts.values())[:MAX_DEPENDENCIES]:
        dependencies.append(
            {
                "dependency_id": f"dep_fact_{fact.fact_id}",
                "dependency_type": "timegraph_fact",
                "owner_type": "release",
                "owner_id": selected,
                "depends_on": [
                    {"entity_type": "temporal_fact", "entity_id": fact.fact_id},
                    {"entity_type": "release", "entity_id": selected},
                    *[
                        {"entity_type": "source", "entity_id": source_id}
                        for source_id in fact.source_ids
                    ],
                ],
                "result_ref": {"type": "timegraph_fact", "id": fact.fact_id},
                "risk_policy": {"requires_review_on_conflict": True},
                "metadata": {"confidence": fact.confidence, "fact_type": fact.fact_type},
            }
        )
    dependencies.extend(_sample_evidence_dependencies(selected))
    dependencies.extend(_sample_rule_dependencies(selected))
    return dependencies[:MAX_DEPENDENCIES]


def reason_codes_payload() -> dict[str, Any]:
    return {
        "reason_codes": sorted(REASON_CODES),
        "claim_boundary": IMPACT_CLAIM_BOUNDARY,
        "meta": _impact_meta()["meta"],
    }


def recommended_actions_payload() -> dict[str, Any]:
    return {
        "recommended_actions": sorted(RECOMMENDED_ACTIONS),
        "claim_boundary": IMPACT_CLAIM_BOUNDARY,
        "meta": _impact_meta()["meta"],
    }


def event_schema_payload() -> dict[str, Any]:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Parva Temporal Impact Event",
        "type": "object",
        "required": ["event_id", "event_type", "created_at", "severity", "reason_codes", "signature_status"],
        "properties": {
            "event_id": {"type": "string"},
            "event_type": {
                "type": "string",
                "enum": [
                    "temporal.release.diff.created",
                    "temporal.impact.detected",
                    "temporal.evidence.stale",
                    "temporal.rule.review_required",
                    "temporal.feed.regeneration_required",
                    "temporal.conflict.discovered",
                    "temporal.conflict.resolved",
                ],
            },
            "created_at": {"type": "string"},
            "impact_run_id": {"type": "string"},
            "severity": {"type": "string", "enum": list(SEVERITIES)},
            "affected_entity": {"type": "object"},
            "reason_codes": {"type": "array", "items": {"type": "string"}},
            "recommended_actions": {"type": "array", "items": {"type": "string"}},
            "signature": {"type": ["string", "null"]},
            "signature_status": {"type": "string", "enum": ["unsigned_preview", "signed", "unverified"]},
        },
    }
    return {"schema": schema, "meta": _impact_meta()["meta"]}


def _sample_evidence_dependencies(release_id: str) -> list[dict[str, Any]]:
    try:
        packet = build_date_conversion_evidence_packet(
            release_id=release_id,
            bs_date="2082-01-01",
            trace_id="impact_dependency_seed",
        )
    except Exception:
        return []
    return [
        {
            "dependency_id": f"dep_evidence_{packet['packet_id']}",
            "dependency_type": "evidence_packet",
            "owner_type": "public_demo",
            "owner_id": "public_evidence_seed",
            "depends_on": [
                {"entity_type": "evidence_packet", "entity_id": packet["packet_id"]},
                {"entity_type": "release", "entity_id": release_id},
                *[
                    {"entity_type": "temporal_fact", "entity_id": fact_id}
                    for fact_id in packet.get("fact_ids", [])
                ],
                *[
                    {"entity_type": "source", "entity_id": str(source.get("id"))}
                    for source in packet.get("sources", [])
                    if source.get("id")
                ],
            ],
            "result_ref": {"type": "evidence_packet", "id": packet["packet_id"]},
            "risk_policy": {"requires_review_on_confidence_below": "source_backed"},
            "metadata": {
                "packet_type": packet.get("packet_type"),
                "historically_valid": True,
                "confidence": packet.get("confidence", "unknown"),
            },
        }
    ]


def _sample_rule_dependencies(release_id: str) -> list[dict[str, Any]]:
    dependencies: list[dict[str, Any]] = []
    for rule in load_rules(include_private=False):
        tests = rule.get("tests") or []
        if not tests:
            continue
        input_payload = deepcopy(tests[0].get("input") or {})
        try:
            result = evaluate_rule_payload(
                str(rule["rule_id"]),
                input_payload,
                release_id=release_id,
                trace_id="impact_rule_dependency_seed",
                include_evidence=False,
            )
        except (RuleLangError, ValueError):
            continue
        dependencies.append(
            {
                "dependency_id": f"dep_rule_exec_{rule['rule_id']}",
                "dependency_type": "rule_execution",
                "owner_type": "rule",
                "owner_id": str(rule["rule_id"]),
                "depends_on": [
                    {"entity_type": "rule", "entity_id": str(rule["rule_id"])},
                    {"entity_type": "profile", "entity_id": result.get("profile_id")},
                    {"entity_type": "release", "entity_id": release_id},
                    *[
                        {"entity_type": "temporal_fact", "entity_id": fact_id}
                        for fact_id in result.get("fact_ids", [])
                    ],
                ],
                "result_ref": {"type": "rule_execution", "id": result.get("trace_id")},
                "risk_policy": {
                    "requires_review_on_conflict": True,
                    "requires_review_on_confidence_below": "source_backed",
                },
                "metadata": {
                    "rule_id": str(rule["rule_id"]),
                    "rule_version": str(rule["version"]),
                    "input": input_payload,
                    "old_output": result.get("output"),
                    "decision_status": result.get("decision", {}).get("status"),
                    "confidence": result.get("confidence", "unknown"),
                },
            }
        )
    return dependencies


def _matching_dependencies(change: dict[str, Any], dependencies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entity = {"entity_type": change["entity_type"], "entity_id": change["entity_id"]}
    aliases = [entity]
    if change["entity_type"] == "temporal_fact":
        aliases.append({"entity_type": "fact", "entity_id": change["entity_id"]})
    return [
        dependency
        for dependency in dependencies
        if any(dep.get("entity_id") == alias["entity_id"] and dep.get("entity_type") == alias["entity_type"] for dep in dependency["depends_on"] for alias in aliases)
    ]


def _impact_item(change: dict[str, Any], dependency: dict[str, Any]) -> dict[str, Any]:
    dependency_type = dependency["dependency_type"]
    reason_codes = _impact_reason_codes(change, dependency)
    severity = _impact_severity(change, dependency)
    actions = _impact_actions(change, dependency, severity)
    impact_type = "dependency_may_change"
    if dependency_type == "evidence_packet":
        impact_type = "evidence_packet_stale"
        reason_codes.extend(["EVIDENCE_PACKET_HISTORICALLY_VALID", "EVIDENCE_PACKET_STALE_FOR_CURRENT_USE"])
    elif dependency_type == "rule_execution":
        impact_type = "rule_execution_may_change"
        reason_codes.append("RULE_RESULT_MAY_CHANGE")
    return {
        "impact_id": f"impact_item_{uuid4().hex[:12]}",
        "impact_type": impact_type,
        "severity": severity,
        "affected_entity": {
            "entity_type": dependency_type,
            "entity_id": dependency["result_ref"]["id"],
        },
        "triggering_change_ids": [change["change_id"]],
        "old_result": dependency.get("metadata", {}).get("old_output"),
        "new_result": None,
        "reason_codes": _dedupe(reason_codes),
        "requires_human_review": severity in {"medium", "high", "critical"},
        "recommended_actions": actions,
        "trace": {
            "dependency_path": [
                {"from": dependency["dependency_id"], "to": change["entity_id"], "type": "DEPENDS_ON"}
            ]
        },
        "meta": _impact_meta(confidence=dependency.get("metadata", {}).get("confidence", "source_backed"))["meta"],
    }


def _impact_reason_codes(change: dict[str, Any], dependency: dict[str, Any]) -> list[str]:
    codes = list(change.get("reason_codes") or [])
    if change["entity_type"] == "source":
        codes.append("SUPPORTING_SOURCE_CHANGED")
    if change["entity_type"] in {"temporal_fact", "fact"}:
        codes.append("SUPPORTING_FACT_CHANGED")
    if change["change_type"] == "FACT_CONFIDENCE_CHANGED":
        before = str(change.get("confidence_before") or "")
        after = str(change.get("confidence_after") or "")
        codes.append("FACT_CONFIDENCE_DOWNGRADED" if _confidence_rank(after) < _confidence_rank(before) else "FACT_CONFIDENCE_UPGRADED")
    if change["change_type"] == "CONFLICT_DISCOVERED":
        codes.append("CONFLICT_DISCOVERED")
        codes.append("FACT_NOW_DISPUTED")
    if change["change_type"] == "CONFLICT_RESOLVED":
        codes.append("CONFLICT_RESOLVED")
    if change["change_type"] == "PROFILE_POLICY_CHANGED" or dependency["dependency_type"] == "profile_decision":
        codes.append("PROFILE_POLICY_CHANGED")
    if change["change_type"] in {"RULE_CHANGED", "RULE_VERSION_CHANGED"}:
        codes.append("RULE_VERSION_CHANGED")
    return _dedupe(codes)


def _impact_severity(change: dict[str, Any], dependency: dict[str, Any]) -> str:
    if change["change_type"] == "CONFLICT_DISCOVERED":
        return "critical"
    if dependency["dependency_type"] == "rule_execution":
        rule_id = str(dependency.get("metadata", {}).get("rule_id") or "")
        if "payroll" in rule_id or "working_day" in rule_id:
            return "high"
        return "medium"
    if dependency["dependency_type"] == "evidence_packet":
        return "medium"
    if change["change_type"] in {"SOURCE_REMOVED", "FACT_REMOVED", "PROFILE_POLICY_CHANGED"}:
        return "high"
    if change["change_type"] in {"SOURCE_CHANGED", "FACT_CHANGED", "FACT_CONFIDENCE_CHANGED"}:
        return "medium"
    return "low"


def _impact_actions(change: dict[str, Any], dependency: dict[str, Any], severity: str) -> list[str]:
    actions: list[str] = []
    if dependency["dependency_type"] == "evidence_packet":
        actions.append("REGENERATE_EVIDENCE_PACKET")
        actions.append("PIN_OLD_RELEASE_FOR_HISTORICAL_RECORD")
    if dependency["dependency_type"] == "rule_execution":
        actions.append("RERUN_RULE")
    if severity in {"high", "critical"}:
        actions.append("ESCALATE_TO_HUMAN_REVIEW")
    if "payroll" in str(dependency.get("owner_id", "")):
        actions.append("REVIEW_BEFORE_PAYROLL_USE")
    if change["change_type"] == "RELEASE_SUPERSEDED":
        actions.append("MIGRATE_TO_NEW_RELEASE")
    return _dedupe(actions or ["NO_ACTION"])


def _normalize_change_set(change_set: dict[str, Any]) -> dict[str, Any]:
    changes = change_set.get("changes")
    if not isinstance(changes, list):
        raise ImpactError("change_set.changes must be a list")
    if len(changes) > MAX_CHANGES:
        raise ImpactError(f"change set exceeds max changes: {MAX_CHANGES}")
    normalized_changes = [_normalize_change(change, index) for index, change in enumerate(changes, start=1)]
    return {
        "change_set_id": str(change_set.get("change_set_id") or f"changeset_{uuid4().hex[:12]}"),
        "change_set_type": str(change_set.get("change_set_type") or "manual_hypothetical"),
        "from_release_id": change_set.get("from_release_id") or PUBLIC_RELEASE_ID,
        "to_release_id": change_set.get("to_release_id") or change_set.get("from_release_id") or PUBLIC_RELEASE_ID,
        "created_at": change_set.get("created_at") or now_utc(),
        "changes": normalized_changes,
        "meta": _impact_meta()["meta"],
    }


def _normalize_change(change: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(change, dict):
        raise ImpactError("each change must be an object")
    change_type = str(change.get("change_type") or "FACT_CHANGED")
    if change_type not in CHANGE_TYPES:
        raise ImpactError(f"unsupported change_type: {change_type}")
    entity_type = str(change.get("entity_type") or "")
    entity_id = str(change.get("entity_id") or "")
    if not entity_type or not entity_id:
        raise ImpactError("each change requires entity_type and entity_id")
    return {
        **change,
        "change_id": str(change.get("change_id") or f"change_{index:03d}"),
        "change_type": change_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "reason_codes": list(change.get("reason_codes") or []),
    }


def _fixture_semantic_diff(from_release_id: str, to_release_id: str) -> dict[str, Any]:
    fact_id = "fact_month_length_bs_2082_04"
    change = _change(
        change_type="FACT_CHANGED",
        entity_type="temporal_fact",
        entity_id=fact_id,
        old_value={"days": 31},
        new_value={"days": 30, "fixture_only": True},
        reason_codes=["SUPPORTING_FACT_CHANGED"],
        notes="Fixture-only semantic diff for public conformance tests.",
    )
    return {
        "from_release_id": from_release_id,
        "to_release_id": to_release_id,
        "diff_level": "fixture_semantic_demo",
        "summary": {
            "facts_added": 0,
            "facts_removed": 0,
            "facts_changed": 1,
            "sources_changed": 0,
            "profiles_changed": 0,
            "rules_changed": 0,
            "confidence_changes": 0,
        },
        "changes": [change],
        "warnings": ["Fixture semantic diff is for tests and demos only."],
        "meta": _impact_meta()["meta"],
    }


def _change(**kwargs: Any) -> dict[str, Any]:
    return {
        "change_id": kwargs.pop("change_id", f"change_{uuid4().hex[:8]}"),
        "source_ids": kwargs.pop("source_ids", []),
        "confidence_before": kwargs.pop("confidence_before", None),
        "confidence_after": kwargs.pop("confidence_after", None),
        **kwargs,
    }


def _impact_meta(*, confidence: str = "source_backed") -> dict[str, Any]:
    trace_id = f"impact_trace_{uuid4().hex[:16]}"
    return {
        "meta": {
            "release_id": resolve_release_id(None),
            "confidence": confidence,
            "claim_boundary": IMPACT_CLAIM_BOUNDARY,
            "warnings": [
                "impact_simulation_limited_to_registered_public_dependencies",
                "not_legal_tax_or_banking_contract_authority",
            ],
            "trace_id": trace_id,
            "simulation_scope": "public_graph_registered_dependencies",
            "data_mode": "public",
        }
    }


def _confidence_rank(confidence: str) -> int:
    order = {
        "unsupported": 0,
        "unknown": 1,
        "disputed": 1,
        "research_preview": 2,
        "fixture_only": 2,
        "calculated": 3,
        "source_backed": 4,
        "official_verified": 5,
    }
    return order.get(confidence, 1)


def _dedupe(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
