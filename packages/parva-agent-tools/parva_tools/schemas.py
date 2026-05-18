"""Tool schemas for public-safe Parva temporal calls."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class ParvaToolSpec:
    name: str
    description: str
    method: Literal["GET", "POST"]
    route: str
    input_schema: dict[str, Any]
    output_contract: tuple[str, ...] = (
        "answer",
        "source_tier",
        "confidence",
        "supported_range",
        "claim_boundary",
        "review_required",
        "not_authority",
    )

    def descriptor(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["read_only"] = True
        payload["authority_boundary"] = (
            "Decision support only. Parva is not an official, legal, tax, "
            "banking, payroll, government, or religious authority."
        )
        return payload


TOOL_SPECS: tuple[ParvaToolSpec, ...] = (
    ParvaToolSpec(
        name="parva_convert_bs_to_ad",
        description="Convert a supported BS date to AD with source and boundary metadata.",
        method="POST",
        route="/v3/api/calendar/bs-to-gregorian",
        input_schema={
            "type": "object",
            "required": ["year", "month", "day"],
            "properties": {
                "year": {"type": "integer"},
                "month": {"type": "integer"},
                "day": {"type": "integer"},
            },
        },
    ),
    ParvaToolSpec(
        name="parva_convert_ad_to_bs",
        description="Convert a supported AD date to BS with source and boundary metadata.",
        method="GET",
        route="/v3/api/calendar/convert",
        input_schema={
            "type": "object",
            "required": ["date"],
            "properties": {"date": {"type": "string", "format": "date"}},
        },
    ),
    ParvaToolSpec(
        name="parva_get_today_nepali_date",
        description="Return today's Nepali calendar context from the public calendar route.",
        method="GET",
        route="/v3/api/calendar/today",
        input_schema={"type": "object", "properties": {"risk_mode": {"type": "string"}}},
    ),
    ParvaToolSpec(
        name="parva_check_holiday",
        description="Check a date against a public-safe institution profile and keep review gates.",
        method="POST",
        route="/v3/api/compliance/evaluate-date",
        input_schema={
            "type": "object",
            "properties": {
                "profile_id": {"type": "string"},
                "bs_date": {"type": "string"},
                "ad_date": {"type": "string"},
            },
        },
    ),
    ParvaToolSpec(
        name="parva_get_working_day_status",
        description="Evaluate public-safe working-day status with profile and review metadata.",
        method="POST",
        route="/v3/api/compliance/evaluate-date",
        input_schema={
            "type": "object",
            "properties": {
                "profile_id": {"type": "string"},
                "bs_date": {"type": "string"},
                "ad_date": {"type": "string"},
                "decision_intent": {"type": "string"},
            },
        },
    ),
    ParvaToolSpec(
        name="parva_get_fiscal_year",
        description="Return Nepali fiscal-year boundaries for a supported BS year.",
        method="GET",
        route="/v3/api/enterprise/fiscal-year/{bs_year}",
        input_schema={
            "type": "object",
            "required": ["bs_year"],
            "properties": {"bs_year": {"type": "integer"}},
        },
    ),
    ParvaToolSpec(
        name="parva_get_festival_date",
        description="Return public-safe festival date metadata for a supported festival and year.",
        method="GET",
        route="/v3/api/festivals/{festival_id}",
        input_schema={
            "type": "object",
            "required": ["festival_id", "year"],
            "properties": {
                "festival_id": {"type": "string"},
                "year": {"type": "integer"},
            },
        },
    ),
    ParvaToolSpec(
        name="parva_get_panchanga_summary",
        description="Return computed panchanga summary metadata for a supported AD date.",
        method="GET",
        route="/v3/api/calendar/panchanga",
        input_schema={
            "type": "object",
            "required": ["date"],
            "properties": {"date": {"type": "string", "format": "date"}},
        },
    ),
    ParvaToolSpec(
        name="parva_check_temporal_claim",
        description="Check a temporal claim using public-safe decision support and review gates.",
        method="POST",
        route="/v3/api/agent/verify-claim",
        input_schema={
            "type": "object",
            "required": ["claim"],
            "properties": {
                "claim": {"type": "string"},
                "context": {"type": "object"},
                "include_evidence": {"type": "boolean"},
            },
        },
    ),
)

TOOL_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
