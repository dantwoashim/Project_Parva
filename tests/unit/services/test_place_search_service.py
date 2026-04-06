from __future__ import annotations

import importlib
import io
from urllib.error import URLError

import app.services.place_search_service as place_search_service


def test_default_user_agent_uses_configured_source_url(monkeypatch):
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.delenv("PARVA_PLACE_SEARCH_USER_AGENT", raising=False)

    module = importlib.reload(place_search_service)

    assert module._USER_AGENT == "ProjectParva/3.0 (+https://example.com/source)"


def test_default_user_agent_falls_back_to_neutral_instance_label(monkeypatch):
    monkeypatch.delenv("PARVA_SOURCE_URL", raising=False)
    monkeypatch.delenv("PARVA_PLACE_SEARCH_USER_AGENT", raising=False)

    module = importlib.reload(place_search_service)

    assert module._USER_AGENT == "ProjectParva/3.0 (self-hosted instance)"


def test_search_places_prefers_offline_gazetteer_for_common_nepal_queries(monkeypatch):
    module = importlib.reload(place_search_service)
    monkeypatch.setattr(module, "_ALLOW_REMOTE", False)

    payload = module.search_places(query="kathmandu", limit=3)

    assert payload["source_mode"] == "offline_gazetteer"
    assert payload["source"] == "offline_nepal_gazetteer"
    assert payload["total"] >= 1
    assert payload["items"][0]["label"].startswith("Kathmandu")
    assert payload["items"][0]["timezone"] == "Asia/Kathmandu"
    assert payload["provider_chain"][0] == "offline_nepal_gazetteer"
    assert payload["provider_health"][0]["status"] == "hit"


def test_search_places_raises_when_remote_is_disabled_and_query_is_not_in_offline_gazetteer(monkeypatch):
    module = importlib.reload(place_search_service)
    monkeypatch.setattr(module, "_ALLOW_REMOTE", False)

    try:
        module.search_places(query="zzzz-not-a-nepal-place", limit=3)
    except RuntimeError as exc:
        assert "Remote place search is disabled" in str(exc)
    else:
        raise AssertionError("Expected remote-disabled search to raise for an offline miss.")


def test_fetch_nominatim_rows_retries_transient_errors(monkeypatch):
    module = importlib.reload(place_search_service)

    attempts = {"count": 0}

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return io.BytesIO(b'[{"lat":"27.7","lon":"85.3","display_name":"Kathmandu, Nepal"}]').getvalue()

    def fake_urlopen(_request, timeout):
        attempts["count"] += 1
        assert timeout > 0
        if attempts["count"] == 1:
            raise URLError("temporary outage")
        return _Response()

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    monkeypatch.setattr(module.time, "sleep", lambda *_args, **_kwargs: None)

    rows = module._fetch_nominatim_rows("kathmandu", 3)

    assert attempts["count"] == 2
    assert rows[0]["display_name"] == "Kathmandu, Nepal"
