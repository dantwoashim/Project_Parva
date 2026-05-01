from __future__ import annotations

import importlib

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


def test_search_places_raises_when_remote_is_disabled_and_query_is_not_in_offline_gazetteer(monkeypatch):
    module = importlib.reload(place_search_service)
    monkeypatch.setattr(module, "_ALLOW_REMOTE", False)

    try:
        module.search_places(query="zzzz-not-a-nepal-place", limit=3)
    except RuntimeError as exc:
        assert "Remote place search is disabled" in str(exc)
    else:
        raise AssertionError("Expected remote-disabled search to raise for an offline miss.")
