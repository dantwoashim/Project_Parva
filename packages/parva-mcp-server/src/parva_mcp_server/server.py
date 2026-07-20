"""Production stdio MCP server for Project Parva's public temporal tools."""

from __future__ import annotations

import argparse
import json
import logging
from functools import partial
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Iterable

import anyio
from jsonschema import FormatChecker, ValidationError, validate
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.stdio import stdio_server

from .client import ParvaClientError, ParvaPublicClient
from .manifest import (
    AGENT_GATEWAY_ROUTE,
    PROMPTS,
    RESOURCES,
    build_manifest,
    lint_manifest,
)

LOGGER = logging.getLogger(__name__)
PACKAGE_NAME = "parva-mcp-server"
SERVER_NAME = "parva-mcp-server"
CLAIM_BOUNDARY = "decision_support_not_authority"


class UnsafeMcpCall(ValueError):
    """Raised when a call attempts to leave the public read-only surface."""


class InvalidMcpArguments(ValueError):
    """Raised when direct callers bypass MCP schema validation."""


def _package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "1.0.0"


SERVER_VERSION = _package_version()
SERVER_INSTRUCTIONS = (
    "Use these read-only temporal tools as decision support. Preserve claim_boundary, "
    "review_required, evidence, source, and uncertainty fields. Treat official-source, "
    "legal, banking, payroll, tax, religious, and unsupported future-BS decisions as "
    "human-review sensitive."
)

MCP_SERVER = Server(
    SERVER_NAME,
    version=SERVER_VERSION,
    instructions=SERVER_INSTRUCTIONS,
    website_url="https://github.com/dantwoashim/Project_Parva",
)

RESOURCE_DESCRIPTIONS: dict[str, str] = {
    "parva://capabilities": "Current public agent capabilities returned by Project Parva.",
    "parva://route-maturity": "Maturity boundary for the MCP-exposed public route surface.",
    "parva://source-policy": "Source, uncertainty, and Future-BS publication policy.",
    "parva://supported-ranges": "How supported date ranges are reported by the live tools.",
    "parva://known-limitations": "Authority and review limitations that apply to every tool.",
    "parva://benchmark-summary": "Current generated public benchmark summary from Project Parva.",
}

