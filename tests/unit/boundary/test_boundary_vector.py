from __future__ import annotations

from app.boundary.vector import BoundaryVector
from app.trust.taint import AuthorityTaint


def test_boundary_vector_serializes_blocked_use_cases() -> None:
    vector = BoundaryVector(authority=AuthorityTaint.COMPUTED_UNCERTIFIED)
    payload = vector.as_dict()
    assert payload["authority"] == "computed_uncertified"
    assert "payroll_final_authority" in payload["blocked_use_cases"]


def test_phase_03_boundary_axes_are_serialized() -> None:
    payload = BoundaryVector(authority=AuthorityTaint.COMPUTED_UNCERTIFIED).as_dict()
    required = {
        "derivation",
        "authority",
        "temporal_scope",
        "geography_scope",
        "conflict_state",
        "review_state",
        "reproducibility",
        "interpretation_state",
        "freshness",
        "ignorance_state",
        "valid_for",
        "blocked_use_cases",
        "warnings",
    }
    assert required.issubset(payload)
