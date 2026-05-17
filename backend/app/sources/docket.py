"""Source docket schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceArtifactRef:
    path: str
    sha256: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "sha256": self.sha256}


@dataclass(frozen=True)
class SourceDocket:
    source_id: str
    issuer: str
    source_type: str
    authority_class: str
    raw_artifact: SourceArtifactRef
    acquired_at: str
    acquisition_method: str
    original_url: str | None
    normalized_output: SourceArtifactRef
    review_status: str
    review_witnesses: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "source_docket",
            "source_id": self.source_id,
            "issuer": self.issuer,
            "source_type": self.source_type,
            "authority_class": self.authority_class,
            "raw_artifact": self.raw_artifact.as_dict(),
            "acquired_at": self.acquired_at,
            "acquisition_method": self.acquisition_method,
            "original_url": self.original_url,
            "normalized_output": self.normalized_output.as_dict(),
            "review_status": self.review_status,
            "review_witnesses": list(self.review_witnesses),
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SourceDocket":
        if payload.get("kind") != "source_docket":
            raise ValueError("source docket kind must be source_docket")
        required = [
            "source_id",
            "issuer",
            "source_type",
            "authority_class",
            "raw_artifact",
            "acquired_at",
            "acquisition_method",
            "normalized_output",
            "review_status",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"missing source docket fields: {', '.join(missing)}")
        return cls(
            source_id=str(payload["source_id"]),
            issuer=str(payload["issuer"]),
            source_type=str(payload["source_type"]),
            authority_class=str(payload["authority_class"]),
            raw_artifact=SourceArtifactRef(**payload["raw_artifact"]),
            acquired_at=str(payload["acquired_at"]),
            acquisition_method=str(payload["acquisition_method"]),
            original_url=payload.get("original_url"),
            normalized_output=SourceArtifactRef(**payload["normalized_output"]),
            review_status=str(payload["review_status"]),
            review_witnesses=tuple(payload.get("review_witnesses") or ()),
            notes=tuple(payload.get("notes") or ()),
        )
