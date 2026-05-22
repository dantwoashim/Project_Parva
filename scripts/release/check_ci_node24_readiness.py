#!/usr/bin/env python3
"""Check GitHub Actions configuration is ready for the Node 24 action runtime."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = [PROJECT_ROOT / ".github/workflows/ci.yml", PROJECT_ROOT / ".github/workflows/public-verification.yml"]
NODE_PACKAGES = [
    PROJECT_ROOT / "frontend" / "package.json",
    PROJECT_ROOT / "packages" / "parva-js" / "package.json",
    PROJECT_ROOT / "packages" / "parva-local-kernel" / "package.json",
]


def main() -> int:
    failures: list[str] = []
    for workflow in WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        rel = workflow.relative_to(PROJECT_ROOT)
        if "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" not in text:
            failures.append(f"{rel} must opt JavaScript actions into the Node 24 runtime")
        if "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION" in text:
            failures.append(f"{rel} must not allow insecure Node action runtimes")
        for action in ("actions/checkout@v4", "actions/setup-node@v4", "actions/setup-python@v5"):
            if action not in text and workflow.name in {"ci.yml", "public-verification.yml"}:
                failures.append(f"{rel} unexpectedly missing supported action {action}")
    for package_json in NODE_PACKAGES:
        package_text = package_json.read_text(encoding="utf-8")
        if '">=20.20 <26"' not in package_text:
            rel = package_json.relative_to(PROJECT_ROOT)
            failures.append(f"{rel} must allow tested Node 20 and Node 24 runtimes")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("CI Node 24 action-runtime readiness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
