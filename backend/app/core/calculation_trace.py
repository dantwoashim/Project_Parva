"""Public calculation trace model aligned with schemas/calculation-trace.schema.json."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SourcePolicy = Literal[
    "official_strict",
    "printed_reviewed",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "experimental_shadow",
    "public_demo",
]

PublicationStatus = Literal[
    "official_verified",
    "printed_verified",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "needs_review",
    "computed_prediction_not_official",
]

TraceStepStatus = Literal["applied", "skipped", "warning"]


class PublicCalculationTraceStep(BaseModel):
    name: str = Field(min_length=1)
    status: TraceStepStatus
    detail: str | None = None


class PublicCalculationTrace(BaseModel):
    trace_id: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    release_id: str = Field(min_length=1)
    source_policy: SourcePolicy
    steps: list[PublicCalculationTraceStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    publication_status: PublicationStatus


def demo_bs_to_ad_trace() -> PublicCalculationTrace:
    return PublicCalculationTrace(
        trace_id="tr_demo_bs_to_ad_2083_01_01",
        operation="bs_to_ad",
        input={"year": 2083, "month": 1, "day": 1},
        output={"date": "2026-04-14"},
        release_id="parva-bs-public-demo",
        source_policy="public_demo",
        steps=[
            PublicCalculationTraceStep(name="validate_bs_date", status="applied"),
            PublicCalculationTraceStep(name="resolve_month_start", status="applied"),
            PublicCalculationTraceStep(name="add_day_offset", status="applied"),
            PublicCalculationTraceStep(name="project_to_gregorian", status="applied"),
        ],
        warnings=[],
        publication_status="computed_prediction_not_official",
    )


__all__ = [
    "PublicCalculationTrace",
    "PublicCalculationTraceStep",
    "demo_bs_to_ad_trace",
]
