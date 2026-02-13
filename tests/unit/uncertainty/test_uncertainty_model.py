from __future__ import annotations

from app.uncertainty import (
    build_bs_uncertainty,
    build_tithi_uncertainty,
    estimate_boundary_proximity_minutes,
)


def test_bs_uncertainty_official_and_estimated_levels():
    official = build_bs_uncertainty("official")
    estimated = build_bs_uncertainty("estimated", "0-1")

    assert official["level"] == "exact"
    assert estimated["level"] == "estimated"


def test_tithi_uncertainty_boundary_case_widens_interval():
    # progress very close to boundary => <= 30 min expected
    out = build_tithi_uncertainty(method="ephemeris_udaya", confidence="exact", progress=0.01)
    assert out["level"] == "uncertain"
    assert out["interval_hours"] >= 12.0


def test_boundary_proximity_helper():
    assert estimate_boundary_proximity_minutes(None) is None
    value = estimate_boundary_proximity_minutes(0.5)
    assert value is not None
    assert value > 600
