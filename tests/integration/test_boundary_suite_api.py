"""Integration tests for runtime boundary-suite reporting."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_boundary_suite_endpoint_returns_fixture_backed_summary():
    response = client.get("/api/reliability/boundary-suite")
    assert response.status_code == 200

    body = response.json()
    suite = body["boundary_suite"]
    assert suite["suite_count"] >= 3
    assert suite["total_samples"] >= 80
    assert isinstance(suite["suites"], list)
    ids = {item["suite_id"] for item in suite["suites"]}
    assert "tithi_boundaries_30" in ids
    assert "sankranti_24" in ids
    assert "adhik_maas_reference" in ids


def test_boundary_suite_includes_radar_counts_for_tithi_cases():
    response = client.get("/api/reliability/boundary-suite")
    assert response.status_code == 200

    suite = response.json()["boundary_suite"]
    tithi = next(item for item in suite["suites"] if item["suite_id"] == "tithi_boundaries_30")
    assert tithi["samples"] == 30
    assert "boundary_radar_counts" in tithi
    assert any(count >= 1 for count in tithi["boundary_radar_counts"].values())
