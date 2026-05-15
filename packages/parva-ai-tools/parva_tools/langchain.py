"""LangChain wrappers for public-safe Parva tools."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Callable

from .safety import normalize_tool_response, validate_tool_specs
from .schemas import TOOL_BY_NAME, TOOL_SPECS, ParvaToolSpec


class PublicRouteClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or os.getenv("PARVA_PUBLIC_ORIGIN") or "https://api.prabinghimire1.com.np").rstrip("/")
        self.timeout = timeout

    def request(self, method: str, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        route, payload = _bind_route(route, payload)
        url = f"{self.base_url}{route}"
        data = None
        headers = {"Accept": "application/json"}
        if method == "GET":
            query = urllib.parse.urlencode({k: v for k, v in payload.items() if v is not None})
            if query:
                url = f"{url}?{query}"
        else:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310
            decoded = json.loads(response.read().decode("utf-8"))
        if not isinstance(decoded, dict):
            raise TypeError("Parva API returned a non-object payload")
        return decoded


def call_tool(name: str, arguments: dict[str, Any] | None = None, *, client: Any = None) -> dict[str, Any]:
    validate_tool_specs()
    spec = TOOL_BY_NAME[name]
    caller = client or PublicRouteClient()
    payload = dict(arguments or {})
    if hasattr(caller, "invoke_parva_tool"):
        raw = caller.invoke_parva_tool(name, payload)
    elif hasattr(caller, "request"):
        raw = caller.request(spec.method, spec.route, payload)
    else:
        raise TypeError("client must expose request(method, route, payload)")
    return normalize_tool_response(raw)


def build_langchain_tools(client: Any = None) -> list[Any]:
    validate_tool_specs()
    try:
        from langchain_core.tools import StructuredTool
    except Exception:  # noqa: BLE001 - optional dependency fallback.
        return [_fallback_descriptor(spec) for spec in TOOL_SPECS]

    tools = []
    for spec in TOOL_SPECS:
        tools.append(
            StructuredTool.from_function(
                name=spec.name,
                description=spec.description,
                func=_callable_for(spec, client),
            )
        )
    return tools


def _callable_for(spec: ParvaToolSpec, client: Any = None) -> Callable[..., dict[str, Any]]:
    def _run(**kwargs: Any) -> dict[str, Any]:
        return call_tool(spec.name, kwargs, client=client)

    return _run


def _fallback_descriptor(spec: ParvaToolSpec) -> dict[str, Any]:
    payload = spec.descriptor()
    payload["framework"] = "langchain"
    payload["callable"] = spec.name
    return payload


def _bind_route(route: str, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    bound = route
    remaining = dict(payload)
    for key, value in list(payload.items()):
        token = "{" + key + "}"
        if token in bound:
            bound = bound.replace(token, urllib.parse.quote(str(value), safe=""))
            remaining.pop(key, None)
    return bound, remaining
