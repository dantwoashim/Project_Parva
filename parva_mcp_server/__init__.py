"""Repository-root import shim for the optional Parva MCP package."""

from __future__ import annotations

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "packages" / "parva-mcp-server" / "src" / "parva_mcp_server"
if _SRC_PACKAGE.exists():
    __path__.append(str(_SRC_PACKAGE))  # type: ignore[name-defined]
