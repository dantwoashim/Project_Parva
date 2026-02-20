"""Integration tests for public artifact exposure endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_public_artifact_manifest_lists_files():
    response = client.get("/v3/api/public/artifacts/manifest")
    assert response.status_code == 200
    payload = response.json()
    assert "total_files" in payload
    assert "files" in payload
    assert isinstance(payload["files"], list)
    # We expect at least one precomputed artifact in repository baseline.
    assert any(item.get("category") == "precomputed" for item in payload["files"])


def test_public_dashboard_artifact_is_accessible():
    response = client.get("/v3/api/public/artifacts/dashboard")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
