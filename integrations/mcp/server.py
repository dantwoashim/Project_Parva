# ruff: noqa: E402, I001
"""Compatibility entrypoint for the canonical packaged Parva MCP server."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parva_mcp_server.server import main


if __name__ == "__main__":
    raise SystemExit(main())
