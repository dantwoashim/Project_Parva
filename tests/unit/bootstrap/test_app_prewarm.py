from types import SimpleNamespace

from app.bootstrap import app_factory


def test_runtime_prewarm_includes_festival_upcoming(monkeypatch):
    app = SimpleNamespace(state=SimpleNamespace(prewarm=None))
    settings = SimpleNamespace(prewarm_hotset=True)
    calls: list[dict] = []

    monkeypatch.setattr(app_factory, "prewarm_hot_set", lambda: {"status": "ok"})

    def fake_upcoming_festivals_payload(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(festivals=[{"id": "dashain"}])

    monkeypatch.setattr(app_factory, "upcoming_festivals_payload", fake_upcoming_festivals_payload)

    app_factory._prewarm_runtime_hotset(app, settings)

    assert len(calls) == 1
    assert calls[0]["days"] == 30
    assert calls[0]["quality_band"] == "all"
    assert calls[0]["profile"] is None
    assert app.state.prewarm["precomputed"] == {"status": "ok"}
    assert app.state.prewarm["festival_upcoming"]["status"] == "ok"
    assert app.state.prewarm["festival_upcoming"]["festival_count"] == 1
