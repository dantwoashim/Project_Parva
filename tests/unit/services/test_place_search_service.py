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
