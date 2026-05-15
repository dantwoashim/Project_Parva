"""LlamaIndex wrappers for public-safe Parva tools."""

from __future__ import annotations

from typing import Any

from .langchain import call_tool
from .safety import validate_tool_specs
from .schemas import TOOL_SPECS, ParvaToolSpec


def build_llamaindex_tools(client: Any = None) -> list[Any]:
    validate_tool_specs()
    try:
        from llama_index.core.tools import FunctionTool
    except Exception:  # noqa: BLE001 - optional dependency fallback.
        return [_fallback_descriptor(spec) for spec in TOOL_SPECS]

    return [
        FunctionTool.from_defaults(
            fn=_callable_for(spec, client),
            name=spec.name,
            description=spec.description,
        )
        for spec in TOOL_SPECS
    ]


def _callable_for(spec: ParvaToolSpec, client: Any = None):
    def _run(**kwargs: Any) -> dict[str, Any]:
        return call_tool(spec.name, kwargs, client=client)

    return _run


def _fallback_descriptor(spec: ParvaToolSpec) -> dict[str, Any]:
    payload = spec.descriptor()
    payload["framework"] = "llamaindex"
    payload["callable"] = spec.name
    return payload
