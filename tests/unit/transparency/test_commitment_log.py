from __future__ import annotations

from app.conformance.badges import generate_badge
from app.transparency.commitment import forecast_commitment
from app.transparency.scoreboard import resolve_forecast


def test_commitment_log_records_non_official_forecast_and_resolution() -> None:
    commitment = forecast_commitment({"bs_year": 2096, "prediction": "sample"})
    assert commitment["publication_status"] == "computed_prediction_not_official"
    resolved = resolve_forecast(commitment, {"status": "later_reviewed"})
    assert resolved["official_authority"] is False


def test_conformance_badge_is_not_certification() -> None:
    badge = generate_badge({"capsule_id": "payroll_core_2082", "status": "pass"})
    assert badge["witness_hash"].startswith("sha256:")
    assert badge["claim_boundary"] == "badge_is_self_attested_not_certification"
