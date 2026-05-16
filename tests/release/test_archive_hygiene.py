from __future__ import annotations

from scripts.release.check_archive_hygiene import (
    REQUIRED_ARCHIVE_PATHS,
    check_archive_hygiene,
    check_required_paths,
)


def test_required_archive_paths_are_declared():
    assert "README.md" in REQUIRED_ARCHIVE_PATHS
    assert "reports/external_reviewer_packet/README.md" in REQUIRED_ARCHIVE_PATHS
    assert "public-benchmark/results/benchmark.svg" in REQUIRED_ARCHIVE_PATHS


def test_current_tree_has_required_archive_paths():
    assert check_required_paths(__import__("pathlib").Path.cwd()) == []


def test_tracked_archive_hygiene_has_no_junk():
    assert check_archive_hygiene(run_archive=False) == []
