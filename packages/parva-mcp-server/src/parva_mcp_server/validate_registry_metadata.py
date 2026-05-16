"""Validate MCP registry metadata against the runtime manifest."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from .manifest import FORBIDDEN_FRAGMENTS, build_manifest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = PACKAGE_ROOT / "mcp-server.json"
PYPROJECT_PATH = PACKAGE_ROOT / "pyproject.toml"
UNSAFE_PHRASES = (
    "government approved",
    "official future",
    "legal authority",
    "banking authority",
    "payroll authority",
    "tax authority",
    "religious authority",
    "guaranteed future",
    "accepted registry",
)


def load_metadata(path: Path = METADATA_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _package_version() -> str:
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))["project"]["version"]


def validate_metadata(path: Path = METADATA_PATH) -> list[str]:
    issues: list[str] = []
    metadata = load_metadata(path)
    manifest = build_manifest()

    if metadata.get("version") != _package_version():
        issues.append("metadata version must match package version")
    if metadata.get("read_only") is not True:
        issues.append("metadata read_only must be true")
    if not metadata.get("repository"):
        issues.append("metadata repository is required")
    if metadata.get("transport") not in {"stdio", "http"}:
        issues.append("metadata transport must be stdio or http")

    metadata_tools = set(metadata.get("tools", []))
    manifest_tools = {tool["name"] for tool in manifest["tools"]}
    if metadata_tools != manifest_tools:
        issues.append("metadata tools must match runtime manifest tools")

    metadata_resources = set(metadata.get("resources", []))
    manifest_resources = {resource["uri"] for resource in manifest["resources"]}
    if metadata_resources != manifest_resources:
        issues.append("metadata resources must match runtime manifest resources")

    metadata_prompts = set(metadata.get("prompts", []))
    manifest_prompts = {prompt["name"] for prompt in manifest["prompts"]}
    if metadata_prompts != manifest_prompts:
        issues.append("metadata prompts must match runtime manifest prompts")

    serialized = json.dumps(metadata, sort_keys=True).lower()
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment in serialized and fragment not in metadata.get("forbidden_routes", []):
            issues.append(f"forbidden route fragment appears outside forbidden_routes: {fragment}")
    for phrase in UNSAFE_PHRASES:
        if phrase in serialized:
            issues.append(f"unsafe authority phrase in registry metadata: {phrase}")

    security = metadata.get("security_boundaries", {})
    for key in (
        "admin_routes",
        "billing_routes",
        "exact_unsupported_future_bs_predictions",
        "filesystem_writes",
        "private_routes",
        "shell_execution",
        "trust_mutation_routes",
    ):
        if security.get(key) is not False:
            issues.append(f"security_boundaries.{key} must be false")
    return issues


def main() -> int:
    issues = validate_metadata()
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2))
        return 1
    print(json.dumps({"ok": True, "metadata": str(METADATA_PATH)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
