from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

from scripts.release import package_source_archive
from scripts.release import verify_source_archive


def test_working_tree_is_clean_accepts_generated_runtime_artifacts(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                " M reports/authority_dashboard.json\n"
                " M reports/release/dashboard_metrics.md\n"
                " M backend/data/public_artifacts/authority_dashboard.json\n"
                " M backend/data/public_artifacts/dashboard_metrics.json\n"
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
            stdout=" M README.md\n M reports/release/dashboard_metrics.md\n",
            stderr="",
        )

    monkeypatch.setattr(package_source_archive.subprocess, "run", fake_run)

    assert package_source_archive._working_tree_is_clean() is False


def test_dirty_paths_handles_git_renames(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="R  docs/old.md -> backend/data/public_artifacts/dashboard_metrics.json\n",
            stderr="",
        )

    monkeypatch.setattr(package_source_archive.subprocess, "run", fake_run)

    assert package_source_archive._dirty_paths() == [
        Path("backend/data/public_artifacts/dashboard_metrics.json")
    ]


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


def test_verify_source_archive_rejects_disallowed_members(tmp_path):
    archive_path = tmp_path / "project-parva-test-source.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("project-parva-test/README.md", "ok")
        archive.writestr("project-parva-test/frontend/dist/index.js", "bad")

    failures: list[str] = []
    members = verify_source_archive._normalized_members(archive_path)
    for member in members:
        parts = Path(member).parts
        if any(part in verify_source_archive.DISALLOWED_SEGMENTS for part in parts):
            failures.append(member)

    assert failures == ["frontend/dist/index.js"]


def test_verify_source_archive_accepts_clean_members(tmp_path):
    archive_path = tmp_path / "project-parva-test-source.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("project-parva-test/README.md", "ok")
        archive.writestr("project-parva-test/backend/app/main.py", "print('ok')")

    assert verify_source_archive._normalized_members(archive_path) == [
        "README.md",
        "backend/app/main.py",
    ]
