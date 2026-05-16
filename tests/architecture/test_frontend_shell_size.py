from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_redesign_route_shell_is_under_500_lines() -> None:
    shell = PROJECT_ROOT / "frontend" / "src" / "redesign" / "ParvaRedesign.jsx"
    lines = shell.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 500
    assert (PROJECT_ROOT / "frontend" / "src" / "redesign" / "ParvaExperience.jsx").exists()


def test_parva_experience_is_no_longer_the_large_runtime_component() -> None:
    orchestrator = PROJECT_ROOT / "frontend" / "src" / "redesign" / "ParvaExperience.jsx"
    lines = orchestrator.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 1_000
    assert "experience/TodayMyPlace.jsx" in orchestrator.read_text(encoding="utf-8")
