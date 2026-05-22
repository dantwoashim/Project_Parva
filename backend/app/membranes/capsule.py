"""Build replay-verifiable civil temporal membranes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, cast

from app.boundary.vector import BoundaryVector
from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    gregorian_to_bs,
    is_valid_bs_date,
)
from app.canonicalization.normalize import canonical_json, canonicalize_query
from app.membranes.identity import membrane_identity_hash
from app.membranes.source_resolution import (
    resolve_ad_to_bs_source,
    resolve_bs_months_source,
    resolve_convert_bs_to_ad_source,
    resolve_fiscal_year_source,
    resolve_holiday_source,
    resolve_validate_bs_date_source,
    resolve_working_day_source,
)
from app.sources.coverage import SourceCoverageResolution
from app.sources.hashing import canonical_json_hash
from app.trust.field_provenance import FieldProvenance, ProvenanceMap
from app.trust.taint import AuthorityTaint, TaintFlag
from app.witnesses.schema import Witness

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "sources" / "source_snapshot.json"


def _source_snapshot_hash() -> str:
    if not SOURCE_SNAPSHOT_PATH.exists():
        return "sha256:source_snapshot_unavailable"
    payload = json.loads(SOURCE_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return str(payload.get("snapshot_hash") or "sha256:source_snapshot_missing_hash")


def _date_key(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def _proof_requested(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"membrane", "compact", "audit", "replay"}


def proof_response(capsule: dict[str, Any], *, mode: str = "membrane") -> dict[str, Any]:
    boundary = dict(capsule["boundary"])
    boundary.setdefault("not_authority", True)
    return {
        "mode": mode,
        "capsule": capsule,
        "identity_hash": capsule["identity_hash"],
        "witness_hash": capsule["witness_hash"],
        "field_provenance": capsule["field_provenance"],
        "boundary_vector": boundary,
        "proof_pack": capsule["proof_pack"],
        "source_docket_refs": capsule["source_docket_ids"],
        "freshness": capsule["boundary"].get("freshness"),
    }


def _provenance_for_result(
    result: dict[str, Any],
    source_resolution: SourceCoverageResolution,
    *,
    derivation: str,
    policy_id: str = "canonical@0.1.0",
    authority: AuthorityTaint | None = None,
    extra_flags: frozenset[TaintFlag] = frozenset(),
) -> ProvenanceMap:
    effective_authority = authority or source_resolution.authority
    flags = set(extra_flags)
    if source_resolution.review_required:
        flags.add(TaintFlag.REVIEW_REQUIRED)
    source_docket_id = source_resolution.source_docket_ids[0] if source_resolution.source_docket_ids else None
    return ProvenanceMap(
        {
            field: FieldProvenance(
                field,
                effective_authority,
                derivation,
                source_docket_id=source_docket_id,
                witness_ids=source_resolution.review_witnesses,
                policy_id=policy_id,
                review_state="review_required" if source_resolution.review_required else "reviewed",
                flags=frozenset(flags),
            )
            for field in result
        }
    )


def _policy_trace(operation: str, source_resolution: SourceCoverageResolution, *, notes: list[str] | None = None) -> dict[str, Any]:
    return {
        "policy_id": "canonical@0.1.0",
        "operation": operation,
        "decision": {
            "authority": source_resolution.authority.value,
            "coverage_status": source_resolution.coverage_status,
            "review_required": source_resolution.review_required,
            "claim_boundary": source_resolution.claim_boundary,
            "eligible_official": source_resolution.eligible_official,
        },
        "rules": [
            "eligible_source_docket_must_cover_requested_temporal_scope",
            "sample_source_dockets_cannot_upgrade_authority",
            "unsupported_or_uncovered_results_require_review",
            "technical_decision_support_not_final_authority",
        ],
        "notes": notes or [],
    }


def _build_capsule(
    *,
    operation: str,
    input_payload: dict[str, Any],
    context: dict[str, Any],
    result: dict[str, Any],
    source_resolution: SourceCoverageResolution,
    derivation: str,
    replay_step: str,
    membrane_kind: str = "positive",
    result_authority: AuthorityTaint | None = None,
    extra_flags: frozenset[TaintFlag] = frozenset(),
    method_parameters: dict[str, Any] | None = None,
    policy_notes: list[str] | None = None,
) -> dict[str, Any]:
    query = {"operation": operation, "input": input_payload, "context": context}
    canonical_query = canonicalize_query(query)
    provenance = _provenance_for_result(
        result,
        source_resolution,
        derivation=derivation,
        authority=result_authority,
        extra_flags=extra_flags,
    )
    boundary = BoundaryVector.from_provenance(
        provenance,
        ignorance_state="known" if membrane_kind == "positive" else "negative_or_failure",
    ).as_dict()
    boundary["claim_boundary"] = source_resolution.claim_boundary
    if source_resolution.review_required:
        boundary["review_state"] = "required"
    source_snapshot_hash = _source_snapshot_hash()
    parameters = {
        "source_snapshot_hash": source_snapshot_hash,
        "policy_id": "canonical@0.1.0",
        **(method_parameters or {}),
    }
    witness = Witness(
        operation=operation,
        input_hash=f"sha256:{canonical_json_hash(canonical_query)}",
        output_hash=f"sha256:{canonical_json_hash(result)}",
        verifier=f"parva.{operation}",
        verifier_version="1.0.0",
        method_parameters=parameters,
        source_refs=source_resolution.source_refs,
    )
    capsule = {
        "kind": "parva_membrane",
        "membrane_kind": membrane_kind,
        "canonical_query": canonical_query,
        "canonical_query_json": canonical_json(canonical_query),
        "identity_hash": membrane_identity_hash(canonical_query),
        "result": result,
        "boundary": boundary,
        "field_provenance": provenance.as_dict(),
        "source_docket_ids": list(source_resolution.source_docket_ids),
        "source_resolution": source_resolution.as_dict(),
        "source_snapshot_hash": source_snapshot_hash,
        "policy_trace": _policy_trace(operation, source_resolution, notes=policy_notes),
        "proof_pack": {
            "level": "audit",
            "verifier": f"parva.{operation}",
            "verifier_version": "1.0.0",
            "method_parameters": parameters,
            "source_artifacts": {
                "source_docket_ids": list(source_resolution.source_docket_ids),
                "source_snapshot_hash": source_snapshot_hash,
            },
            "steps": [
                {
                    "operation": "canonicalize_query",
                    "output_hash": f"sha256:{canonical_json_hash(canonical_query)}",
                },
                {
                    "operation": replay_step,
                    "output_hash": f"sha256:{canonical_json_hash(result)}",
                },
            ],
        },
        "witness": witness.as_dict(),
    }
    capsule["witness_hash"] = witness.witness_id
    return capsule


def build_convert_bs_to_ad_capsule(year: int, month: int, day: int) -> dict[str, Any]:
    result = {"ad_date": bs_to_gregorian(year, month, day).isoformat()}
    return _build_capsule(
        operation="convert_bs_to_ad",
        input_payload={"year": year, "month": month, "day": day},
        context={"calendar": "BS", "policy_id": "canonical@0.1.0"},
        result=result,
        source_resolution=resolve_convert_bs_to_ad_source(year, month, day),
        derivation="source_lookup" if result else "deterministic_conversion_without_source_coverage",
        replay_step="convert_bs_to_ad",
        method_parameters={"calendar": "BS"},
    )


def build_ad_to_bs_capsule(ad_date: date) -> dict[str, Any]:
    bs_year, bs_month, bs_day = gregorian_to_bs(ad_date)
    result = {
        "bs_date": _date_key(bs_year, bs_month, bs_day),
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
    }
    return _build_capsule(
        operation="ad_to_bs",
        input_payload={"ad_date": ad_date.isoformat()},
        context={"calendar": "AD", "policy_id": "canonical@0.1.0"},
        result=result,
        source_resolution=resolve_ad_to_bs_source(bs_year, bs_month, bs_day),
        derivation="inverse_conversion_replay",
        replay_step="ad_to_bs",
        method_parameters={"calendar": "AD"},
    )


def _validate_bs_result(year: int, month: int, day: int) -> dict[str, Any]:
    try:
        max_day = days_in_bs_month(year, month)
    except ValueError as exc:
        return {
            "valid": False,
            "bs_date": _date_key(year, month, day),
            "reason": str(exc),
            "year": year,
            "month": month,
            "day": day,
            "max_day": None,
        }
    valid = is_valid_bs_date(year, month, day)
    return {
        "valid": valid,
        "bs_date": _date_key(year, month, day),
        "reason": "valid" if valid else f"day must be between 1 and {max_day}",
        "year": year,
        "month": month,
        "day": day,
        "max_day": max_day,
    }


def build_validate_bs_date_capsule(year: int, month: int, day: int) -> dict[str, Any]:
    result = _validate_bs_result(year, month, day)
    return _build_capsule(
        operation="validate_bs_date",
        input_payload={"year": year, "month": month, "day": day},
        context={"calendar": "BS", "policy_id": "canonical@0.1.0"},
        result=result,
        source_resolution=resolve_validate_bs_date_source(year, month, day),
        derivation="month_length_boundary_check",
        replay_step="validate_bs_date",
        membrane_kind="positive" if result["valid"] else "negative",
        method_parameters={"calendar": "BS"},
    )


def _holiday_result(year: int, month: int, day: int, profile_id: str) -> dict[str, Any]:
    from app.services.compliance_service import FIXED_BS_PUBLIC_HOLIDAYS

    holiday = FIXED_BS_PUBLIC_HOLIDAYS.get((month, day))
    source_set = "public_fixed_date_corpus"
    index_payload = {
        "source_set": source_set,
        "holidays": sorted(f"{m:02d}-{d:02d}:{item['holiday_id']}" for (m, d), item in FIXED_BS_PUBLIC_HOLIDAYS.items()),
    }
    return {
        "bs_date": _date_key(year, month, day),
        "profile_id": profile_id,
        "is_holiday": holiday is not None,
        "holiday": dict(holiday) if holiday else None,
        "source_set": source_set,
        "membership_key": f"{month:02d}-{day:02d}",
        "membership_proof": {
            "claim_index_hash": f"sha256:{canonical_json_hash(index_payload)}",
            "proof_type": "membership" if holiday else "non_membership",
        },
    }


def build_holiday_capsule(
    year: int,
    month: int,
    day: int,
    *,
    profile_id: str = "nepal_public_general",
) -> dict[str, Any]:
    result = _holiday_result(year, month, day, profile_id)
    source_resolution = resolve_holiday_source(year, month, day)
    return _build_capsule(
        operation="holiday",
        input_payload={"year": year, "month": month, "day": day, "profile_id": profile_id},
        context={"calendar": "BS", "policy_id": "canonical@0.1.0", "jurisdiction": "NP"},
        result=result,
        source_resolution=source_resolution,
        derivation="fixed_public_corpus_membership",
        replay_step="holiday_membership",
        membrane_kind="positive" if result["is_holiday"] else "negative",
        result_authority=AuthorityTaint.STATIC_REFERENCE,
        extra_flags=frozenset({TaintFlag.REVIEW_REQUIRED}),
        method_parameters={"profile_id": profile_id, "source_set": result["source_set"]},
        policy_notes=["public fixed-date holiday corpus is decision support, not an official holiday notice"],
    )


def _working_day_result(year: int, month: int, day: int, profile_id: str, decision_intent: str) -> dict[str, Any]:
    from app.services.compliance_service import evaluate_date_payload

    payload = evaluate_date_payload(
        profile_id=profile_id,
        bs_date=_date_key(year, month, day),
        decision_intent=decision_intent,
        trace_id=None,
    )
    decision = payload["decision"]
    return {
        "bs_date": _date_key(year, month, day),
        "ad_date": payload["date"]["ad"],
        "profile_id": profile_id,
        "decision_intent": decision_intent,
        "is_working_day": decision["is_working_day"],
        "is_business_day": decision["is_business_day"],
        "requires_human_review": decision["requires_human_review"],
        "reason_codes": decision["reason_codes"],
        "holiday": decision["holiday"],
    }


def build_working_day_capsule(
    year: int,
    month: int,
    day: int,
    *,
    profile_id: str = "nepal_private_company_default",
    decision_intent: str = "general",
) -> dict[str, Any]:
    result = _working_day_result(year, month, day, profile_id, decision_intent)
    return _build_capsule(
        operation="working_day",
        input_payload={
            "year": year,
            "month": month,
            "day": day,
            "profile_id": profile_id,
            "decision_intent": decision_intent,
        },
        context={"calendar": "BS", "policy_id": "canonical@0.1.0", "jurisdiction": "NP"},
        result=result,
        source_resolution=resolve_working_day_source(year, month, day),
        derivation="weekday_policy_plus_public_holiday_overlay",
        replay_step="working_day_policy",
        membrane_kind="positive" if result["is_working_day"] else "negative",
        result_authority=AuthorityTaint.COMPUTED_UNCERTIFIED,
        extra_flags=frozenset({TaintFlag.REVIEW_REQUIRED}) if result["requires_human_review"] else frozenset(),
        method_parameters={"profile_id": profile_id, "decision_intent": decision_intent},
        policy_notes=["working-day results are decision support and must not be used as final payroll/legal authority"],
    )


def build_fiscal_year_capsule(bs_year: int) -> dict[str, Any]:
    from app.services.enterprise_calendar_service import fiscal_year_payload

    payload = fiscal_year_payload(bs_year, trace_id=None)
    result = {
        "fiscal_year": payload["fiscal_year"],
        "start": payload["start"],
        "end": payload["end"],
        "basis": payload["basis"],
    }
    return _build_capsule(
        operation="fiscal_year",
        input_payload={"bs_year": bs_year},
        context={"calendar": "BS", "policy_id": "canonical@0.1.0", "jurisdiction": "NP"},
        result=result,
        source_resolution=resolve_fiscal_year_source(bs_year),
        derivation="nepali_fiscal_boundary_rule",
        replay_step="fiscal_year_rule",
        result_authority=AuthorityTaint.COMPUTED_UNCERTIFIED,
        extra_flags=frozenset({TaintFlag.REVIEW_REQUIRED}),
        method_parameters={"fiscal_year_start": "BS-04-01"},
        policy_notes=["fiscal-year output is decision support, not legal or tax authority"],
    )


def build_bs_months_capsule(bs_year: int, *, mode: str = "canonical") -> dict[str, Any]:
    from app.services.bs_month_metadata_service import BsMonthCalculationMode
    from app.services.enterprise_calendar_service import bs_months_payload

    payload = bs_months_payload(bs_year, mode=cast(BsMonthCalculationMode, mode), trace_id=None)
    result = {
        "bs_year": payload["bs_year"],
        "requested_mode": payload["requested_mode"],
        "selected_method": payload.get("selected_method"),
        "total_days": payload.get("total_days"),
        "months": payload.get("months"),
        "branch_set": payload.get("branch_set"),
        "branches": payload.get("branches"),
        "policy_decision": payload.get("policy_decision"),
    }
    authority = AuthorityTaint.STATIC_REFERENCE if mode == "static_lookup" else AuthorityTaint.COMPUTED_UNCERTIFIED
    return _build_capsule(
        operation="bs_months",
        input_payload={"bs_year": bs_year, "mode": mode},
        context={"calendar": "BS", "policy_id": "canonical@0.1.0"},
        result=result,
        source_resolution=resolve_bs_months_source(bs_year, mode),
        derivation="bs_month_metadata_branch_evaluation",
        replay_step="bs_months_metadata",
        membrane_kind="branch_set" if mode == "compare" else "positive",
        result_authority=authority,
        extra_flags=frozenset({TaintFlag.REVIEW_REQUIRED}),
        method_parameters={"mode": mode},
        policy_notes=["static lookup is explicit reference mode and does not become source-backed authority"],
    )


__all__ = [
    "_proof_requested",
    "build_ad_to_bs_capsule",
    "build_bs_months_capsule",
    "build_convert_bs_to_ad_capsule",
    "build_fiscal_year_capsule",
    "build_holiday_capsule",
    "build_validate_bs_date_capsule",
    "build_working_day_capsule",
    "proof_response",
]
