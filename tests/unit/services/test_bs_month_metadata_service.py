from __future__ import annotations

import pytest
from app.calendar.bikram_sambat import days_in_bs_month
from app.calendar.sankranti import compute_bs_month_lengths
from app.services.bs_month_metadata_service import build_bs_month_metadata


def test_canonical_month_metadata_prefers_verified_source_data() -> None:
    payload = build_bs_month_metadata(2082)

    assert payload["calculation_mode"] == "canonical"
    assert payload["selected_mode"] == "source_backed_lookup"
    assert payload["engine"] == "bs_month_canonical_policy_v1"
    assert [row["days"] for row in payload["months"]] == [
        days_in_bs_month(2082, month) for month in range(1, 13)
    ]
    assert payload["confidence"] == "official_verified"
    assert payload["source_status"] == "structured_official"
    assert payload["review_required"] is False
    assert all(row["not_authority"] is True for row in payload["months"])


def test_solar_civil_mode_remains_explicit_computation_base() -> None:
    payload = build_bs_month_metadata(2082, mode="solar_civil")

    assert payload["calculation_mode"] == "solar_civil"
    assert payload["engine"] == "solar_civil_sankranti_v1"
    assert [row["days"] for row in payload["months"]] == compute_bs_month_lengths(2082)
    assert payload["confidence"] == "solar_civil_computed"
    assert payload["review_required"] is True


def test_static_lookup_is_explicit_compatibility_mode() -> None:
    payload = build_bs_month_metadata(2082, mode="static_lookup")

    assert payload["calculation_mode"] == "static_lookup"
    assert payload["engine"] == "static_lookup_compatibility_v1"
    assert payload["confidence"] == "static_lookup_unverified"
    assert payload["source_status"] == "static_reference"
    assert payload["authority"] == "static_reference"
    assert payload["review_required"] is True
    assert [row["days"] for row in payload["months"]] == [
        days_in_bs_month(2082, month) for month in range(1, 13)
    ]


def test_compare_mode_returns_separate_branches() -> None:
    payload = build_bs_month_metadata(2087, mode="compare")

    assert payload["calculation_mode"] == "compare"
    assert payload["default_branch"] == "canonical"
    assert set(payload["branches"]) == {"canonical", "solar_civil", "static_lookup"}
    assert payload["branches"]["canonical"]["total_days"] == 365
    assert payload["branches"]["solar_civil"]["total_days"] == 365
    assert payload["branches"]["static_lookup"]["total_days"] == 367
    assert payload["disagreement"] is True
    assert payload["review_required"] is True


def test_unknown_month_metadata_mode_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_bs_month_metadata(2082, mode="table")  # type: ignore[arg-type]
