from __future__ import annotations

from typing import Any

from parva_mcp_server.client import ParvaClientError, ParvaPublicClient, validate_public_origin
from parva_mcp_server.manifest import AGENT_GATEWAY_ROUTE


def test_http_client_calls_only_the_agent_gateway(parva_http_stub: dict[str, Any]) -> None:
    client = ParvaPublicClient(origin=parva_http_stub["origin"], timeout=5)
    result = client.request(
        "POST",
        AGENT_GATEWAY_ROUTE,
        {"tool_name": "parva.get_today", "input": {}},
    )
    assert result["tool_name"] == "parva.get_today"
    assert parva_http_stub["calls"][0]["path"] == AGENT_GATEWAY_ROUTE


def test_http_client_returns_sanitized_api_error(parva_http_stub: dict[str, Any]) -> None:
    client = ParvaPublicClient(origin=parva_http_stub["origin"], timeout=5)
    try:
        client.request(
            "POST",
            AGENT_GATEWAY_ROUTE,
            {
                "tool_name": "parva.convert_date",
                "input": {"ad_date": "9999-01-01"},
            },
        )
    except ParvaClientError as exc:
        assert exc.code == "UNSUPPORTED_DATE_RANGE"
        assert exc.status_code == 400
        assert exc.retryable is False
        assert "supported range" in str(exc)
        assert parva_http_stub["origin"] not in str(exc)
    else:
        raise AssertionError("upstream 400 was accepted")


def test_http_client_blocks_every_other_route(parva_http_stub: dict[str, Any]) -> None:
    client = ParvaPublicClient(origin=parva_http_stub["origin"])
    try:
        client.request("GET", "/v3/api/calendar/convert", {"date": "2026-04-14"})
    except ParvaClientError as exc:
        assert exc.code == "UNSAFE_ROUTE"
    else:
        raise AssertionError("non-gateway route was accepted")
    assert parva_http_stub["calls"] == []


def test_origin_validation_requires_https_outside_localhost() -> None:
    assert validate_public_origin("https://api.example.com/") == "https://api.example.com"
    assert validate_public_origin("http://127.0.0.1:8000") == "http://127.0.0.1:8000"
    for origin in (
        "http://api.example.com",
        "https://user:secret@example.com",
        "https://api.example.com/path",
        "file:///tmp/parva",
    ):
        try:
            validate_public_origin(origin)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe origin was accepted: {origin}")
