from __future__ import annotations

import pytest
from app.calendar.bikram_sambat import days_in_bs_month
from app.calendar.sankranti import compute_bs_month_lengths
from app.services.bs_month_metadata_service import build_bs_month_metadata


def test_solar_civil_month_metadata_is_default_computation_base() -> None:
    payload = build_bs_month_metadata(2082)

    assert payload["calculation_mode"] == "solar_civil"
    assert payload["engine"] == "solar_civil_sankranti_v1"
    assert [row["days"] for row in payload["months"]] == compute_bs_month_lengths(2082)
    assert payload["confidence"] == "solar_civil_computed"
    assert payload["source_status"] == "computed_solar_civil"
    assert all(row["not_authority"] is True for row in payload["months"])


def test_static_lookup_is_explicit_compatibility_mode() -> None:
    payload = build_bs_month_metadata(2082, mode="static_lookup")

    assert payload["calculation_mode"] == "static_lookup"
    assert payload["engine"] == "static_lookup_compatibility_v1"
    assert [row["days"] for row in payload["months"]] == [
        days_in_bs_month(2082, month) for month in range(1, 13)
    ]


def test_unknown_month_metadata_mode_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_bs_month_metadata(2082, mode="table")  # type: ignore[arg-type]
