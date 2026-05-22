#!/usr/bin/env python3
"""Print the npm executable resolved through Project Parva's Node runtime helper."""

from __future__ import annotations

import shlex
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from node_runtime import build_npm_command, resolve_node_runtime  # noqa: E402


def main() -> int:
    command = build_npm_command([], resolve_node_runtime())
    print(" ".join(shlex.quote(part) for part in command))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
