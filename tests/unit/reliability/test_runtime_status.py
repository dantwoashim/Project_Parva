from __future__ import annotations


def test_runtime_status_marks_missing_required_precompute_as_degraded(monkeypatch):
    import app.reliability.status as status_module

    monkeypatch.setattr(
        status_module,
        "load_settings",
        lambda: type(
            "S",
            (),
            {"require_precomputed": True, "precomputed_stale_hours": 24 * 30},
        )(),
    )
    monkeypatch.setattr(status_module, "get_ephemeris_info", lambda: {"mode": "swiss"})
    monkeypatch.setattr(
        status_module,
        "get_cache_stats",
        lambda: {
            "file_count": 0,
            "total_bytes": 0,
            "freshness": {},
            "artifact_classes": {},
        },
    )

    payload = status_module.get_runtime_status()

    assert payload["status"] == "degraded"
    assert "precomputed_required_but_missing" in payload["warnings"]
    assert payload["cache"]["required"] is True


def test_runtime_status_flags_stale_artifacts(monkeypatch):
    import app.reliability.status as status_module

    monkeypatch.setattr(
        status_module,
        "load_settings",
        lambda: type(
            "S",
            (),
            {"require_precomputed": False, "precomputed_stale_hours": 1},
        )(),
    )
    monkeypatch.setattr(status_module, "get_ephemeris_info", lambda: {"mode": "swiss"})
    monkeypatch.setattr(
        status_module,
        "get_cache_stats",
        lambda: {
            "file_count": 1,
            "total_bytes": 10,
            "freshness": {
                "newest_modified": 1.0,
                "oldest_modified": 1.0,
                "newest_age_seconds": 7200.0,
                "oldest_age_seconds": 7200.0,
            },
            "artifact_classes": {"panchanga": {"available": True, "file_count": 1}},
        },
    )

    payload = status_module.get_runtime_status()

    assert payload["status"] == "degraded"
    assert "precomputed_artifacts_stale" in payload["warnings"]
    assert payload["cache"]["stale_threshold_hours"] == 1
