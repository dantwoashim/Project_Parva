from __future__ import annotations

import json
from pathlib import Path

from app.bootstrap.app_factory import create_app
from app.future_bs.risk import (
    FutureBSRiskInput,
    RiskLabel,
    assess_month_assumption,
    risk_label_values,
)
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]


def test_risk_labels_are_valid_enum_values():
    assert risk_label_values() == ["GREEN", "YELLOW", "RED"]
    assert {label.value for label in RiskLabel} == {"GREEN", "YELLOW", "RED"}


def test_month_assumption_assessment_hides_corrected_values():
    assessment = assess_month_assumption(
        FutureBSRiskInput(bs_year=9000, bs_month=3, month_length=32, synthetic_example=True)
    ).to_public_dict()

    assert assessment["publication_status"] == "computed_prediction_not_official"
    assert assessment["risk_label"] == "YELLOW"
    assert assessment["corrected_value_included"] is False
    assert "corrected_value" not in assessment
    assert "predicted_days" not in assessment


def test_public_capabilities_has_no_raw_future_values(monkeypatch):
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    client = TestClient(create_app())
    response = client.get("/v4/api/future-bs/capabilities")
    assert response.status_code == 200
    body = response.json()
    serialized = json.dumps(body)

    assert body["publication_status"] == "computed_prediction_not_official"
    assert body["surface"] == "future_bs_risk_research"
    for forbidden in [
        "predicted_days",
        "month_lengths",
        "corrected_value",
        "model-runs",
        "export.csv",
        "export.xlsx",
        "2084",
        "2099",
        "2200",
    ]:
        assert forbidden not in serialized


def test_wrong_green_policy_doc_exists_and_is_careful():
    path = ROOT / "docs" / "future_bs" / "WRONG_GREEN_POLICY.md"
    text = path.read_text(encoding="utf-8")

    assert "wrong_green_count = 0" in text
    assert "computed_prediction_not_official" in text
    assert "does not mean official publication" in text
    assert "does not guarantee future behavior" in text
