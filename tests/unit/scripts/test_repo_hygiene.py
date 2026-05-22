from __future__ import annotations

import subprocess

from scripts.release import check_repo_hygiene


def test_repo_hygiene_rejects_tracked_release_artifacts(monkeypatch):
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                b"frontend/dist/assets/index.js\0"
                b"reports/conformance_report.json\0"
                b"evaluation.csv\0"
                b"backend/project_parva.egg-info/PKG-INFO\0"
                b"backend/app/__pycache__/main.cpython-311.pyc\0"
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
        return subprocess.CompletedProcess(args=[], returncode=0, stdout=b"README.md\0backend/app/main.py\0", stderr="")

    monkeypatch.setattr(check_repo_hygiene.subprocess, "run", fake_run)

    assert check_repo_hygiene.main() == 0


def test_repo_hygiene_detects_nested_local_artifacts():
    assert check_repo_hygiene._tracked_path_issue("backend/project_parva.egg-info/PKG-INFO")
    assert check_repo_hygiene._tracked_path_issue("backend/app/__pycache__/main.cpython-311.pyc")
    assert check_repo_hygiene._tracked_path_issue("img/.DS_Store")


def test_repo_hygiene_rejects_utf8_bom(tmp_path):
    target = tmp_path / "module.py"
    target.write_bytes(b"\xef\xbb\xbfprint('bad encoding marker')\n")

    assert check_repo_hygiene._has_utf8_bom(target)


def test_repo_hygiene_rejects_windows_hostile_paths():
    assert check_repo_hygiene._path_portability_issue("data/bad:name.json")
    assert check_repo_hygiene._path_portability_issue("data/CON/source.json")
    assert check_repo_hygiene._path_portability_issue("data/source./payload.json")
    assert check_repo_hygiene._path_portability_issue("data/source /payload.json")


def test_repo_hygiene_allows_portable_unicode_paths():
    assert check_repo_hygiene._path_portability_issue("data/sources/२०८२-sample.json") is None
