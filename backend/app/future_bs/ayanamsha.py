"""Ayanamsha candidates for future BS sensitivity analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AyanamshaCandidate:
    name: str
    label: str
    offset_arcseconds: float = 0.0
    status: str = "candidate"

    def payload(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "offset_arcseconds": self.offset_arcseconds,
            "status": self.status,
        }


AYANAMSHA_CANDIDATES = {
    "lahiri": AyanamshaCandidate("lahiri", "Lahiri / Chitra Paksha", status="active"),
    "raman": AyanamshaCandidate("raman", "Raman", status="sensitivity_candidate"),
    "krishnamurti": AyanamshaCandidate("krishnamurti", "Krishnamurti", status="sensitivity_candidate"),
    "calibrated_offset": AyanamshaCandidate(
        "calibrated_offset",
        "Calibrated offset placeholder",
        status="requires_calibration",
    ),
    "committee_aligned_offset": AyanamshaCandidate(
        "committee_aligned_offset",
        "Committee-aligned offset placeholder",
        status="requires_discovery",
    ),
}


def candidate_payloads() -> list[dict]:
    return [candidate.payload() for candidate in AYANAMSHA_CANDIDATES.values()]
