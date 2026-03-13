#!/usr/bin/env python3
"""Run lightweight security checks (dependency + config) and emit report."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "reports" / "security_audit.json"


def _run(cmd: list[str], cwd: Path) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return {
            "cmd": " ".join(cmd),
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "cmd": " ".join(cmd),
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }


def main() -> int:
    checks = []
    npm_binary = shutil.which("npm.cmd") or shutil.which("npm")

    # Python dependency check
    if importlib.util.find_spec("pip_audit") is not None:
        checks.append(("pip_audit", _run([sys.executable, "-m", "pip_audit", "-f", "json"], PROJECT_ROOT)))
    else:
        checks.append(
            (
                "pip_audit",
                {
                    "cmd": f"{sys.executable} -m pip_audit -f json",
                    "returncode": None,
                    "stdout": "",
                    "stderr": "pip-audit not installed; skipped",
                },
            )
        )

    # Node dependency check
    if npm_binary:
        checks.append(("npm_audit", _run([npm_binary, "audit", "--json"], PROJECT_ROOT / "frontend")))
    else:
        checks.append(
            (
                "npm_audit",
                {
                    "cmd": "npm audit --json",
                    "returncode": None,
                    "stdout": "",
                    "stderr": "npm not installed; skipped",
                },
            )
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": {name: result for name, result in checks},
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(REPORT_PATH)}, indent=2))

    for _, result in checks:
        if result.get("returncode") not in {0, None}:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
