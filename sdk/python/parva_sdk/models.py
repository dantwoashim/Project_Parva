"""Typed response models for the Project Parva Python SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass
class ConfidenceMeta:
    level: str = "unknown"
    score: Optional[float] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ConfidenceMeta":
        return cls(
            level=str(payload.get("level", "unknown")),
            score=payload.get("score"),
        )


@dataclass
class ProvenanceMeta:
    snapshot_id: Optional[str] = None
    dataset_hash: Optional[str] = None
    rules_hash: Optional[str] = None
    verify_url: Optional[str] = None
    signature: Optional[str] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ProvenanceMeta":
        return cls(
            snapshot_id=payload.get("snapshot_id"),
            dataset_hash=payload.get("dataset_hash"),
            rules_hash=payload.get("rules_hash"),
            verify_url=payload.get("verify_url"),
            signature=payload.get("signature"),
        )


@dataclass
class UncertaintyMeta:
    interval_hours: Optional[float] = None
    boundary_risk: str = "unknown"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UncertaintyMeta":
        return cls(
            interval_hours=payload.get("interval_hours"),
            boundary_risk=str(payload.get("boundary_risk", "unknown")),
        )


@dataclass
class PolicyMeta:
    profile: Optional[str] = None
    jurisdiction: Optional[str] = None
    advisory: Optional[bool] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PolicyMeta":
        return cls(
            profile=payload.get("profile"),
            jurisdiction=payload.get("jurisdiction"),
            advisory=payload.get("advisory"),
        )


@dataclass
class ResponseMeta:
    confidence: ConfidenceMeta = field(default_factory=ConfidenceMeta)
    method: str = "unknown"
    provenance: ProvenanceMeta = field(default_factory=ProvenanceMeta)
    uncertainty: UncertaintyMeta = field(default_factory=UncertaintyMeta)
    trace_id: Optional[str] = None
    policy: PolicyMeta = field(default_factory=PolicyMeta)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ResponseMeta":
        confidence_block = payload.get("confidence")
        if isinstance(confidence_block, dict):
            confidence = ConfidenceMeta.from_dict(confidence_block)
        else:
            confidence = ConfidenceMeta(level=str(confidence_block or "unknown"), score=None)

        return cls(
            confidence=confidence,
            method=str(payload.get("method", "unknown")),
            provenance=ProvenanceMeta.from_dict(
                payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
            ),
            uncertainty=UncertaintyMeta.from_dict(
                payload.get("uncertainty") if isinstance(payload.get("uncertainty"), dict) else {}
            ),
            trace_id=payload.get("trace_id"),
            policy=PolicyMeta.from_dict(payload.get("policy") if isinstance(payload.get("policy"), dict) else {}),
        )


@dataclass
class DataEnvelope(Generic[T]):
    data: T
    meta: ResponseMeta = field(default_factory=ResponseMeta)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DataEnvelope[Dict[str, Any]]":
        if "data" in payload and "meta" in payload:
            return cls(
                data=payload.get("data"),
                meta=ResponseMeta.from_dict(payload.get("meta") if isinstance(payload.get("meta"), dict) else {}),
            )
        # Compatibility mode for v3 payloads.
        return cls(data=payload, meta=ResponseMeta())
