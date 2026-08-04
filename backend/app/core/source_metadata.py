"""Source-aware metadata helpers for public temporal claims."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any

from app.calendar.provenance import BSYearProvenance, get_bs_year_provenance
from app.core.source_authority import normalize_source_tier

PUBLIC_DATA_VERSION = "parva-public-calendar-v1"
PUBLIC_RELEASE_ID = "parva-bs-public-demo"
NOT_LEGAL_AUTHORITY = "calendar_computation_not_legal_authority"
PUBLIC_CORPUS_BOUNDARY = "public_corpus_reference_only"
ASTRONOMY_BOUNDARY = "astronomical_calculation_subject_to_source_model"
RESEARCH_BOUNDARY = "research_preview_not_safe_for_legal_or_payroll_use"
COMPLIANCE_BOUNDARY = "enterprise_decision_support_not_legal_authority"


@dataclass(frozen=True)
class SourceClaim:
    id: str
    label: str
    tier: str
    authority: str
    version: str = PUBLIC_DATA_VERSION
    url: str | None = None
    retrieved_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {key: value for key, value in asdict(self).items() if value is not None}
        payload["tier"] = normalize_source_tier(str(payload.get("tier") or "unknown"))
        return payload


PUBLIC_BS_AD_CORPUS = SourceClaim(
    id="parva_public_bs_ad_corpus",
    label="Parva public BS/AD corpus",
    tier="software_table_reference",
    authority="derived_reference_not_legal_authority",
)
STRUCTURED_OFFICIAL_CORPUS = SourceClaim(
    id="parva_structured_official_bs_window",
    label="Parva structured official BS window",
    tier="official",
    authority="official_notice",
)
STATIC_LOOKUP_TABLE = SourceClaim(
    id="parva_static_lookup_table",
    label="Parva static BS/AD lookup table",
    tier="software_table_reference",
    authority="derived_reference_not_legal_authority",
)
ESTIMATED_CALENDAR_MODEL = SourceClaim(
    id="parva_estimated_calendar_model",
    label="Parva estimated BS/AD calendar model",
    tier="calculated",
    authority="derived_reference_not_legal_authority",
)
ASTRONOMICAL_ENGINE = SourceClaim(
    id="parva_astronomical_engine",
    label="Parva astronomical calculation engine",
    tier="calculated",
    authority="astronomical_calculation",
)
PUBLIC_FESTIVAL_RULES = SourceClaim(
    id="parva_public_festival_rules",
    label="Parva public festival rule set",
    tier="calculated",
    authority="derived_reference_not_legal_authority",
)
ENTERPRISE_COMPLIANCE_PROFILES = SourceClaim(
    id="parva_enterprise_compliance_profiles",
    label="Parva enterprise compliance profile definitions",
    tier="publisher_reference",
    authority="derived_reference_not_legal_authority",
)
FUTURE_BS_RESEARCH = SourceClaim(
    id="parva_future_bs_risk_research",
    label="Parva future-BS risk research layer",
    tier="research_private",
    authority="research_preview",
)
PUBLIC_FUTURE_BS_FORECAST = SourceClaim(
    id="parva_public_future_bs_forecast",
    label="Parva public Future BS research forecast",
    tier="calculated",
    authority="computed_research_preview",
)


def _bs_confidence(provenance: BSYearProvenance) -> str:
    if provenance.confidence == "official" and provenance.source_status == "structured_official":
        return "official_verified"
    if provenance.confidence == "static_lookup":
        return "source_backed"
    if provenance.confidence == "estimated":
        return "calculated"
    return "unknown"


def _bs_source(provenance: BSYearProvenance) -> SourceClaim:
    if provenance.confidence == "official" and provenance.source_status == "structured_official":
        return STRUCTURED_OFFICIAL_CORPUS
    if provenance.source_status == "static_table_unverified":
        return STATIC_LOOKUP_TABLE
    if provenance.confidence == "estimated":
        return ESTIMATED_CALENDAR_MODEL
    return PUBLIC_BS_AD_CORPUS


def _bs_claim_boundary(provenance: BSYearProvenance) -> str:
    if provenance.confidence == "official" and provenance.source_status == "structured_official":
        return "official_source_interpretation_not_legal_advice"
    if provenance.confidence == "estimated":
        return NOT_LEGAL_AUTHORITY
    return PUBLIC_CORPUS_BOUNDARY


def _bs_warnings(provenance: BSYearProvenance) -> list[str]:
    warnings: list[str] = []
    if provenance.source_status == "archived_official_pdf_unstructured":
        warnings.append("official_pdf_archived_but_structured_extraction_not_accepted")
    if provenance.source_status == "static_table_unverified":
        warnings.append("static_lookup_without_structured_official_provenance")
    if provenance.confidence == "estimated":
        warnings.append("outside_static_lookup_range_estimated_result")
    warnings.append("not_legal_tax_or_banking_contract_authority")
    return warnings


def build_claim_meta(
    *,
    source: SourceClaim,
    confidence: str,
    claim_boundary: str,
    trace_id: str | None = None,
    warnings: list[str] | None = None,
    data_version: str = PUBLIC_DATA_VERSION,
    result_class: str | None = None,
) -> dict[str, Any]:
    return {
        "source": source.as_dict(),
        "confidence": confidence,
        "data_version": data_version,
        "release_id": os.getenv("PARVA_ACTIVE_RELEASE_ID", PUBLIC_RELEASE_ID).strip()
        or PUBLIC_RELEASE_ID,
        "claim_boundary": claim_boundary,
        "warnings": list(warnings or []),
        "trace_id": trace_id,
        "result_class": result_class or "temporal_claim",
    }


def build_bs_claim_meta(
    bs_year: int,
    *,
    trace_id: str | None = None,
    result_class: str | None = None,
) -> dict[str, Any]:
    provenance = get_bs_year_provenance(bs_year)
    return build_claim_meta(
        source=_bs_source(provenance),
        confidence=_bs_confidence(provenance),
        claim_boundary=_bs_claim_boundary(provenance),
        warnings=_bs_warnings(provenance),
        trace_id=trace_id,
        result_class=result_class or "bs_ad_calendar_claim",
    )


def build_calculated_claim_meta(
    *,
    trace_id: str | None = None,
    result_class: str,
    source: SourceClaim = ASTRONOMICAL_ENGINE,
    confidence: str = "calculated",
    claim_boundary: str = ASTRONOMY_BOUNDARY,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    default_warnings = ["not_legal_tax_or_banking_contract_authority"]
    if warnings:
        default_warnings.extend(warnings)
    return build_claim_meta(
        source=source,
        confidence=confidence,
        claim_boundary=claim_boundary,
        warnings=default_warnings,
        trace_id=trace_id,
        result_class=result_class,
    )


def build_research_claim_meta(
    *,
    trace_id: str | None = None,
    result_class: str = "future_bs_research_capability",
) -> dict[str, Any]:
    return build_claim_meta(
        source=FUTURE_BS_RESEARCH,
        confidence="research_preview",
        claim_boundary=RESEARCH_BOUNDARY,
        warnings=[
            "computed_prediction_not_official",
            "not_safe_for_legal_tax_payroll_or_banking_contract_authority",
        ],
        trace_id=trace_id,
        result_class=result_class,
    )
