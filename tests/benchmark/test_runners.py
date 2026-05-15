from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


static_runner = _load("run_against_static_baseline", ROOT / "public-benchmark" / "runners" / "run_against_static_baseline.py")
parva_runner = _load("run_against_parva", ROOT / "public-benchmark" / "runners" / "run_against_parva.py")
compare_runner = _load("compare_results", ROOT / "public-benchmark" / "runners" / "compare_results.py")


def test_static_baseline_scores_every_task() -> None:
    report = static_runner.run_static_baseline()

    assert report["summary"]["total"] >= 30
    assert len(report["results"]) == report["summary"]["total"]
    assert report["summary"]["score_percent"] < 100


def test_parva_runner_records_blocked_fetch_without_faking_result() -> None:
    def blocked_fetcher(base_url, spec, timeout):
        raise RuntimeError(f"blocked {spec.path}")

    report = parva_runner.run_benchmark("https://example.invalid", fetcher=blocked_fetcher)

    assert report["summary"]["blocked"] == report["summary"]["total"]
    assert all(item["score"] == 0 for item in report["results"])


def test_compare_reports_score_gap_and_review_gate_performance() -> None:
    static = static_runner.run_static_baseline()
    parva = static_runner.run_static_baseline()
    parva["runner"] = "parva"
    for item in parva["results"]:
        item["signals"]["source_awareness"] = True
        item["signals"]["uncertainty_handling"] = True
        item["signals"]["review_gate_behavior"] = True
        item["score"] = sum(
            weight for key, weight in parva_runner.WEIGHTS.items() if item["signals"].get(key)
        )
        item["status"] = "pass"
    score = sum(item["score"] for item in parva["results"])
    parva["summary"]["score"] = score
    parva["summary"]["score_percent"] = round((score / parva["summary"]["max_score"]) * 100.0, 2)

    comparison = compare_runner.compare(parva, static)

    assert comparison["parva_score_percent"] >= comparison["static_score_percent"]
    assert "review_gate_performance" in comparison
