"""Integration tests for public artifact exposure endpoints."""

from app.main import app
from fastapi.testclient import TestClient

from tests.helpers import TRUST_HEADERS

client = TestClient(app)


def test_public_artifact_manifest_lists_files():
    response = client.get("/v3/api/public/artifacts/manifest", headers=TRUST_HEADERS)
    assert response.status_code == 200
    payload = response.json()
    assert "total_files" in payload
    assert "files" in payload
    assert isinstance(payload["files"], list)
    # We expect at least one precomputed artifact in repository baseline.
    assert any(item.get("category") == "precomputed" for item in payload["files"])


def test_public_dashboard_artifact_is_accessible():
    response = client.get("/v3/api/public/artifacts/dashboard", headers=TRUST_HEADERS)
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_public_artifact_manifest_is_publicly_readable():
    response = client.get("/v3/api/public/artifacts/manifest")
    assert response.status_code == 200
    assert "files" in response.json()
