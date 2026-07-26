#!/usr/bin/env python3
"""Check GitHub Actions configuration is ready for the Node 24 action runtime."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKOUT_ACTION = "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd"
SETUP_PYTHON_ACTION = "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
SETUP_NODE_ACTION = "actions/setup-node@53b83947a5a98c8d113130e565377fae1a50d02f"
WORKFLOW_ACTIONS = {
    PROJECT_ROOT / ".github/workflows/ci.yml": (
        CHECKOUT_ACTION,
        SETUP_PYTHON_ACTION,
        SETUP_NODE_ACTION,
    ),
    PROJECT_ROOT / ".github/workflows/public-verification.yml": (
        CHECKOUT_ACTION,
        SETUP_PYTHON_ACTION,
        SETUP_NODE_ACTION,
    ),
    PROJECT_ROOT / ".github/workflows/trust-drift.yml": (
        CHECKOUT_ACTION,
        SETUP_PYTHON_ACTION,
    ),
}
DEPENDABOT_CONFIG = PROJECT_ROOT / ".github/dependabot.yml"
NODE_PACKAGES = [
    PROJECT_ROOT / "frontend" / "package.json",
    PROJECT_ROOT / "packages" / "parva-js" / "package.json",
    PROJECT_ROOT / "packages" / "parva-local-kernel" / "package.json",
]


def main() -> int:
    failures: list[str] = []
    for workflow, required_actions in WORKFLOW_ACTIONS.items():
        text = workflow.read_text(encoding="utf-8")
        rel = workflow.relative_to(PROJECT_ROOT)
        if "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION" in text:
            failures.append(f"{rel} must not allow insecure Node action runtimes")
        if "permissions:\n  contents: read" not in text:
            failures.append(f"{rel} must restrict the workflow token to contents: read")
        for action in required_actions:
            if f"uses: {action}" not in text:
                failures.append(f"{rel} must use pinned action {action}")
        checkout_count = text.count(f"uses: {CHECKOUT_ACTION}")
        persisted_credential_controls = text.count("persist-credentials: false")
        if persisted_credential_controls < checkout_count:
            failures.append(f"{rel} must disable persisted credentials for every checkout")

    if not DEPENDABOT_CONFIG.exists():
        failures.append(".github/dependabot.yml must maintain pinned GitHub Actions")
    elif "package-ecosystem: github-actions" not in DEPENDABOT_CONFIG.read_text(encoding="utf-8"):
        failures.append(".github/dependabot.yml must enable github-actions updates")

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
