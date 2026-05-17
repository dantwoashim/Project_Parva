"""Temporal intermediate representation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalIR:
    intent: str
    entities: tuple[dict, ...]
    constraints: tuple[dict, ...]
    ambiguities: tuple[dict, ...]
    target: str | None
    interpretation_confidence: float
    surface_form: str
    language_surface: str

    def as_dict(self) -> dict:
        return {
            "intent": self.intent,
            "entities": list(self.entities),
            "constraints": list(self.constraints),
            "ambiguities": list(self.ambiguities),
            "target": self.target,
            "interpretation_confidence": self.interpretation_confidence,
            "surface_form": self.surface_form,
            "language_surface": self.language_surface,
        }
