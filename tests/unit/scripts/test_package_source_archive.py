from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.release import package_source_archive


def test_working_tree_is_clean_accepts_generated_public_beta_artifacts(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                " M docs/public_beta/authority_dashboard.json\n"
                " M docs/public_beta/authority_dashboard.md\n"
                " M docs/public_beta/dashboard_metrics.json\n"
                " M docs/public_beta/dashboard_metrics.md\n"
                " M docs/public_beta/month9_release_dossier.md\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(package_source_archive.subprocess, "run", fake_run)

    assert package_source_archive._working_tree_is_clean() is True


def test_working_tree_is_clean_rejects_unexpected_dirty_paths(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=" M README.md\n M docs/public_beta/dashboard_metrics.md\n",
            stderr="",
        )

    monkeypatch.setattr(package_source_archive.subprocess, "run", fake_run)

    assert package_source_archive._working_tree_is_clean() is False


def test_dirty_paths_handles_git_renames(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="R  docs/old.md -> docs/public_beta/dashboard_metrics.md\n",
            stderr="",
        )

    monkeypatch.setattr(package_source_archive.subprocess, "run", fake_run)

    assert package_source_archive._dirty_paths() == [Path("docs/public_beta/dashboard_metrics.md")]


def test_should_skip_generated_provenance_artifacts():
    assert package_source_archive._should_skip(
        package_source_archive.PROJECT_ROOT / "backend" / "data" / "snapshots" / "snap.json"
    )
    assert package_source_archive._should_skip(
        package_source_archive.PROJECT_ROOT / "backend" / "data" / "traces" / "trace.json"
    )


def test_should_skip_prompt_artifacts():
    assert package_source_archive._should_skip(package_source_archive.PROJECT_ROOT / "SKILL.md")


def test_should_skip_internal_review_docs():
    assert package_source_archive._should_skip(
        package_source_archive.PROJECT_ROOT / "docs" / "PROJECT_AUDIT_2026-03-13.md"
    )
    assert package_source_archive._should_skip(
        package_source_archive.PROJECT_ROOT / "docs" / "PROJECT_DEEP_AUDIT_2026-03-14.md"
    )
