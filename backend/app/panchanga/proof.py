"""Replay-verifiable Panchanga membrane construction."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.boundary.vector import BoundaryVector
from app.canonicalization.normalize import canonical_json, canonicalize_query
from app.membranes.identity import membrane_identity_hash
from app.panchanga.ephemeris_provider import method_dockets, provider_from_id
from app.sources.hashing import canonical_json_hash
from app.trust.field_provenance import FieldProvenance, ProvenanceMap
from app.trust.taint import AuthorityTaint, TaintFlag
from app.witnesses.schema import Witness


def _context(
    *,
    latitude: float,
    longitude: float,
    timezone_name: str,
    provider_id: str,
    fixture_id: str | None,
    ayanamsa: str,
    sunrise_rule: str,
) -> dict[str, Any]:
    return {
        "calendar": "AD",
        "policy_id": "panchanga-computed-not-authority@1.0.0",
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "timezone": timezone_name,
        "ephemeris_provider": provider_id,
        "ephemeris_fixture_id": fixture_id,
        "ayanamsa": ayanamsa,
        "sidereal_mode": "sidereal",
        "sunrise_rule": sunrise_rule,
        "canonicalization_version": "parva-canon-v1",
    }


def panchanga_result_payload(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": str(raw["date"]),
        "sunrise": raw["sunrise"],
        "sunset": raw["sunset"],
        "tithi": raw["tithi"],
        "nakshatra": raw["nakshatra"],
        "yoga": raw["yoga"],
        "karana": raw["karana"],
        "paksha": raw["tithi"]["paksha"],
        "vaara": raw["vaara"],
        "sun": raw["sun"],
        "moon": raw["moon"],
        "publication_status": "computed_not_official",
        "claim_boundary": "computed_ephemeris_not_panchanga_authority",
        "review_required": True,
    }


def _provenance(result: dict[str, Any]) -> ProvenanceMap:
    return ProvenanceMap(
        {
            field: FieldProvenance(
                field,
                AuthorityTaint.COMPUTED_UNCERTIFIED,
                "panchanga_ephemeris_method_replay",
                source_docket_id=None,
                witness_ids=(),
                policy_id="panchanga-computed-not-authority@1.0.0",
                review_state="review_required",
                flags=frozenset({TaintFlag.REVIEW_REQUIRED}),
            )
            for field in result
        }
    )


def build_panchanga_summary_capsule(
    target_date: date,
    *,
    latitude: float = 27.7172,
    longitude: float = 85.3240,
    timezone_name: str = "Asia/Kathmandu",
    provider_id: str = "builtin_swiss_moshier",
    fixture_id: str | None = None,
    ayanamsa: str = "lahiri",
    sunrise_rule: str = "udaya_at_local_sunrise",
) -> dict[str, Any]:
    provider = provider_from_id(provider_id, fixture_id=fixture_id)
    provider_meta = provider.metadata(ayanamsa=ayanamsa)
    raw = provider.panchanga_for(
        target_date,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        ayanamsa=ayanamsa,
    )
    result = panchanga_result_payload(raw)
    context = _context(
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        provider_id=provider_id,
        fixture_id=fixture_id,
        ayanamsa=ayanamsa,
        sunrise_rule=sunrise_rule,
    )
    canonical_query = canonicalize_query(
        {"operation": "panchanga_summary", "input": {"date": target_date.isoformat()}, "context": context}
    )
    provenance = _provenance(result)
    boundary = BoundaryVector.from_provenance(provenance, ignorance_state="known").as_dict()
    boundary.update(
        {
            "claim_boundary": "computed_ephemeris_not_panchanga_authority",
            "review_state": "required",
            "not_authority": True,
            "not_panchanga_authority": True,
            "not_ritual_final_authority": True,
            "location_sensitive": True,
            "ephemeris_method_dependent": True,
        }
    )
    method_refs = [docket["method_id"] for docket in method_dockets()]
    method_parameters = {
        "ephemeris_metadata": provider_meta,
        "method_docket_refs": method_refs,
        "location": {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "timezone": timezone_name,
        },
        "ayanamsa": ayanamsa,
        "sunrise_rule": sunrise_rule,
        "not_authority": True,
    }
    witness = Witness(
        operation="panchanga_summary",
        input_hash=f"sha256:{canonical_json_hash(canonical_query)}",
        output_hash=f"sha256:{canonical_json_hash(result)}",
        verifier="parva.panchanga_summary",
        verifier_version="1.0.0",
        method_parameters=method_parameters,
        source_refs=tuple(method_refs),
    )
    capsule = {
        "kind": "parva_membrane",
        "membrane_kind": "positive",
        "canonical_query": canonical_query,
        "canonical_query_json": canonical_json(canonical_query),
        "identity_hash": membrane_identity_hash(canonical_query),
        "result": result,
        "boundary": boundary,
        "field_provenance": provenance.as_dict(),
        "source_docket_ids": [],
        "method_dockets": method_dockets(),
        "method_docket_refs": method_refs,
        "ephemeris_metadata": provider_meta,
        "policy_trace": {
            "policy_id": "panchanga-computed-not-authority@1.0.0",
            "operation": "panchanga_summary",
            "decision": {
                "authority": AuthorityTaint.COMPUTED_UNCERTIFIED.value,
                "review_required": True,
                "claim_boundary": "computed_ephemeris_not_panchanga_authority",
            },
            "rules": [
                "panchanga_outputs_are_computed_not_official",
                "location_timezone_ephemeris_and_ayanamsa_are_identity_inputs",
                "fallback_provider_cannot_claim_jpl_authority",
                "ritual_final_authority_is_not_claimed",
            ],
        },
        "proof_pack": {
            "level": "replay",
            "verifier": "parva.panchanga_summary",
            "verifier_version": "1.0.0",
            "method_parameters": method_parameters,
            "source_artifacts": {
                "method_docket_refs": method_refs,
                "ephemeris_metadata": provider_meta,
            },
            "steps": [
                {
                    "operation": "canonicalize_query",
                    "output_hash": f"sha256:{canonical_json_hash(canonical_query)}",
                },
                {
                    "operation": "panchanga_summary",
                    "output_hash": f"sha256:{canonical_json_hash(result)}",
                },
            ],
        },
        "witness": witness.as_dict(),
    }
    capsule["witness_hash"] = witness.witness_id
    return capsule


__all__ = ["build_panchanga_summary_capsule", "panchanga_result_payload"]
