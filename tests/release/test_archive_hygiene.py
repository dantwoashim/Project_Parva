from __future__ import annotations

import io
import tarfile

import pytest

from scripts.release.check_archive_hygiene import (
    REQUIRED_ARCHIVE_PATHS,
    _safe_extract_tar,
    check_archive_hygiene,
    check_required_paths,
)


def test_required_archive_paths_are_declared():
    assert "README.md" in REQUIRED_ARCHIVE_PATHS
    assert "reports/red_check_closure/README.md" in REQUIRED_ARCHIVE_PATHS
    assert "public-benchmark/results/benchmark.svg" in REQUIRED_ARCHIVE_PATHS


def test_current_tree_has_required_archive_paths():
    assert check_required_paths(__import__("pathlib").Path.cwd()) == []


def test_tracked_archive_hygiene_has_no_junk():
    assert check_archive_hygiene(run_archive=False) == []


def test_safe_extract_rejects_path_traversal(tmp_path):
    archive_path = tmp_path / "bad.tar"
    with tarfile.open(archive_path, "w") as archive:
        payload = b"bad"
        member = tarfile.TarInfo("../escape.txt")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    extract_root = tmp_path / "extract"
    extract_root.mkdir()
    with (
        tarfile.open(archive_path) as archive,
        pytest.raises(RuntimeError, match="escapes extraction root"),
    ):
        _safe_extract_tar(archive, extract_root)


def test_safe_extract_rejects_links(tmp_path):
    archive_path = tmp_path / "bad-link.tar"
    with tarfile.open(archive_path, "w") as archive:
        member = tarfile.TarInfo("link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../escape.txt"
        archive.addfile(member)

    extract_root = tmp_path / "extract"
    extract_root.mkdir()
    with (
        tarfile.open(archive_path) as archive,
        pytest.raises(RuntimeError, match="not a regular file"),
    ):
        _safe_extract_tar(archive, extract_root)
