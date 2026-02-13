from __future__ import annotations

from benchmark.harness import run_pack
from benchmark.validate_pack import validate_pack_data


def test_validate_pack_data_passes_valid_shape():
    pack = {
        "pack_id": "x",
        "version": "1",
        "description": "d",
        "calendar_family": "bs",
        "cases": [
            {
                "id": "c1",
                "endpoint": "/v2/api/calendar/convert",
                "params": {"date": "2026-02-15"},
                "assertions": {"bikram_sambat.year": 2082},
                "source": "test",
            }
        ],
    }
    assert validate_pack_data(pack) == []


def test_validate_pack_data_catches_errors():
    pack = {
        "pack_id": "x",
        "version": "1",
        "description": "d",
        "calendar_family": "bs",
        "cases": [{"id": "c1", "endpoint": "bad", "params": [], "assertions": {}, "source": "s"}],
    }
    errors = validate_pack_data(pack)
    assert errors


def test_run_pack_reports_pass_and_fail(monkeypatch):
    pack = {
        "pack_id": "demo",
        "version": "1",
        "description": "d",
        "calendar_family": "bs",
        "cases": [
            {
                "id": "ok",
                "endpoint": "/x",
                "params": {},
                "assertions": {"a": 1},
                "source": "s",
            },
            {
                "id": "bad",
                "endpoint": "/y",
                "params": {},
                "assertions": {"a": 2},
                "source": "s",
            },
        ],
    }

    def fake_get_json(base_url, endpoint, params):
        if endpoint == "/x":
            return {"a": 1}, 10
        return {"a": 1}, 10

    monkeypatch.setattr("benchmark.harness._http_get_json", fake_get_json)
    report = run_pack(pack, "http://localhost")
    assert report["summary"]["total"] == 2
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 1
