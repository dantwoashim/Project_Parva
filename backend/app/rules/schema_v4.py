"""Canonical festival rule schema (v4).

This schema normalizes legacy and v3 rule sources into a single shape so
coverage/reporting APIs can reason about completeness without tying to one
engine implementation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

RuleType = Literal["lunar", "solar", "relative", "transit", "override"]
RuleStatus = Literal["computed", "override", "provisional"]
RuleConfidence = Literal["high", "medium", "low"]


class FestivalRuleV4(BaseModel):
    """Canonical rule definition for one festival."""

    festival_id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    name_en: str
    name_ne: Optional[str] = None
    rule_type: RuleType
    status: RuleStatus = "computed"
    confidence: RuleConfidence = "medium"

    category: str = "hindu"
    importance: str = "national"
    tradition: Optional[str] = None
    regions: List[str] = Field(default_factory=list)
    rule_family: str = "unknown"
    profile_ids: List[str] = Field(default_factory=list)
    has_variant_profiles: bool = False

    source: str
    engine: str
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Rule payload is intentionally flexible so we can support lunar/solar/
    # relative/transit/override without forcing lossy conversions.
    rule: Dict[str, Any] = Field(default_factory=dict)


class FestivalRuleCatalogV4(BaseModel):
    """Catalog envelope stored on disk for v4 rules."""

    version: int = 4
    generated_at: str
    total_rules: int
    source_files: List[str] = Field(default_factory=list)
    festivals: List[FestivalRuleV4] = Field(default_factory=list)
