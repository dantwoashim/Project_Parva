"""Minimal CLI for emitting the Parva MCP manifest."""

from __future__ import annotations

import json

from .manifest import build_manifest, lint_manifest


def main() -> int:
    manifest = build_manifest()
    issues = lint_manifest(manifest)
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2))
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
