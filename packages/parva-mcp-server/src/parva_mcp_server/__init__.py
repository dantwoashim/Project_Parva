"""Read-only production MCP adapter for Project Parva."""

from __future__ import annotations

from typing import Any

from .client import ParvaClientError, ParvaPublicClient, validate_public_origin
from .manifest import build_manifest, lint_manifest, manifest_digest

_SERVER_EXPORTS = {
    "InvalidMcpArguments",
    "UnsafeMcpCall",
    "call_tool",
    "check_server",
}


def __getattr__(name: str) -> Any:
    if name in _SERVER_EXPORTS:
        from . import server

        return getattr(server, name)
    raise AttributeError(name)


__all__ = [
    "InvalidMcpArguments",
    "ParvaClientError",
    "ParvaPublicClient",
    "UnsafeMcpCall",
    "build_manifest",
    "call_tool",
    "check_server",
    "lint_manifest",
    "manifest_digest",
    "validate_public_origin",
]
