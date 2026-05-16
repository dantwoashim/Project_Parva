import pytest
from app.future_bs.calendar_var import calendar_var_payload
from app.services.future_bs_service import predict_bs_year

pytestmark = pytest.mark.research_artifact


def test_calendar_var_payload_estimates_financial_exposure():
    prediction = predict_bs_year(2084)
    payload = calendar_var_payload(
        {
            "month": 6,
            "principal": 1000000,
            "annual_rate": 12,
            "affected_contracts": 10,
        },
        prediction=prediction,
    )
    assert payload["estimated_one_day_interest_exposure"] > 0
    assert payload["stress_scenarios"]
