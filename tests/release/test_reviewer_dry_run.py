from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def test_reviewer_dry_run_emits_offline_reports(tmp_path: Path) -> None:
    json_out = tmp_path / "review.json"
    md_out = tmp_path / "review.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release/reviewer_dry_run.py",
            "--quick",
            "--deterministic",
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["status"] == "pass"
    assert payload["generated_at"] == "2026-01-01T00:00:00+00:00"
    assert payload["live_api_required"] is False
    assert payload["external_validation_claimed"] is False
    assert payload["jpl_lane"]["status"] in {"skip", "pass"}
    assert "Forbidden Claims" in md_out.read_text(encoding="utf-8")


def test_reviewer_dry_run_fails_on_tampered_proofpack(tmp_path: Path) -> None:
    source = Path("examples/external/proofpacks/civil-conversion.proofpack.json")
    tampered = tmp_path / "tampered.proofpack.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["membrane"]["result"]["ad_date"] = "2025-04-15"
    tampered.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release/reviewer_dry_run.py",
            "--quick",
            "--skip-local-kernel",
            "--deterministic",
            "--civil-proofpack",
            str(tampered),
            "--json-out",
            str(tmp_path / "review.json"),
            "--md-out",
            str(tmp_path / "review.md"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    report = json.loads((tmp_path / "review.json").read_text(encoding="utf-8"))
    civil = next(item for item in report["commands"] if item["label"] == "civil proofpack")
    assert civil["status"] == "fail"


def test_reviewer_dry_run_fails_on_missing_artifact(tmp_path: Path) -> None:
    missing = tmp_path / "missing.proofpack.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release/reviewer_dry_run.py",
            "--quick",
            "--skip-local-kernel",
            "--deterministic",
            "--civil-proofpack",
            str(missing),
            "--json-out",
            str(tmp_path / "review.json"),
            "--md-out",
            str(tmp_path / "review.md"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert (tmp_path / "review.json").exists()


def test_reviewer_bundle_manifest_artifacts_exist() -> None:
    manifest = json.loads(Path("examples/external/reviewer-bundle/manifest.json").read_text(encoding="utf-8"))
    for item in manifest.get("artifacts", []):
        path = Path(item["path"])
        assert path.exists(), path
        assert path.stat().st_size > 0
    assert shutil.which("git") is not None
