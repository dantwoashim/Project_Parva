import asyncio
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest
from app.bootstrap.middleware import (
    _client_ip,
    _should_rate_limit,
    _wants_data_meta_envelope,
    build_rate_limit_guard,
    build_request_context,
)
from app.bootstrap.rate_limit import RateLimiterUnavailable
from app.bootstrap.settings import AppSettings


def _settings(*, trusted_proxy_ips=frozenset()):
    return AppSettings(
        environment="test",
        exposure="local",
        license_mode="AGPL-3.0-or-later",
        source_url=None,
        route_profile="full",
        enable_experimental_api=False,
        enable_research_api=False,
        show_private_schema=False,
        allow_experimental_in_prod=False,
        serve_frontend=False,
        frontend_dist=Path("."),
        max_request_bytes=1024,
        max_query_length=1024,
        admin_token=None,
        trusted_proxy_ips=trusted_proxy_ips,
    )


class _Request:
    def __init__(self, remote_host, forwarded_for=None):
        self.client = SimpleNamespace(host=remote_host)
        self.headers = {}
        if forwarded_for is not None:
            self.headers["x-forwarded-for"] = forwarded_for


def _scope(path, *, header_value=None, query_string=b""):
    headers = []
    if header_value is not None:
        headers.append((b"x-parva-envelope", header_value.encode("latin-1")))
    return {
        "type": "http",
        "path": path,
        "headers": headers,
        "query_string": query_string,
    }


def test_client_ip_ignores_forwarded_for_from_untrusted_proxy():
    request = _Request("127.0.0.1", "203.0.113.1")

    assert _client_ip(request, _settings()) == "127.0.0.1"


def test_client_ip_uses_forwarded_for_from_trusted_proxy():
    request = _Request("127.0.0.1", "203.0.113.1, 198.51.100.9")

    assert _client_ip(request, _settings(trusted_proxy_ips=frozenset({"127.0.0.1"}))) == "203.0.113.1"


def test_rate_limiter_applies_to_api_paths():
    assert _should_rate_limit("/v3/api/calendar/today") is True
    assert _should_rate_limit("/api/personal/panchanga") is True


def test_rate_limiter_skips_frontend_routes_and_assets():
    assert _should_rate_limit("/") is False
    assert _should_rate_limit("/today") is False
    assert _should_rate_limit("/assets/FeedSubscriptionsPage-DgZZ0dbC.css") is False


def test_rate_limiter_unavailability_returns_fail_closed_503():
    class _UnavailableBackend:
        def check(self, **_kwargs):
            raise RateLimiterUnavailable("invalid Redis response")

    request = SimpleNamespace(
        state=SimpleNamespace(
            principal=SimpleNamespace(principal_type="free_ip", principal_id="203.0.113.1"),
            request_id="req-rate-limit",
            client_ip="203.0.113.1",
        ),
        url=SimpleNamespace(path="/v3/api/calendar/today"),
    )
    route_called = False

    async def call_next(_request):
        nonlocal route_called
        route_called = True

    middleware = build_rate_limit_guard(
        settings=_settings(),
        backend=_UnavailableBackend(),
    )
    response = asyncio.run(middleware(request, call_next))

    assert response.status_code == 503
    assert response.headers["retry-after"] == "60"
    assert json.loads(response.body)["rate_limit_policy"] == "fail_closed"
    assert route_called is False


def test_data_meta_envelope_opt_in_detects_header():
    assert _wants_data_meta_envelope(_scope("/v3/api/personal/panchanga", header_value="data-meta")) is True


def test_data_meta_envelope_opt_in_detects_query_param():
    assert _wants_data_meta_envelope(_scope("/v3/api/festivals/timeline", query_string=b"envelope=data-meta")) is True


def test_request_context_logs_exception_type_before_reraising(caplog):
    request = SimpleNamespace(
        headers={"x-request-id": "req-error"},
        state=SimpleNamespace(),
        client=SimpleNamespace(host="127.0.0.1"),
        url=SimpleNamespace(path="/boom"),
        method="GET",
    )

    async def call_next(_request):
        raise ValueError("boom")

    middleware = build_request_context(product_version="test-version", settings=_settings())

    with caplog.at_level(logging.ERROR, logger="parva.request"), pytest.raises(ValueError):
        asyncio.run(middleware(request, call_next))

    payload = json.loads(caplog.records[-1].message)
    assert payload["event"] == "request.error"
    assert payload["request_id"] == "req-error"
    assert payload["exception_type"] == "ValueError"
