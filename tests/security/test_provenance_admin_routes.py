from __future__ import annotations

from app.bootstrap.access_control import classify_request


def test_provenance_write_routes_require_admin_policy():
    for path in [
        "/v3/api/provenance/snapshot/create",
        "/v3/api/provenance/transparency/append",
        "/v3/api/provenance/transparency/anchor/record",
    ]:
        requirement = classify_request(path, "POST")

        assert requirement.required is True
        assert requirement.admin_only is True
        assert requirement.policy_name == "provenance_admin"


def test_provenance_public_read_routes_stay_public_read_only():
    requirement = classify_request("/v3/api/provenance/transparency/log", "GET")

    assert requirement.required is False
    assert requirement.admin_only is False
    assert requirement.policy_name == "provenance_read"
