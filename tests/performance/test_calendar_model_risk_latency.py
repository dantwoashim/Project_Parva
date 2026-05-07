import time

from app.services.calendar_model_risk_service import claim_readiness_report, prediction_payload


def test_prediction_payload_latency_under_100ms():
    start = time.perf_counter()
    prediction_payload(2084, 6)
    assert (time.perf_counter() - start) < 0.1


def test_claim_readiness_latency_under_3s():
    start = time.perf_counter()
    claim_readiness_report()
    assert (time.perf_counter() - start) < 3.0
