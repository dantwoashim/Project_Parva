"""Minimal read-only Parva MCP adapter entrypoint."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .manifest import FORBIDDEN_FRAGMENTS, build_manifest, lint_manifest


class UnsafeMcpCall(ValueError):
    """Raised when a call attempts to leave the public read-only surface."""


def _tool_by_name(name: str) -> dict[str, Any]:
    manifest = build_manifest()
    for tool in manifest["tools"]:
        if tool["name"] == name:
            return tool
    raise UnsafeMcpCall(f"Unknown or unsupported MCP tool: {name}")


def _bind_route(route: str, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    bound = route
    remaining = dict(payload)
    for key, value in list(payload.items()):
        token = "{" + key + "}"
        if token in bound:
            bound = bound.replace(token, str(value))
            remaining.pop(key, None)
    return bound, remaining


def call_tool(name: str, arguments: dict[str, Any] | None = None, *, client: Any = None) -> dict[str, Any]:
    tool = _tool_by_name(name)
    route, payload = _bind_route(str(tool["route"]), dict(arguments or {}))
    lowered_route = route.lower()
    if not route.startswith("/v3/api/"):
        raise UnsafeMcpCall(f"{name} is outside the public v3 API")
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment in lowered_route:
            raise UnsafeMcpCall(f"{name} includes forbidden route fragment {fragment}")
    if client is None:
        return {
            "status": "manifest_only",
            "tool": name,
            "route": route,
            "method": tool["method"],
            "claim_boundary": tool["claim_boundary"],
            "review_required": bool(tool.get("review_required_passthrough", True)),
        }
    if not hasattr(client, "request"):
        raise TypeError("client must expose request(method, route, payload)")
    raw = client.request(tool["method"], route, payload)
    if not isinstance(raw, dict):
        raise TypeError("client returned a non-object payload")
    raw.setdefault("claim_boundary", tool["claim_boundary"])
    raw.setdefault("review_required", bool(tool.get("review_required_passthrough", True)))
    return raw


def check_server() -> dict[str, Any]:
    manifest = build_manifest()
    issues = lint_manifest(manifest)
    if issues:
        return {"ok": False, "issues": issues}
    probe = call_tool("convert_ad_to_bs", {"date": "2026-04-14"})
    return {
        "ok": True,
        "manifest_sha256": manifest["manifest_sha256"],
        "tool_count": len(manifest["tools"]),
        "resource_count": len(manifest["resources"]),
        "probe": probe,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", action="store_true", help="Print the safe MCP manifest.")
    parser.add_argument("--check", action="store_true", help="Run descriptor and tool-surface checks.")
    args = parser.parse_args(argv)

    if args.check:
        result = check_server()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok") else 1

    manifest = build_manifest()
    issues = lint_manifest(manifest)
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
