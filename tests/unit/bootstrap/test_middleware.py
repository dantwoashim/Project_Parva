from pathlib import Path
from types import SimpleNamespace

from app.bootstrap.middleware import _client_ip, _should_rate_limit
from app.bootstrap.settings import AppSettings


def _settings(*, trusted_proxy_ips=frozenset()):
    return AppSettings(
        environment="test",
        license_mode="AGPL-3.0-or-later",
        source_url=None,
        enable_experimental_api=False,
        allow_experimental_in_prod=False,
        enable_webhooks=False,
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
