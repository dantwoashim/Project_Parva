"""Contract checks for reliability and policy endpoints."""

from app.main import app
from fastapi.testclient import TestClient

from tests.helpers import TRUST_HEADERS

client = TestClient(app)


def test_policy_endpoint_exists():
    response = client.get("/api/policy")
    assert response.status_code == 200
    body = response.json()
    assert body["policy"]["usage"] == "informational"
    assert "advisory" in body["policy"]


def test_reliability_endpoints_exist():
    status = client.get("/api/reliability/status", headers=TRUST_HEADERS)
    slos = client.get("/api/reliability/slos", headers=TRUST_HEADERS)
    playbooks = client.get("/api/reliability/playbooks", headers=TRUST_HEADERS)
    benchmark = client.get("/api/reliability/benchmark-manifest", headers=TRUST_HEADERS)
    review_queue = client.get("/api/reliability/source-review-queue", headers=TRUST_HEADERS)
    boundary_suite = client.get("/api/reliability/boundary-suite", headers=TRUST_HEADERS)
    differential = client.get("/api/reliability/differential-manifest", headers=TRUST_HEADERS)

    assert status.status_code == 200
    assert slos.status_code == 200
    assert playbooks.status_code == 200
    assert benchmark.status_code == 200
    assert review_queue.status_code == 200
    assert boundary_suite.status_code == 200
    assert differential.status_code == 200
    assert "runtime" in status.json()
    assert "cache" in status.json()["runtime"]
    assert "freshness" in status.json()["runtime"]["cache"]
    assert "required" in status.json()["runtime"]["cache"]
    assert "artifact_classes" in status.json()["runtime"]["cache"]
    assert "slo" in slos.json()
    assert isinstance(playbooks.json().get("playbooks"), list)
    assert "benchmark" in benchmark.json()
    assert "engine_manifest_hash" in benchmark.json()["benchmark"]
    assert "queue" in review_queue.json()
    assert "items" in review_queue.json()["queue"]
    assert "boundary_suite" in boundary_suite.json()
    assert "suites" in boundary_suite.json()["boundary_suite"]
    assert "differential" in differential.json()
    assert "drift_percent" in differential.json()["differential"]


def test_reliability_endpoints_are_publicly_readable():
    status = client.get("/api/reliability/status")
    slos = client.get("/api/reliability/slos")
    playbooks = client.get("/api/reliability/playbooks")
    benchmark = client.get("/api/reliability/benchmark-manifest")
    review_queue = client.get("/api/reliability/source-review-queue")
    boundary_suite = client.get("/api/reliability/boundary-suite")
    differential = client.get("/api/reliability/differential-manifest")

    assert status.status_code == 200
    assert slos.status_code == 200
    assert playbooks.status_code == 200
    assert benchmark.status_code == 200
    assert review_queue.status_code == 200
    assert boundary_suite.status_code == 200
    assert differential.status_code == 200


def test_policy_metadata_attached_to_key_calendar_routes():
    response = client.get("/api/calendar/today")
    assert response.status_code == 200
    body = response.json()
    assert body["policy"]["usage"] == "informational"

    response2 = client.get("/api/forecast/festivals", params={"year": 2035})
    assert response2.status_code == 200
    assert response2.json()["policy"]["usage"] == "informational"
