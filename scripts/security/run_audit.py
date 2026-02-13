#!/usr/bin/env python3
"""Run lightweight security checks (dependency + config) and emit report."""

from __future__ import annotations

import json
import shutil
import subprocess
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

    # Python dependency check
    if shutil.which("pip-audit"):
        checks.append(("pip_audit", _run(["pip-audit", "-f", "json"], PROJECT_ROOT)))
    else:
        checks.append(
            (
                "pip_audit",
                {
                    "cmd": "pip-audit -f json",
                    "returncode": None,
                    "stdout": "",
                    "stderr": "pip-audit not installed; skipped",
                },
            )
        )

    # Node dependency check
    if shutil.which("npm"):
        checks.append(("npm_audit", _run(["npm", "audit", "--json"], PROJECT_ROOT / "frontend")))
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
