from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_policy_route_returns_truthful_route_access_manifest():
    response = client.get("/v3/api/policy")
    assert response.status_code == 200

    body = response.json()
    assert body["policy"]["route_policy_url"] == "/v3/api/policy"
    assert body["route_access"]["access_model"] == "public_compute_with_admin_mutations"

    personal = next(item for item in body["route_access"]["families"] if item["family"] == "personal")
    assert personal["read_access"] == "public"
    assert personal["write_access"] == "public"

    provenance = next(item for item in body["route_access"]["families"] if item["family"] == "provenance")
    assert provenance["read_access"] == "public"
    assert provenance["write_access"] == "admin"


def test_root_metadata_points_clients_to_route_policy_manifest():
    response = client.get("/")
    assert response.status_code == 200

    body = response.json()
    assert "non_public_auth" not in body
    assert body["access_model"]["policy_url"] == "/v3/api/policy"
    assert body["route_access"]["access_model"] == "public_compute_with_admin_mutations"
