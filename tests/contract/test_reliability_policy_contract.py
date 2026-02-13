"""Contract checks for reliability and policy endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_policy_endpoint_exists():
    response = client.get("/api/policy")
    assert response.status_code == 200
    body = response.json()
    assert body["policy"]["usage"] == "informational"
    assert "advisory" in body["policy"]


def test_reliability_endpoints_exist():
    status = client.get("/api/reliability/status")
    slos = client.get("/api/reliability/slos")
    playbooks = client.get("/api/reliability/playbooks")

    assert status.status_code == 200
    assert slos.status_code == 200
    assert playbooks.status_code == 200
    assert "runtime" in status.json()
    assert "slo" in slos.json()
    assert isinstance(playbooks.json().get("playbooks"), list)


def test_policy_metadata_attached_to_key_calendar_routes():
    response = client.get("/api/calendar/today")
    assert response.status_code == 200
    body = response.json()
    assert body["policy"]["usage"] == "informational"

    response2 = client.get("/api/forecast/festivals", params={"year": 2035})
    assert response2.status_code == 200
    assert response2.json()["policy"]["usage"] == "informational"
