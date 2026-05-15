"""Repository-root entrypoint shim for ``python -m parva_mcp_server.server``."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SRC_SERVER = (
    Path(__file__).resolve().parents[1]
    / "packages"
    / "parva-mcp-server"
    / "src"
    / "parva_mcp_server"
    / "server.py"
)
_SPEC = importlib.util.spec_from_file_location("parva_mcp_server._server_impl", _SRC_SERVER)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Unable to load packaged Parva MCP server entrypoint")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

main = _MODULE.main


if __name__ == "__main__":
    raise SystemExit(main())
