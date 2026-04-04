from __future__ import annotations

import json
from datetime import date


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_precomputed_festivals_between_report_surfaces_partial_hits(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
    precomputed_module.clear_precomputed_cache()
    _write_json(
        tmp_path / "festivals_2028.json",
        {
            "year": 2028,
            "festivals": [
                {
                    "festival_id": "demo-festival",
                    "start": "2028-12-30",
                    "end": "2028-12-30",
                    "method": "precomputed",
                }
            ],
        },
    )

    report = precomputed_module.load_precomputed_festivals_between_report(
        date(2028, 12, 25),
        date(2029, 1, 5),
    )

    assert report["loaded_years"] == [2028]
    assert report["missing_years"] == [2029]
    assert report["partial_hit"] is True
    assert report["full_hit"] is False
    assert len(report["rows"]) == 1
    assert report["rows"][0]["festival_id"] == "demo-festival"


def test_get_cache_stats_includes_freshness_metadata(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
    precomputed_module.clear_precomputed_cache()
    _write_json(tmp_path / "panchanga_2028.json", {"dates": {}})

    stats = precomputed_module.get_cache_stats()

    assert "freshness" in stats
    assert stats["freshness"]["newest_modified"] is not None
    assert stats["freshness"]["oldest_modified"] is not None
    assert stats["freshness"]["newest_age_seconds"] is not None
    assert stats["artifact_classes"]["panchanga"]["available"] is True
    assert stats["artifact_classes"]["festivals"]["available"] is False


def test_load_precomputed_panchanga_reuses_cached_year_blob(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    reads = {"count": 0}
    source = tmp_path / "panchanga_2028.json"
    payload = {
        "dates": {
            "2028-01-01": {"tithi": {"name": "Pratipada"}},
            "2028-01-02": {"tithi": {"name": "Dwitiya"}},
        }
    }
    _write_json(source, payload)
    precomputed_module.clear_precomputed_cache()
    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)

    original_read_text = precomputed_module.Path.read_text

    def counting_read_text(path_obj, *args, **kwargs):
        if path_obj == source:
            reads["count"] += 1
        return original_read_text(path_obj, *args, **kwargs)

    monkeypatch.setattr(precomputed_module.Path, "read_text", counting_read_text)

    first = precomputed_module.load_precomputed_panchanga(date(2028, 1, 1))
    second = precomputed_module.load_precomputed_panchanga(date(2028, 1, 2))

    assert first["tithi"]["name"] == "Pratipada"
    assert second["tithi"]["name"] == "Dwitiya"
    assert reads["count"] == 1


def test_prewarm_hot_set_warms_today_and_festival_years(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    today = date(2026, 4, 4)
    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
    precomputed_module.clear_precomputed_cache()

    _write_json(
        tmp_path / "panchanga_2026.json",
        {"dates": {today.isoformat(): {"panchanga": {"tithi": {"name": "Dwitiya"}}}}},
    )
    _write_json(tmp_path / "festivals_2026.json", {"festivals": []})
    _write_json(tmp_path / "festivals_2027.json", {"festivals": []})

    warmed = precomputed_module.prewarm_hot_set(today)

    assert warmed["target_date"] == "2026-04-04"
    assert warmed["panchanga_today"] is True
    assert warmed["festival_years"] == {"2026": True, "2027": True}
    assert warmed["hit_count"] == 3


def test_measure_hotset_latency_reports_cold_and_warm(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    today = date(2026, 4, 4)
    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
    precomputed_module.clear_precomputed_cache()

    _write_json(
        tmp_path / "panchanga_2026.json",
        {"dates": {today.isoformat(): {"panchanga": {"tithi": {"name": "Dwitiya"}}}}},
    )
    _write_json(tmp_path / "festivals_2026.json", {"festivals": []})
    _write_json(tmp_path / "festivals_2027.json", {"festivals": []})

    probe = precomputed_module.measure_hotset_latency(today)

    assert probe["target_date"] == "2026-04-04"
    assert probe["cold_ms"] >= 0
    assert probe["warm_ms"] >= 0
    assert "delta_ms" in probe
    assert probe["panchanga_hit"] is True
    assert probe["festival_years"] == {"2026": True, "2027": True}
