#!/usr/bin/env python3
"""Verify the local/offline kernel npm package is publish-ready without publishing it."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "packages" / "parva-local-kernel"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from node_runtime import build_npm_command, resolve_node_runtime  # noqa: E402


def _run(command: list[str], *, cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def _fail(message: str) -> None:
    raise SystemExit(f"[local-kernel-package] {message}")


def main() -> int:
    package_json = PACKAGE_ROOT / "package.json"
    readme = PACKAGE_ROOT / "README.md"
    if not package_json.exists():
        _fail("package.json missing")
    if not readme.exists() or readme.stat().st_size == 0:
        _fail("README.md missing or empty")

    payload = json.loads(package_json.read_text(encoding="utf-8"))
    required = ["name", "version", "description", "license", "repository", "main", "types", "files", "scripts"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        _fail(f"package metadata missing: {', '.join(missing)}")
    if payload["name"] != "@project-parva/local-kernel":
        _fail("unexpected package name")
    if "dist" not in payload.get("files", []):
        _fail("package files must include dist")
    if "README.md" not in payload.get("files", []):
        _fail("package files must include README.md")

    node_runtime = resolve_node_runtime()
    npm_ci = build_npm_command(["--prefix", "packages/parva-local-kernel", "ci"], node_runtime)
    npm_test = build_npm_command(["--prefix", "packages/parva-local-kernel", "test"], node_runtime)
    npm_pack = build_npm_command(["pack", "--dry-run", "--json"], node_runtime)

    for label, command in (("npm ci", npm_ci), ("npm test", npm_test)):
        result = _run(command)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            _fail(f"{label} failed")

    pack = _run(npm_pack, cwd=PACKAGE_ROOT)
    if pack.returncode != 0:
        print(pack.stdout)
        print(pack.stderr)
        _fail("npm pack --dry-run failed")
    pack_payload = json.loads(pack.stdout)
    files = {entry["path"] for entry in pack_payload[0].get("files", [])}
    for expected in ("package.json", "README.md", "dist/index.js", "dist/index.d.ts"):
        if expected not in files:
            _fail(f"packed package missing {expected}")
    forbidden = [path for path in files if "node_modules/" in path or path.startswith("tests/")]
    if forbidden:
        _fail(f"packed package includes unwanted files: {forbidden}")

    with tempfile.TemporaryDirectory(prefix="parva-local-kernel-consumer-") as tmp:
        consumer = Path(tmp)
        (consumer / "package.json").write_text('{"type":"module"}\n', encoding="utf-8")
        script = consumer / "smoke.mjs"
        package_entry = (PACKAGE_ROOT / "dist" / "index.js").as_uri()
        script.write_text(
            "import { verifyMembrane, replayMembrane, verifyProofPack, verifyTimepack } "
            f"from '{package_entry}';\n"
            "if (typeof verifyMembrane !== 'function' || typeof replayMembrane !== 'function' "
            "|| typeof verifyProofPack !== 'function' || typeof verifyTimepack !== 'function') "
            "{ throw new Error('exports missing'); }\n"
            "console.log('ok');\n",
            encoding="utf-8",
        )
        node = "node"
        if node_runtime:
            node = str(node_runtime.executable)
        smoke = _run([node, str(script)], cwd=consumer)
        if smoke.returncode != 0:
            print(smoke.stdout)
            print(smoke.stderr)
            _fail("consumer import smoke failed")

    print(json.dumps({"ok": True, "package": payload["name"], "version": payload["version"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
