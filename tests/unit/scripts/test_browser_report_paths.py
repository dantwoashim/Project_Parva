from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest

from scripts import run_browser_smoke, run_frontend_accessibility, run_golden_journeys
from scripts.run_frontend_accessibility import _resolve_report_path as resolve_a11y_report
from scripts.run_golden_journeys import _resolve_report_path as resolve_golden_report


def test_browser_report_paths_are_root_relative() -> None:
    expected = Path.cwd() / "tmp" / "browser-report.json"

    assert resolve_a11y_report("tmp/browser-report.json") == expected
    assert resolve_golden_report("tmp/browser-report.json") == expected


def test_absolute_browser_report_paths_are_preserved(tmp_path: Path) -> None:
    report = tmp_path / "browser-report.json"

    assert resolve_a11y_report(str(report)) == report
    assert resolve_golden_report(str(report)) == report


@pytest.mark.parametrize(
    "runner",
    [run_browser_smoke, run_frontend_accessibility, run_golden_journeys],
)
def test_self_started_browser_servers_disable_rate_limiting(
    monkeypatch: pytest.MonkeyPatch,
    runner: ModuleType,
) -> None:
    captured: dict = {}

    def fake_popen(*_args, **kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)

    runner._start_backend_server("127.0.0.1", 8765)

    assert captured["env"]["PARVA_RATE_LIMIT_ENABLED"] == "false"
