"""Hard-case benchmark summary for false-confidence control."""

from __future__ import annotations

from typing import Any

from .adversarial_boundary_generator import generate_adversarial_boundary_cases

PUBLICATION_STATUS = "computed_prediction_not_official"


def build_hard_case_benchmark(limit: int = 100) -> dict[str, Any]:
    cases = generate_adversarial_boundary_cases(limit=limit)
    return {
        "publication_status": PUBLICATION_STATUS,
        "case_count": len(cases),
        "hard_case_families": [
            "Ashwin/Kartik boundary",
            "source disagreement",
            "fragile or invalid reconstructed year totals",
            "2083-style operational risk",
        ],
        "cases": cases,
        "risk_policy": "Hard cases cannot be GREEN unless prediction set is single-valued and all certification checks pass.",
    }
