#!/usr/bin/env python3
"""Generate public-beta release artifacts in the required dependency order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run_step(label: str, args: list[str]) -> None:
    print(f"[artifacts] {label}")
    completed = subprocess.run(args, cwd=PROJECT_ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate public-beta evidence artifacts")
    parser.add_argument("--target", type=int, default=300, help="Rule coverage target.")
    parser.add_argument(
        "--computed-target",
        type=int,
        default=300,
        help="Computed-rule baseline target enforced during ingestion.",
    )
    args = parser.parse_args()

    python = sys.executable
    steps = [
        (
            "1/6 Rule ingestion summary",
            [
                python,
                "scripts/rules/ingest_rule_sources.py",
                "--check",
                "--target",
                str(args.target),
                "--computed-target",
                str(args.computed_target),
            ],
        ),
        ("2/6 Accuracy report", [python, "scripts/generate_accuracy_report.py"]),
        ("3/6 Conformance report", [python, "scripts/spec/run_conformance_tests.py"]),
        ("4/6 Authority dashboard", [python, "scripts/generate_authority_dashboard.py"]),
        ("5/6 Dashboard metrics", [python, "scripts/release/generate_dashboard_metrics.py"]),
        ("6/6 Month 9 dossier", [python, "scripts/release/generate_month9_dossier.py"]),
    ]

    for label, command in steps:
        _run_step(label, command)

    print("[artifacts] Public-beta artifact generation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
