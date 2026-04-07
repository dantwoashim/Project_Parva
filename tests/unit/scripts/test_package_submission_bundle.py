from __future__ import annotations

import subprocess

from scripts.release import package_submission_bundle


def test_should_skip_non_submission_top_level_paths():
    assert package_submission_bundle._should_skip(
        package_submission_bundle.PROJECT_ROOT / "docs" / "DEPLOYMENT.md"
    )
    assert package_submission_bundle._should_skip(
        package_submission_bundle.PROJECT_ROOT / "tests" / "unit" / "bootstrap" / "test_settings.py"
    )


def test_should_skip_generated_and_large_runtime_artifacts():
    assert package_submission_bundle._should_skip(
        package_submission_bundle.PROJECT_ROOT / "backend" / "data" / "snapshots" / "snap.json"
    )
    assert package_submission_bundle._should_skip(
        package_submission_bundle.PROJECT_ROOT / "data" / "holiday_source.pdf"
    )


def test_should_keep_runtime_submission_files():
    assert package_submission_bundle._should_skip(
        package_submission_bundle.PROJECT_ROOT / "backend" / "app" / "main.py"
    ) is False
    assert package_submission_bundle._should_skip(
        package_submission_bundle.PROJECT_ROOT / "frontend" / "package.json"
    ) is False


def test_working_tree_is_clean_ignores_dirty_paths_outside_submission_scope(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=" M docs/DEPLOYMENT.md\n M tests/unit/bootstrap/test_settings.py\n",
            stderr="",
        )

    monkeypatch.setattr(package_submission_bundle.subprocess, "run", fake_run)

    assert package_submission_bundle._working_tree_is_clean() is True


def test_working_tree_is_clean_rejects_dirty_submission_files(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=" M README.md\n",
            stderr="",
        )

    monkeypatch.setattr(package_submission_bundle.subprocess, "run", fake_run)

    assert package_submission_bundle._working_tree_is_clean() is False
