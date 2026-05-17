"""Read-only Parva MCP adapter entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
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
            "not_authority": True,
        }
    if not hasattr(client, "request"):
        raise TypeError("client must expose request(method, route, payload)")
    raw = client.request(tool["method"], route, payload)
    if not isinstance(raw, dict):
        raise TypeError("client returned a non-object payload")
    raw.setdefault("claim_boundary", tool["claim_boundary"])
    raw.setdefault("review_required", bool(tool.get("review_required_passthrough", True)))
    raw.setdefault("not_authority", True)
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


JSONRPC_VERSION = "2.0"
SERVER_INFO = {"name": "parva-mcp-server", "version": "0.3.0a0"}
SUPPORTED_PROTOCOL_VERSION = "2024-11-05"

RESOURCE_PAYLOADS: dict[str, dict[str, Any]] = {
    "parva://capabilities": {
        "name": "Project Parva public-safe capabilities",
        "tools": [tool["name"] for tool in build_manifest()["tools"]],
        "claim_boundary": "decision_support_not_authority",
        "not_authority": True,
    },
    "parva://route-maturity": {
        "stable": "public v3 API routes only",
        "preview": "research/private routes are not exposed through MCP",
        "claim_boundary": "decision_support_not_authority",
        "not_authority": True,
    },
    "parva://source-policy": {
        "policy": "source-aware responses with confidence, source tier, and review gates",
        "future_bs": "computed_prediction_not_official when applicable",
        "claim_boundary": "decision_support_not_authority",
        "not_authority": True,
    },
    "parva://supported-ranges": {
        "scope": "public-safe supported ranges are returned by the underlying public routes",
        "unsupported_future_bs": "review_required or unsupported rather than official prediction",
        "claim_boundary": "decision_support_not_authority",
        "not_authority": True,
    },
    "parva://known-limitations": {
        "limitations": [
            "not a government calendar authority",
            "not legal, tax, banking, payroll, or religious authority",
            "not an official Future-BS source",
            "MCP adapter is read-only decision support",
        ],
        "claim_boundary": "decision_support_not_authority",
        "not_authority": True,
    },
    "parva://benchmark-summary": {
        "benchmark": "Nepali Time Reliability Benchmark v0",
        "parva_score_percent": 89.47,
        "static_score_percent": 20.53,
        "task_count": 38,
        "claim_boundary": "technical_benchmark_not_authority",
        "not_authority": True,
    },
}

PROMPT_TEMPLATES: dict[str, dict[str, Any]] = {
    "explain_nepali_date_safely": {
        "description": "Explain a Nepali date using source and uncertainty boundaries.",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        "Explain this Nepali date safely. Include source_tier, confidence, "
                        "claim_boundary, review_required, and not_authority. Do not claim "
                        "government, legal, tax, banking, payroll, religious, or official "
                        "future-date authority."
                    ),
                },
            }
        ],
    },
    "check_claim_with_sources": {
        "description": "Check a temporal claim while preserving source and review gates.",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        "Check this Nepali temporal claim with sources. Return source_tier, "
                        "confidence, claim_boundary, review_required, and not_authority. "
                        "Escalate unsupported or future-sensitive claims for review."
                    ),
                },
            }
        ],
    },
    "plan_schedule_with_review_gates": {
        "description": "Plan a schedule with explicit review gates for sensitive dates.",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        "Plan this Nepali schedule with deterministic dates where supported. "
                        "Include source_tier, confidence, claim_boundary, review_required, "
                        "and not_authority for each sensitive date."
                    ),
                },
            }
        ],
    },
}


def _tool_descriptor(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": tool["name"],
        "description": (
            f"Read-only Project Parva public tool for {tool['name']}. "
            "Decision support only; not authority."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": True,
            "properties": {},
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
        },
        "claim_boundary": tool["claim_boundary"],
        "review_required": bool(tool.get("review_required_passthrough", True)),
        "not_authority": True,
    }


def _jsonrpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _jsonrpc_error(request_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
        "error": {"code": code, "message": message},
    }
    if data is not None:
        payload["error"]["data"] = data
    return payload


def _safe_resource_payload(uri: str) -> dict[str, Any]:
    if not uri.startswith("parva://"):
        raise UnsafeMcpCall("Only whitelisted parva:// resources are supported")
    if uri not in RESOURCE_PAYLOADS:
        raise UnsafeMcpCall(f"Unknown MCP resource: {uri}")
    return RESOURCE_PAYLOADS[uri]


def handle_jsonrpc_request(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    if request.get("jsonrpc") != JSONRPC_VERSION:
        return _jsonrpc_error(request_id, -32600, "Invalid JSON-RPC request")
    method = request.get("method")
    if not isinstance(method, str):
        return _jsonrpc_error(request_id, -32600, "JSON-RPC method is required")
    params = request.get("params") or {}
    if params is not None and not isinstance(params, dict):
        return _jsonrpc_error(request_id, -32602, "params must be an object")

    manifest = build_manifest()

    try:
        if method == "initialize":
            return _jsonrpc_result(
                request_id,
                {
                    "protocolVersion": SUPPORTED_PROTOCOL_VERSION,
                    "serverInfo": SERVER_INFO,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                },
            )
        if method == "tools/list":
            return _jsonrpc_result(
                request_id,
                {"tools": [_tool_descriptor(tool) for tool in manifest["tools"]]},
            )
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(name, str) or not isinstance(arguments, dict):
                return _jsonrpc_error(request_id, -32602, "tools/call requires name and arguments")
            result = call_tool(name, arguments)
            return _jsonrpc_result(
                request_id,
                {
                    "content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}],
                    "structuredContent": result,
                    "isError": False,
                },
            )
        if method == "resources/list":
            return _jsonrpc_result(
                request_id,
                {
                    "resources": [
                        {
                            "uri": resource["uri"],
                            "name": resource["uri"].replace("parva://", "parva "),
                            "mimeType": "application/json",
                        }
                        for resource in manifest["resources"]
                    ]
                },
            )
        if method == "resources/read":
            uri = params.get("uri")
            if not isinstance(uri, str):
                return _jsonrpc_error(request_id, -32602, "resources/read requires uri")
            payload = _safe_resource_payload(uri)
            return _jsonrpc_result(
                request_id,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(payload, sort_keys=True),
                        }
                    ]
                },
            )
        if method == "prompts/list":
            return _jsonrpc_result(
                request_id,
                {
                    "prompts": [
                        {
                            "name": prompt["name"],
                            "description": PROMPT_TEMPLATES[prompt["name"]]["description"],
                        }
                        for prompt in manifest["prompts"]
                    ]
                },
            )
        if method == "prompts/get":
            name = params.get("name")
            if not isinstance(name, str):
                return _jsonrpc_error(request_id, -32602, "prompts/get requires name")
            if name not in PROMPT_TEMPLATES:
                return _jsonrpc_error(request_id, -32602, f"Unknown MCP prompt: {name}")
            return _jsonrpc_result(request_id, PROMPT_TEMPLATES[name])
    except UnsafeMcpCall as exc:
        return _jsonrpc_error(request_id, -32602, str(exc))

    return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")


def run_stdio() -> int:
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            request = json.loads(stripped)
        except json.JSONDecodeError as exc:
            response = _jsonrpc_error(None, -32700, "Parse error", {"detail": str(exc)})
        else:
            if not isinstance(request, dict):
                response = _jsonrpc_error(None, -32600, "Invalid JSON-RPC request")
            else:
                response = handle_jsonrpc_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
            sys.stdout.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", action="store_true", help="Print the safe MCP manifest.")
    parser.add_argument("--check", action="store_true", help="Run descriptor and tool-surface checks.")
    parser.add_argument("--stdio", action="store_true", help="Run the live stdio JSON-RPC MCP server.")
    args = parser.parse_args(argv)

    if args.stdio:
        return run_stdio()

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
