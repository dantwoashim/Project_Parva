from __future__ import annotations

import pytest

from parva import (
    DEFAULT_API_BASE,
    DEFAULT_FUTURE_BS_CAPABILITIES_URL,
    ParvaAPIError,
    ParvaClient,
)


def test_bs_to_ad_uses_public_v3_base() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"gregorian": "2026-04-14"}

    client = ParvaClient(transport=transport)
    payload = client.bs_to_ad(2083, 1, 1)

    assert payload["gregorian"] == "2026-04-14"
    assert calls[0][0] == "POST"
    assert calls[0][1] == f"{DEFAULT_API_BASE}/calendar/bs-to-gregorian"
    assert calls[0][3] == {"year": 2083, "month": 1, "day": 1}


def test_future_capabilities_uses_public_v4_endpoint() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {
            "surface": "future_bs_risk_research",
            "publication_status": "computed_prediction_not_official",
        }

    client = ParvaClient(transport=transport)
    payload = client.get_future_bs_capabilities()

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert calls[0][1] == DEFAULT_FUTURE_BS_CAPABILITIES_URL


def test_validate_bs_date_returns_false_for_public_400() -> None:
    def transport(method, url, params, json_body, timeout):
        raise ParvaAPIError("Invalid BS date", status=400, body={"detail": "Invalid BS date"})

    client = ParvaClient(transport=transport)
    payload = client.validate_bs_date(2083, 1, 32)

    assert payload["valid"] is False
    assert payload["publication_status"] == "computed_prediction_not_official"


def test_non_validation_errors_are_not_hidden() -> None:
    def transport(method, url, params, json_body, timeout):
        raise ParvaAPIError("server unavailable", status=503)

    client = ParvaClient(transport=transport)
    with pytest.raises(ParvaAPIError):
        client.validate_bs_date(2083, 1, 1)
