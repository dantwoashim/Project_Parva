"""Ignorance algebra for structured non-answer states."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class IgnoranceKind(StrEnum):
    UNTOUCHED = "untouched"
    UNDER_SPECIFIED = "under_specified"
    INTERPRETATION_AMBIGUOUS = "interpretation_ambiguous"
    SOURCE_UNCONSULTED = "source_unconsulted"
    KNOWN = "known"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    AMBIGUOUS = "ambiguous"
    SOURCE_SILENT = "source_silent"
    SOURCE_EXHAUSTED = "source_exhausted"
    SOURCE_CONFLICT = "source_conflict"
    AUTHORITY_DEFERRED = "authority_deferred"
    TEMPORALLY_PRECLUDED = "temporally_precluded"
    RESOLVED = "resolved"


IGNORANCE_ORDER = {
    IgnoranceKind.RESOLVED: 0,
    IgnoranceKind.KNOWN: 0,
    IgnoranceKind.UNTOUCHED: 1,
    IgnoranceKind.UNDER_SPECIFIED: 2,
    IgnoranceKind.SOURCE_UNCONSULTED: 3,
    IgnoranceKind.SOURCE_SILENT: 4,
    IgnoranceKind.SOURCE_EXHAUSTED: 5,
    IgnoranceKind.INTERPRETATION_AMBIGUOUS: 6,
    IgnoranceKind.AMBIGUOUS: 6,
    IgnoranceKind.AUTHORITY_DEFERRED: 7,
    IgnoranceKind.TEMPORALLY_PRECLUDED: 8,
    IgnoranceKind.SOURCE_CONFLICT: 9,
    IgnoranceKind.UNKNOWN: 10,
    IgnoranceKind.UNSUPPORTED: 10,
}


@dataclass(frozen=True)
class IgnoranceState:
    kind: IgnoranceKind
    reason: str
    review_required: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "reason": self.reason,
            "review_required": self.review_required,
        }


def compose_ignorance(*states: IgnoranceState) -> IgnoranceState:
    if not states:
        return IgnoranceState(IgnoranceKind.RESOLVED, "no_ignorance")
    selected = max(states, key=lambda state: IGNORANCE_ORDER[state.kind])
    return IgnoranceState(
        selected.kind,
        "; ".join(state.reason for state in states if state.reason),
        any(state.review_required for state in states),
    )
