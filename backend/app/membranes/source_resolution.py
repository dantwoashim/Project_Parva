"""Membrane-facing source resolution helpers."""

from __future__ import annotations

from app.sources.coverage import SourceCoverageResolution, resolve_bs_date_source
from app.trust.taint import AuthorityTaint


def resolve_convert_bs_to_ad_source(year: int, month: int, day: int) -> SourceCoverageResolution:
    return resolve_bs_date_source("convert_bs_to_ad", year=year, month=month, day=day)


def resolve_ad_to_bs_source(year: int, month: int, day: int) -> SourceCoverageResolution:
    return resolve_bs_date_source("ad_to_bs", year=year, month=month, day=day)


def resolve_validate_bs_date_source(year: int, month: int, day: int) -> SourceCoverageResolution:
    return resolve_bs_date_source("validate_bs_date", year=year, month=month, day=day)


def resolve_holiday_source(year: int, month: int, day: int) -> SourceCoverageResolution:
    resolution = resolve_bs_date_source("holiday", year=year, month=month, day=day)
    return SourceCoverageResolution(
        operation="holiday",
        bs_date=resolution.bs_date,
        authority=resolution.authority,
        coverage_status=resolution.coverage_status,
        review_required=True,
        source_docket_ids=resolution.source_docket_ids,
        source_refs=resolution.source_refs,
        review_witnesses=resolution.review_witnesses,
        claim_boundary="decision_support_not_authority",
        reason=resolution.reason,
        eligible_official=resolution.eligible_official,
    )


def resolve_working_day_source(year: int, month: int, day: int) -> SourceCoverageResolution:
    resolution = resolve_bs_date_source("working_day", year=year, month=month, day=day)
    return SourceCoverageResolution(
        operation="working_day",
        bs_date=resolution.bs_date,
        authority=resolution.authority,
        coverage_status=resolution.coverage_status,
        review_required=True,
        source_docket_ids=resolution.source_docket_ids,
        source_refs=resolution.source_refs,
        review_witnesses=resolution.review_witnesses,
        claim_boundary="decision_support_not_legal_tax_payroll_authority",
        reason=resolution.reason,
        eligible_official=resolution.eligible_official,
    )


def resolve_fiscal_year_source(year: int) -> SourceCoverageResolution:
    resolution = resolve_bs_date_source("fiscal_year", year=year, month=4, day=1)
    if resolution.eligible_official:
        return resolution
    return SourceCoverageResolution(
        operation="fiscal_year",
        bs_date=f"{year:04d}-04-01",
        authority=AuthorityTaint.COMPUTED_UNCERTIFIED,
        coverage_status=resolution.coverage_status,
        review_required=True,
        source_docket_ids=resolution.source_docket_ids,
        source_refs=resolution.source_refs,
        review_witnesses=resolution.review_witnesses,
        claim_boundary="decision_support_not_legal_tax_payroll_authority",
        reason=resolution.reason,
        eligible_official=False,
    )


def resolve_bs_months_source(year: int, mode: str) -> SourceCoverageResolution:
    resolution = resolve_bs_date_source("bs_months", year=year, month=1, day=1)
    if mode == "static_lookup":
        return SourceCoverageResolution(
            operation="bs_months",
            bs_date=f"{year:04d}-01-01",
            authority=AuthorityTaint.STATIC_REFERENCE,
            coverage_status="static_lookup_reference_not_source_backed",
            review_required=True,
            source_docket_ids=(),
            source_refs=(),
            review_witnesses=(),
            claim_boundary="static_reference_not_authority",
            reason="static_lookup_mode_is_explicit_reference_mode",
            eligible_official=False,
        )
    if resolution.eligible_official and mode in {"canonical", "compare"}:
        return resolution
    return SourceCoverageResolution(
        operation="bs_months",
        bs_date=f"{year:04d}-01-01",
        authority=AuthorityTaint.COMPUTED_UNCERTIFIED,
        coverage_status=resolution.coverage_status,
        review_required=True,
        source_docket_ids=resolution.source_docket_ids if resolution.authority == AuthorityTaint.STATIC_REFERENCE else (),
        source_refs=resolution.source_refs if resolution.authority == AuthorityTaint.STATIC_REFERENCE else (),
        review_witnesses=resolution.review_witnesses,
        claim_boundary=(
            "branch_set_model_risk_not_authority"
            if mode == "compare"
            else "computed_solar_civil_or_reference_not_authority"
        ),
        reason=resolution.reason,
        eligible_official=False,
    )


__all__ = [
    "resolve_ad_to_bs_source",
    "resolve_bs_months_source",
    "resolve_convert_bs_to_ad_source",
    "resolve_fiscal_year_source",
    "resolve_holiday_source",
    "resolve_validate_bs_date_source",
    "resolve_working_day_source",
]
