"""Repository-root import shim for the optional Parva MCP package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "packages" / "parva-mcp-server" / "src" / "parva_mcp_server"
if _SRC_PACKAGE.exists():
    __path__.append(str(_SRC_PACKAGE))  # type: ignore[name-defined]

_EXPORT_MODULES = {
    "InvalidMcpArguments": "server",
    "ParvaClientError": "client",
    "ParvaPublicClient": "client",
    "UnsafeMcpCall": "server",
    "build_manifest": "manifest",
    "call_tool": "server",
    "check_server": "server",
    "lint_manifest": "manifest",
    "manifest_digest": "manifest",
    "validate_public_origin": "client",
}


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = __import__(f"{__name__}.{module_name}", fromlist=[name])
    return getattr(module, name)


__all__ = sorted(_EXPORT_MODULES)
