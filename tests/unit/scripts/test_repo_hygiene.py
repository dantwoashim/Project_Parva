from __future__ import annotations

import subprocess

from scripts.release import check_repo_hygiene


def test_repo_hygiene_rejects_tracked_release_artifacts(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                "frontend/dist/assets/index.js\n"
                "reports/conformance_report.json\n"
                "evaluation.csv\n"
                "backend/project_parva.egg-info/PKG-INFO\n"
                "backend/app/__pycache__/main.cpython-311.pyc\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(check_repo_hygiene.subprocess, "run", fake_run)

    try:
        check_repo_hygiene.main()
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("Expected hygiene check to reject tracked release artifacts.")


def test_repo_hygiene_accepts_clean_tracking(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="README.md\nbackend/app/main.py\n", stderr="")

    monkeypatch.setattr(check_repo_hygiene.subprocess, "run", fake_run)

    assert check_repo_hygiene.main() == 0


def test_repo_hygiene_detects_nested_local_artifacts():
    assert check_repo_hygiene._tracked_path_issue("backend/project_parva.egg-info/PKG-INFO")
    assert check_repo_hygiene._tracked_path_issue("backend/app/__pycache__/main.cpython-311.pyc")
    assert check_repo_hygiene._tracked_path_issue("img/.DS_Store")
