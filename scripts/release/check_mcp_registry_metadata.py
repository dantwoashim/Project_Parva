#!/usr/bin/env python3
"""Validate the optional MCP registry metadata file."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MCP_SRC = ROOT / "packages" / "parva-mcp-server" / "src"
sys.path.insert(0, str(MCP_SRC))

from parva_mcp_server.validate_registry_metadata import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
