from __future__ import annotations

import importlib

import app.services.runtime_cache as runtime_cache


def test_runtime_cache_tracks_hits_misses_and_evictions(monkeypatch):
    monkeypatch.setenv("PARVA_RUNTIME_CACHE_ENABLED", "true")
    monkeypatch.setenv("PARVA_RUNTIME_CACHE_MAX_ENTRIES", "2")
    module = importlib.reload(runtime_cache)
    module.clear()

    assert module.cached("a", 60, lambda: "one") == "one"
    assert module.cached("a", 60, lambda: "two") == "one"
    assert module.cached("b", 60, lambda: "bee") == "bee"
    assert module.cached("c", 60, lambda: "see") == "see"

    stats = module.stats()
    assert stats["enabled"] is True
    assert stats["hits"] == 1
    assert stats["misses"] == 3
    assert stats["evictions"] == 1
    assert stats["entries"] == 2


def test_runtime_cache_can_be_disabled(monkeypatch):
    monkeypatch.setenv("PARVA_RUNTIME_CACHE_ENABLED", "false")
    module = importlib.reload(runtime_cache)
    module.clear()

    counter = {"value": 0}

    def compute():
        counter["value"] += 1
        return counter["value"]

    assert module.cached("a", 60, compute) == 1
    assert module.cached("a", 60, compute) == 2

    stats = module.stats()
    assert stats["enabled"] is False
    assert stats["hits"] == 0
    assert stats["misses"] == 2
