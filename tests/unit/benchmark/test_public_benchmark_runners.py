from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load_runner(name: str):
    path = ROOT / "public-benchmark" / "runners" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_parva_runner_maps_every_task_to_endpoint():
    runner = _load_runner("run_against_parva.py")
    benchmark = runner._load_benchmark()

    specs = [runner._request_for_task(task) for task in benchmark["tasks"]]

    assert len(specs) == len(benchmark["tasks"])
    assert all(spec.path.startswith(("/v3/", "/v4/")) for spec in specs)


def test_public_parva_runner_executes_all_tasks_with_fetcher():
    runner = _load_runner("run_against_parva.py")

    def fake_fetch(_base_url, spec, _timeout):
        if spec.path.endswith("/bs-to-gregorian"):
            body = spec.body or {}
            if body.get("month", 1) not in range(1, 13) or body.get("day", 1) > 32:
                return 400, {"detail": "invalid", "policy": {"claim_boundary": "unsupported"}}
            return 200, {"gregorian": "2026-04-14", "provenance": {}, "confidence": "official"}
        if spec.path.endswith("/convert"):
            return 200, {"bikram_sambat": {"year": 2083, "month": 1, "day": 1}, "provenance": {}, "confidence": "official"}
        if "future-bs" in spec.path:
            return 200, {"publication_status": "computed_prediction_not_official", "review_required": True}
        return 200, {"policy": {"claim_boundary": "technical_benchmark_not_authority"}, "meta": {"confidence": "public"}}

    report = runner.run_benchmark("https://example.test", fetcher=fake_fetch)

    assert report["summary"]["total"] == len(runner._load_benchmark()["tasks"])
    assert report["summary"]["blocked"] == 0
    assert all(item["status"] != "not_implemented_in_v0_runner" for item in report["results"])


def test_static_baseline_emits_score_summary():
    runner = _load_runner("run_against_static_baseline.py")

    report = runner.run_static_baseline()

    assert report["summary"]["total"] == len(report["results"])
    assert 0 < report["summary"]["score_percent"] < 100
