"""Core v5 authority-track types."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class RuleQualityBand(BaseModel):
    level: Literal["proposed", "provisional", "computed", "gold"]
    score: float = Field(ge=0.0, le=1.0)
    rationale: Optional[str] = None


class FestivalRuleV5(BaseModel):
    festival_id: str
    rule_family: str
    rule_type: str
    source: str
    quality_band: RuleQualityBand


class ProvenanceMetaV2(BaseModel):
    snapshot_id: Optional[str] = None
    dataset_hash: Optional[str] = None
    rules_hash: Optional[str] = None
    signature: Optional[str] = None
    verify_url: Optional[str] = None


class VariantCoverageMeta(BaseModel):
    available_profiles: int = 0
    profiles_with_variant: int = 0
    profile_coverage_pct: float = 0.0
    variant_count: int = 0
    missing_profiles: List[str] = Field(default_factory=list)
    rule_family: str = "unknown"
    rule_source: str = "unknown"


class ConfidenceScore(BaseModel):
    level: Literal["official", "computed", "estimated", "unknown"] = "unknown"
    score: float = Field(default=0.0, ge=0.0, le=1.0)


class UncertaintyMetaV2(BaseModel):
    interval_hours: Optional[float] = None
    boundary_risk: Literal["low", "medium", "high", "unknown"] = "unknown"


class PolicyMetaV2(BaseModel):
    profile: str = "np-mainstream"
    jurisdiction: str = "NP"
    advisory: bool = True


class CalculationTraceV2(BaseModel):
    trace_id: str
    trace_type: str
    subject: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ResolveResult(BaseModel):
    date: str
    profile: str
    location: Dict[str, Any] = Field(default_factory=dict)
    bikram_sambat: Dict[str, Any] = Field(default_factory=dict)
    tithi: Dict[str, Any] = Field(default_factory=dict)
    panchanga: Dict[str, Any] = Field(default_factory=dict)
    observances: List[Dict[str, Any]] = Field(default_factory=list)
    trace: Optional[CalculationTraceV2] = None
