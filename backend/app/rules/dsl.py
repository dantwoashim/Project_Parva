"""Typed Rule DSL for canonical festival rule execution planning.

Month-2 foundation:
- Normalize heterogeneous v4 catalog rows into typed DSL payloads.
- Expose deterministic executability checks for quality gating.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from .schema_v4 import FestivalRuleV4

RuleType = Literal["lunar", "solar", "relative", "transit", "override"]


class LunarRuleDSL(BaseModel):
    lunar_month: Optional[str] = None
    bs_month: Optional[int] = Field(default=None, ge=1, le=12)
    paksha: Optional[str] = None
    tithi: Optional[int] = Field(default=None, ge=1, le=30)
    adhik_policy: str = "skip"


class SolarRuleDSL(BaseModel):
    bs_month: Optional[int] = Field(default=None, ge=1, le=12)
    solar_day: Optional[int] = Field(default=None, ge=1, le=32)
    event: Optional[str] = None


class RelativeRuleDSL(BaseModel):
    anchor_festival_id: Optional[str] = None
    offset_days: int = 0


class TransitRuleDSL(BaseModel):
    body: str = "sun"
    event: Optional[str] = None
    target_rashi: Optional[str] = None
    target_longitude: Optional[float] = None


class OverrideRuleDSL(BaseModel):
    mode: str = "official_override"
    dates: dict[str, str] = Field(default_factory=dict)
    bs_year: Optional[int] = None
    bs_month: Optional[int] = Field(default=None, ge=1, le=12)
    bs_day: Optional[int] = Field(default=None, ge=1, le=32)


class RuleDSLDocument(BaseModel):
    festival_id: str
    rule_type: RuleType
    rule_family: str
    source: str
    status: str
    confidence: str
    executable: bool
    execution_template: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)


def _execution_template(rule: FestivalRuleV4) -> str | None:
    payload = rule.rule or {}
    if rule.rule_type == "lunar":
        if payload.get("lunar_month") and payload.get("paksha") and payload.get("tithi"):
            return "lunar_tithi_window_v1"
        if payload.get("bs_month") and payload.get("paksha") and payload.get("tithi"):
            return "lunar_bs_month_v1"
        return None

    if rule.rule_type == "solar":
        if payload.get("event"):
            return "solar_sankranti_v1"
        if payload.get("bs_month") and payload.get("solar_day"):
            return "solar_bs_fixed_v1"
        return None

    if rule.rule_type == "relative":
        if payload.get("relative_to") and payload.get("offset_days") is not None:
            return "relative_offset_v1"
        return None

    if rule.rule_type == "transit":
        if payload.get("event") or payload.get("target_rashi") or payload.get("target_longitude") is not None:
            return "solar_transit_v1"
        return None

    if rule.rule_type == "override":
        if isinstance(payload.get("dates"), dict) and payload.get("dates"):
            return "official_override_lookup_v1"
        if payload.get("bs_year") and payload.get("bs_month") and payload.get("bs_day"):
            return "official_bs_override_v1"
        return None

    return None


def is_rule_executable(rule: FestivalRuleV4) -> bool:
    """Return whether rule has sufficient parameters for deterministic execution."""
    return _execution_template(rule) is not None


def _payload_for_type(rule: FestivalRuleV4) -> dict[str, Any]:
    payload = rule.rule or {}
    if rule.rule_type == "lunar":
        model = LunarRuleDSL(
            lunar_month=payload.get("lunar_month"),
            bs_month=payload.get("bs_month"),
            paksha=payload.get("paksha"),
            tithi=payload.get("tithi"),
            adhik_policy=payload.get("adhik_policy", "skip"),
        )
        return model.model_dump(exclude_none=True)

    if rule.rule_type == "solar":
        model = SolarRuleDSL(
            bs_month=payload.get("bs_month"),
            solar_day=payload.get("solar_day"),
            event=payload.get("event"),
        )
        return model.model_dump(exclude_none=True)

    if rule.rule_type == "relative":
        model = RelativeRuleDSL(
            anchor_festival_id=payload.get("relative_to") or payload.get("anchor_festival_id"),
            offset_days=payload.get("offset_days", 0),
        )
        return model.model_dump(exclude_none=True)

    if rule.rule_type == "transit":
        model = TransitRuleDSL(
            body=payload.get("body", "sun"),
            event=payload.get("event"),
            target_rashi=payload.get("target_rashi"),
            target_longitude=payload.get("target_longitude"),
        )
        return model.model_dump(exclude_none=True)

    model = OverrideRuleDSL(
        mode=payload.get("mode", "official_override"),
        dates=payload.get("dates") if isinstance(payload.get("dates"), dict) else {},
        bs_year=payload.get("bs_year"),
        bs_month=payload.get("bs_month"),
        bs_day=payload.get("bs_day"),
    )
    return model.model_dump(exclude_none=True)


def rule_to_dsl_document(rule: FestivalRuleV4) -> RuleDSLDocument:
    template = _execution_template(rule)
    return RuleDSLDocument(
        festival_id=rule.festival_id,
        rule_type=rule.rule_type,
        rule_family=rule.rule_family,
        source=rule.source,
        status=rule.status,
        confidence=rule.confidence,
        executable=template is not None,
        execution_template=template,
        payload=_payload_for_type(rule),
    )
