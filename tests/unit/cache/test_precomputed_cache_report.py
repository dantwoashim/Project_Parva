from __future__ import annotations

import json
from datetime import date


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_precomputed_festivals_between_report_surfaces_partial_hits(monkeypatch, tmp_path):
    import app.cache.precomputed as precomputed_module

    monkeypatch.setattr(precomputed_module, "PRECOMPUTE_DIR", tmp_path)
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
    _write_json(tmp_path / "panchanga_2028.json", {"dates": {}})

    stats = precomputed_module.get_cache_stats()

    assert "freshness" in stats
    assert stats["freshness"]["newest_modified"] is not None
    assert stats["freshness"]["oldest_modified"] is not None
    assert stats["freshness"]["newest_age_seconds"] is not None
    assert stats["artifact_classes"]["panchanga"]["available"] is True
    assert stats["artifact_classes"]["festivals"]["available"] is False
