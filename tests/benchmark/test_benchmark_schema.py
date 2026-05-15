from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "public-benchmark" / "validate_benchmark.py"
spec = importlib.util.spec_from_file_location("validate_benchmark", MODULE_PATH)
assert spec and spec.loader
validate_benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_benchmark)


def test_public_benchmark_schema_passes() -> None:
    assert validate_benchmark.validate_benchmark_file() == []


def test_benchmark_tasks_have_public_authority_boundary() -> None:
    benchmark = validate_benchmark.load_benchmark()
    assert len(benchmark["tasks"]) >= 30
    for task in benchmark["tasks"]:
        assert task["public_safe"] is True
        assert "authority" in task["authority_boundary"]
        assert set(task["scoring_dimensions"]) == set(validate_benchmark.REQUIRED_SCORING)


def test_future_bs_tasks_require_review_or_no_exact_predictions() -> None:
    benchmark = validate_benchmark.load_benchmark()
    future_tasks = [task for task in benchmark["tasks"] if task["category"] == "future_bs_unsupported_review_required"]
    assert future_tasks
    for task in future_tasks:
        expected = task["expected"]
        assert expected.get("exact_predictions_public") is False or expected.get("review_required") is True
