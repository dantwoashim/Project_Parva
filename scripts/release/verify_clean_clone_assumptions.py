#!/usr/bin/env python3
"""Check that public verification does not depend on local-only artifacts."""

from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PUBLIC_FILES = (
    "reports/phase_07_future_bs_governance/module_classification.md",
    "reports/phase_08_performance_sre/latency_baseline.json",
    "reports/red_check_closure/README.md",
    "reports/next_roadmap_execution/README.md",
    "reports/next_roadmap_execution/verification_matrix.json",
    "reports/external_reviewer_packet/README.md",
    "public-benchmark/benchmark.json",
    "public-benchmark/schema.json",
    "public-benchmark/validate_benchmark.py",
    "public-benchmark/runners/run_against_static_baseline.py",
    "public-benchmark/runners/run_against_parva.py",
    "public-benchmark/runners/compare_results.py",
    "public-benchmark/results/latest-parva.json",
    "public-benchmark/results/latest-static-baseline.json",
    "public-benchmark/results/comparison.json",
)

OPTIONAL_PRIVATE_INPUTS = (
    "data/ephemeris/jpl/de440.bsp",
    "data/ephemeris/jpl/de441_part-1.bsp",
    "data/ephemeris/jpl/de441_part-2.bsp",
    "data/source_archive",
    "data/future_bs/private",
)


def _git_ls_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return set(result.stdout.splitlines())


def _is_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode == 0


def verify_clean_clone_assumptions() -> list[str]:
    tracked = _git_ls_files()
    issues: list[str] = []

    for path in REQUIRED_PUBLIC_FILES:
        full_path = PROJECT_ROOT / path
        if not full_path.exists():
            issues.append(f"{path}: required public file is missing")
            continue
        if full_path.is_file() and full_path.stat().st_size == 0:
            issues.append(f"{path}: required public file is empty")
        if path not in tracked:
            issues.append(f"{path}: required public file is not tracked")
        if _is_ignored(path) and path not in tracked:
            issues.append(f"{path}: required public file is ignored and untracked")

    for path in OPTIONAL_PRIVATE_INPUTS:
        if path in tracked:
            issues.append(f"{path}: private/large optional input must not be tracked")

    config_text = (PROJECT_ROOT / "config" / "ephemeris-kernels.yaml").read_text(encoding="utf-8")
    if '"public_runtime_required": true' in config_text or "public_runtime_required: true" in config_text:
        issues.append("config/ephemeris-kernels.yaml: JPL kernels must not be public-runtime required")
    if "D:\\" in config_text or "C:\\" in config_text:
        issues.append("config/ephemeris-kernels.yaml: local absolute path leaked")

    return issues


def main() -> int:
    issues = verify_clean_clone_assumptions()
    if issues:
        for issue in issues:
            print(f"[clean-clone] {issue}")
        return 1
    print("Clean-clone public verification assumptions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