STATIC_RESOURCE_PAYLOADS: dict[str, dict[str, Any]] = {
    "parva://route-maturity": {
        "stable": "Only the public v3 agent execution gateway is callable through MCP.",
        "excluded": "Research, private, admin, billing, mutation, and key-management routes.",
        "claim_boundary": CLAIM_BOUNDARY,
        "not_authority": True,
    },
    "parva://source-policy": {
        "policy": "Preserve source, confidence, uncertainty, and human-review fields.",
        "future_bs_publication_status": "computed_prediction_not_official",
        "claim_boundary": CLAIM_BOUNDARY,
        "not_authority": True,
    },
    "parva://supported-ranges": {
        "scope": "Each live tool returns its current supported range or a bounded error.",
        "unsupported_future_bs": "Return unsupported or review_required; never invent official data.",
        "claim_boundary": CLAIM_BOUNDARY,
        "not_authority": True,
    },
    "parva://known-limitations": {
        "limitations": [
            "Project Parva is not a government calendar authority.",
            "Project Parva is not legal, tax, banking, payroll, or religious authority.",
            "Future-BS computed predictions are not official publications.",
            "Sensitive or disputed results require human review when marked.",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
        "not_authority": True,
    },
}

PROMPT_TEMPLATES: dict[str, dict[str, Any]] = {
    "explain_nepali_date_safely": {
        "description": "Explain a Nepali date while preserving its source and review boundary.",
        "text": (
            "Explain the supplied Nepali date clearly. Preserve source, confidence, uncertainty, "
            "claim_boundary, review_required, and not_authority from the tool result."
        ),
    },
    "check_claim_with_sources": {
        "description": "Check a temporal claim and keep its evidence and review status.",
        "text": (
            "Check the supplied temporal claim with Project Parva. Report the result, evidence, "
            "source, confidence, claim_boundary, and whether human review is required."
        ),
    },
    "plan_schedule_with_review_gates": {
        "description": "Prepare a bounded schedule using working-day and fiscal results.",
        "text": (
            "Build the requested schedule from Project Parva working-day and fiscal results. "
            "Keep every review gate and ask for human confirmation before sensitive use."
        ),
    },
}


def _tool_by_name(name: str) -> dict[str, Any]:
    for tool in build_manifest()["tools"]:
        if tool["name"] == name:
            return tool
    raise UnsafeMcpCall(f"Unknown or unsupported MCP tool: {name}")


def _validate_arguments(tool: dict[str, Any], arguments: dict[str, Any]) -> None:
    try:
        validate(
            instance=arguments,
            schema=tool["input_schema"],
            format_checker=FormatChecker(),
        )
    except ValidationError as exc:
        raise InvalidMcpArguments(f"Invalid arguments for {tool['name']}: {exc.message}") from exc


def _agent_input(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "convert_bs_to_ad":
        return {
            "bs_date": (
                f"{int(arguments['year']):04d}-{int(arguments['month']):02d}-"
                f"{int(arguments['day']):02d}"
            )
        }
    if name == "convert_ad_to_bs":
        return {"ad_date": arguments["date"]}
    if name == "get_nepali_today":
        return {}
    if name in {"check_holiday", "check_working_day", "get_fiscal_year"}:
        payload = {
            key: arguments[key]
            for key in ("ad_date", "bs_date", "profile_id", "decision_intent")
            if key in arguments
        }
        if name == "check_holiday":
            payload["decision_intent"] = "general"
        return payload
    if name == "get_festival_date":
        return {
            "festival_id": arguments["festival_id"],
            "year": arguments["year"],
        }
    if name == "get_panchanga_summary":
        return dict(arguments)
    if name == "check_temporal_claim":
        payload = dict(arguments)
        payload.setdefault("include_evidence", True)
        return payload
    raise UnsafeMcpCall(f"Unknown or unsupported MCP tool: {name}")


def _request_agent_tool(
    agent_tool: str,
    input_payload: dict[str, Any],
    *,
    client: Any,
) -> dict[str, Any]:
    if not hasattr(client, "request"):
        raise TypeError("client must expose request(method, route, payload)")
    raw = client.request(
        "POST",
        AGENT_GATEWAY_ROUTE,
        {"tool_name": agent_tool, "input": input_payload},
    )
    if not isinstance(raw, dict):
        raise TypeError("client returned a non-object payload")
    return raw


def call_tool(
    name: str,
    arguments: dict[str, Any] | None = None,
    *,
    client: Any = None,
) -> dict[str, Any]:
    """Execute one MCP tool through the public Project Parva agent gateway."""
    tool = _tool_by_name(name)
    payload = dict(arguments or {})
    _validate_arguments(tool, payload)
    caller = client or ParvaPublicClient()
    raw = _request_agent_tool(
        str(tool["agent_tool"]),
        _agent_input(name, payload),
        client=caller,
    )
    return _normalize_tool_response(raw, tool)


def _normalize_tool_response(raw: dict[str, Any], tool: dict[str, Any]) -> dict[str, Any]:
    payload = dict(raw)
    agent_meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    claim_boundary = agent_meta.get("claim_boundary") or _find_first(
        payload,
        "claim_boundary",
    ) or tool["claim_boundary"]
    review_required = _contains_true(payload, {"review_required", "requires_human_review"})
    review_required = review_required or _contains_value(
        payload,
        {"status"},
        "review_required",
    )
    payload["claim_boundary"] = str(claim_boundary)
    payload["review_required"] = bool(review_required)
    payload["not_authority"] = True
    return payload


def _find_first(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value and value[key] is not None:
            return value[key]
        for child in value.values():
            found = _find_first(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_first(child, key)
            if found is not None:
                return found
    return None


def _contains_true(value: Any, keys: set[str]) -> bool:
    if isinstance(value, dict):
        if any(value.get(key) is True for key in keys):
            return True
        return any(_contains_true(child, keys) for child in value.values())
    if isinstance(value, list):
        return any(_contains_true(child, keys) for child in value)
    return False


def _contains_value(value: Any, keys: set[str], expected: str) -> bool:
    if isinstance(value, dict):
        if any(value.get(key) == expected for key in keys):
            return True
        return any(_contains_value(child, keys, expected) for child in value.values())
    if isinstance(value, list):
        return any(_contains_value(child, keys, expected) for child in value)
    return False


def _tool_descriptor(tool: dict[str, Any]) -> types.Tool:
    return types.Tool(
        name=str(tool["name"]),
        title=str(tool["title"]),
        description=str(tool["description"]),
        inputSchema=dict(tool["input_schema"]),
        outputSchema=dict(tool["output_schema"]),
        annotations=types.ToolAnnotations(
            title=str(tool["title"]),
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
        _meta={
            "io.projectparva/claimBoundary": tool["claim_boundary"],
            "io.projectparva/reviewRequiredPassthrough": True,
            "io.projectparva/notAuthority": True,
        },
    )


def _tool_error_result(error: ParvaClientError | Exception, *, code: str) -> types.CallToolResult:
    if isinstance(error, ParvaClientError):
        error_payload = error.payload()
    else:
        error_payload = {
            "code": code,
            "message": " ".join(str(error).split())[:400]
            or "Project Parva tool execution failed.",
            "retryable": False,
        }
    structured = {
        "error": error_payload,
        "claim_boundary": CLAIM_BOUNDARY,
        "review_required": True,
        "not_authority": True,
    }
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=f"{error_payload['code']}: {error_payload['message']}",
            )
        ],
        structuredContent=structured,
        isError=True,
    )


@MCP_SERVER.list_tools()
async def _list_tools() -> list[types.Tool]:
    return [_tool_descriptor(tool) for tool in build_manifest()["tools"]]


@MCP_SERVER.call_tool(validate_input=True)
async def _call_tool_handler(name: str, arguments: dict[str, Any]) -> dict[str, Any] | types.CallToolResult:
    try:
        return await anyio.to_thread.run_sync(partial(call_tool, name, arguments))
    except InvalidMcpArguments as exc:
        return _tool_error_result(exc, code="INVALID_TOOL_ARGUMENTS")
    except UnsafeMcpCall as exc:
        return _tool_error_result(exc, code="UNSUPPORTED_TOOL")
    except ParvaClientError as exc:
        return _tool_error_result(exc, code=exc.code)
    except (TypeError, ValueError) as exc:
        return _tool_error_result(exc, code="MCP_ADAPTER_ERROR")
    except Exception as exc:  # pragma: no cover - defensive protocol boundary
        LOGGER.error("Unexpected MCP tool failure: %s", type(exc).__name__)
        return _tool_error_result(
            RuntimeError("Project Parva could not complete the tool request."),
            code="MCP_INTERNAL_ERROR",
        )


@MCP_SERVER.list_resources()
async def _list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=uri,
            name=uri.removeprefix("parva://").replace("-", " "),
            title=uri.removeprefix("parva://").replace("-", " ").title(),
            description=RESOURCE_DESCRIPTIONS[uri],
            mimeType="application/json",
        )
        for uri in RESOURCES
    ]


