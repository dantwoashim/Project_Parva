#!/usr/bin/env python3
"""Reject known non-Parva workspace residue in the repo root."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    issues: list[str] = []

    root_package = PROJECT_ROOT / "package.json"
    if root_package.exists():
        payload = _load_json(root_package)
        if payload.get("name") == "viral-sync-workspace":
            issues.append("Root package.json still identifies the repo as viral-sync-workspace.")
        workspaces = payload.get("workspaces") or []
        if any(item in {"app", "relayer", "server/actions", "cranks", "packages/*"} for item in workspaces):
            issues.append("Root package.json still declares unrelated viral-sync workspaces.")

    legacy_shared_package = PROJECT_ROOT / "packages" / "shared" / "package.json"
    if legacy_shared_package.exists():
        payload = _load_json(legacy_shared_package)
        package_name = str(payload.get("name") or "")
        if package_name.startswith("@viral-sync/"):
            issues.append("packages/shared/package.json still exports the unrelated @viral-sync package.")

    legacy_shared_source = PROJECT_ROOT / "packages" / "shared" / "src" / "index.ts"
    if legacy_shared_source.exists():
        source_text = legacy_shared_source.read_text(encoding="utf-8")
        if "LAMPORTS_PER_SOL" in source_text or "RELAYER_ROUTE_PREFIX" in source_text:
            issues.append("packages/shared/src/index.ts still contains unrelated relayer/Solana exports.")

    root_tsconfig = PROJECT_ROOT / "tsconfig.json"
    if root_tsconfig.exists():
        text = root_tsconfig.read_text(encoding="utf-8")
        if "packages/shared" in text or '"mocha"' in text:
            issues.append("Root tsconfig.json still references unrelated workspace test settings.")

    root_tsconfig_base = PROJECT_ROOT / "tsconfig.base.json"
    if root_tsconfig_base.exists():
        issues.append("Root tsconfig.base.json still exists even though Parva does not use a root TS workspace.")

    if issues:
        for issue in issues:
            print(f"[repo-hygiene] {issue}")
        raise SystemExit(1)

    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
