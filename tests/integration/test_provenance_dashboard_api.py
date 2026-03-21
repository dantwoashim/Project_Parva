from app.main import app
from fastapi.testclient import TestClient

from tests.helpers import TRUST_HEADERS

client = TestClient(app)


def test_provenance_dashboard_is_accessible():
    response = client.get("/v3/api/provenance/dashboard", headers=TRUST_HEADERS)
    assert response.status_code == 200
    payload = response.json()
    assert "request_health" in payload
    assert "degraded_mode" in payload
    assert "provenance_verification" in payload
    assert "latency_error_budgets" in payload
