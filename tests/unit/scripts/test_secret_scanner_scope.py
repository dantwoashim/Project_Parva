from __future__ import annotations

from types import SimpleNamespace

from scripts.security import scan_repo_secrets


def test_secret_scan_excludes_generated_workspaces() -> None:
    for directory in ("tmp", "venv", ".tox", ".nox", "build"):
        path = scan_repo_secrets.PROJECT_ROOT / directory / "dependency.py"
        assert scan_repo_secrets._is_excluded(path)


def test_secret_scan_uses_git_visible_files(monkeypatch) -> None:
    captured: dict = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="README.md\0src/example.py\0")

    monkeypatch.setattr(scan_repo_secrets.subprocess, "run", fake_run)

    paths = scan_repo_secrets._candidate_paths()

    assert captured["command"] == [
        "git",
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "-z",
    ]
    assert paths == [
        scan_repo_secrets.PROJECT_ROOT / "README.md",
        scan_repo_secrets.PROJECT_ROOT / "src/example.py",
    ]
