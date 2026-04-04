"""Launch profile contract checks."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_webhooks_are_not_part_of_public_openapi_contract():
    response = client.get("/v3/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/v3/api/webhooks" not in paths
    assert "/v3/api/webhooks/subscribe" not in paths


def test_webhook_routes_are_not_shipped():
    assert client.get("/api/webhooks").status_code == 404
    assert client.get("/v3/api/webhooks").status_code == 404
