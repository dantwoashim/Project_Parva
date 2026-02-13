"""Week 23 validation for extended-range BS sample fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "fixtures"


def _load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_historical_samples_roundtrip_stability():
    data = _load("bs_historical.json")
    assert len(data["samples"]) >= 5
    for row in data["samples"]:
        assert abs(row["roundtrip_delta_days"]) <= 2
        assert row["confidence"] in {"official", "estimated"}


def test_future_samples_roundtrip_stability():
    data = _load("bs_future_projection.json")
    assert len(data["samples"]) >= 5
    for row in data["samples"]:
        assert abs(row["roundtrip_delta_days"]) <= 2
        assert row["confidence"] in {"official", "estimated"}