def _resource_payload(uri: str, *, client: Any = None) -> dict[str, Any]:
    if uri not in RESOURCES:
        raise UnsafeMcpCall(f"Unknown MCP resource: {uri}")
    if uri in STATIC_RESOURCE_PAYLOADS:
        return dict(STATIC_RESOURCE_PAYLOADS[uri])
    caller = client or ParvaPublicClient()
    agent_tool = (
        "parva.get_capabilities"
        if uri == "parva://capabilities"
        else "parva.get_benchmark_summary"
    )
    raw = _request_agent_tool(agent_tool, {}, client=caller)
    return _normalize_tool_response(
        raw,
        {"claim_boundary": CLAIM_BOUNDARY},
    )


@MCP_SERVER.read_resource()
async def _read_resource(uri: Any) -> Iterable[ReadResourceContents]:
    payload = await anyio.to_thread.run_sync(partial(_resource_payload, str(uri)))
    return [
        ReadResourceContents(
            content=json.dumps(payload, sort_keys=True),
            mime_type="application/json",
        )
    ]


@MCP_SERVER.list_prompts()
async def _list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name=name,
            title=name.replace("_", " ").title(),
            description=PROMPT_TEMPLATES[name]["description"],
        )
        for name in PROMPTS
    ]


@MCP_SERVER.get_prompt()
async def _get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    del arguments
    if name not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown MCP prompt: {name}")
    prompt = PROMPT_TEMPLATES[name]
    return types.GetPromptResult(
        description=prompt["description"],
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt["text"]),
            )
        ],
    )


