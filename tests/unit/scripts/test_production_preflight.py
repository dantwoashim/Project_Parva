from __future__ import annotations

from scripts.release import check_production_preflight


class _FakeApp:
    class _State:
        settings = type(
            "Settings",
            (),
            {
                "environment": "production",
                "source_url": "https://example.com/source",
                "rate_limit_backend": "redis",
                "require_precomputed": False,
                "place_search_provider_policy": "offline_only",
                "place_search_allow_remote": False,
                "place_search_provider_chain": ("offline",),
                "place_search_endpoint": "https://example.com/geocoder",
            },
        )()
        startup_checks = {
            "ready": True,
            "checks": {
                "config": {"required": True, "ok": True, "detail": "validated"},
            },
        }

    state = _State()


def test_production_preflight_passes_when_app_boots(monkeypatch, capsys):
    monkeypatch.setattr(check_production_preflight, "create_app", lambda: _FakeApp())

    assert check_production_preflight.main() == 0
    output = capsys.readouterr().out
    assert '"environment": "production"' in output
    assert '"policy": "offline_only"' in output


def test_production_preflight_fails_when_app_boot_fails(monkeypatch, capsys):
    def _boom():
        raise RuntimeError("PARVA_SOURCE_URL is missing")

    monkeypatch.setattr(check_production_preflight, "create_app", _boom)

    assert check_production_preflight.main() == 1
    output = capsys.readouterr().out
    assert "PARVA_SOURCE_URL is missing" in output
