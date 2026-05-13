#!/usr/bin/env python3
"""Shared CLI entrypoint for the future-BS accuracy lab."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if os.getenv("PARVA_SCRIPT_REEXEC") != "1":
    needs_python311 = sys.version_info < (3, 11)
    try:
        import pydantic  # noqa: F401
        import swisseph  # noqa: F401
    except ModuleNotFoundError:
        needs_python311 = True
    if needs_python311:
        env = {**os.environ, "PARVA_SCRIPT_REEXEC": "1"}
        python_executable = os.getenv("PARVA_PYTHON", sys.executable)
        completed = subprocess.run([python_executable, *sys.argv], env=env)
        raise SystemExit(completed.returncode)

from app.future_bs.accuracy_lab import run_accuracy_loop  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    payload = run_accuracy_loop(final=args.final)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