def check_server(*, live: bool = False, client: Any = None) -> dict[str, Any]:
    manifest = build_manifest()
    issues = lint_manifest(manifest)
    try:
        configured_client = client or ParvaPublicClient()
    except ValueError as exc:
        issues.append(str(exc))
        configured_client = None

    result: dict[str, Any] = {
        "ok": not issues,
        "issues": issues,
        "server_version": SERVER_VERSION,
        "protocol_implementation": "official-mcp-python-sdk",
        "manifest_sha256": manifest["manifest_sha256"],
        "tool_count": len(manifest["tools"]),
        "resource_count": len(manifest["resources"]),
        "execution": manifest["execution"],
    }
    if configured_client is not None:
        result["public_origin"] = getattr(configured_client, "origin", "injected-client")
    if live and not issues and configured_client is not None:
        try:
            capabilities = _request_agent_tool(
                "parva.get_capabilities",
                {},
                client=configured_client,
            )
            advertised_tools = _find_first(capabilities, "public_tools")
            if not isinstance(advertised_tools, list) or not all(
                isinstance(name, str) for name in advertised_tools
            ):
                raise TypeError("Project Parva returned an invalid agent capability list")
            required_tools = {
                str(tool["agent_tool"])
                for tool in manifest["tools"]
            } | {
                "parva.get_capabilities",
                "parva.get_benchmark_summary",
            }
            missing_tools = sorted(required_tools - set(advertised_tools))
            if missing_tools:
                result["ok"] = False
                result["live_probe"] = {
                    "ok": False,
                    "error": {
                        "code": "MISSING_AGENT_CAPABILITIES",
                        "message": (
                            "The configured Project Parva gateway is missing "
                            "required MCP capabilities."
                        ),
                    },
                    "missing_agent_tools": missing_tools,
                    "required_agent_tool_count": len(required_tools),
                    "advertised_agent_tool_count": len(set(advertised_tools)),
                }
                return result
            probe = call_tool(
                "convert_ad_to_bs",
                {"date": "2026-04-14"},
                client=configured_client,
            )
        except (InvalidMcpArguments, ParvaClientError, UnsafeMcpCall, TypeError, ValueError) as exc:
            result["ok"] = False
            result["live_probe"] = {
                "ok": False,
                "error": exc.payload() if isinstance(exc, ParvaClientError) else str(exc),
            }
        else:
            result["live_probe"] = {
                "ok": True,
                "manifest_only": probe.get("status") == "manifest_only",
                "tool_name": probe.get("tool_name"),
                "review_required": probe["review_required"],
                "claim_boundary": probe["claim_boundary"],
                "required_agent_tool_count": len(required_tools),
                "advertised_agent_tool_count": len(set(advertised_tools)),
            }
    return result


async def _serve_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await MCP_SERVER.run(
            read_stream,
            write_stream,
            MCP_SERVER.create_initialization_options(),
        )


def run_stdio() -> int:
    anyio.run(_serve_stdio)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", action="store_true", help="Print the safe MCP manifest.")
    parser.add_argument("--check", action="store_true", help="Validate local MCP configuration.")
    parser.add_argument(
        "--check-live",
        action="store_true",
        help="Validate gateway capabilities and execute one live API probe.",
    )
    parser.add_argument("--stdio", action="store_true", help="Run the stdio MCP server.")
    parser.add_argument("--version", action="store_true", help="Print the package version.")
    args = parser.parse_args(argv)

    if args.version:
        print(SERVER_VERSION)
        return 0
    if args.stdio:
        return run_stdio()
    if args.check or args.check_live:
        result = check_server(live=args.check_live)
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
