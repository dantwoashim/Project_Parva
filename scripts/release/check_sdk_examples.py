#!/usr/bin/env python3
"""Smoke-check offline SDK proof examples."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTHON_EXAMPLES = [
    "examples/sdk/python/verify_proofpack.py",
    "examples/sdk/python/verify_timepack.py",
    "examples/sdk/python/replay_membrane.py",
    "examples/sdk/python/verify_payroll_timepack.py",
]

JS_EXAMPLES = [
    "examples/sdk/js/verifyProofPack.ts",
    "examples/sdk/js/verifyTimepack.ts",
    "examples/sdk/js/replayMembrane.ts",
    "examples/sdk/js/verifyPayrollTimepack.ts",
]


def main() -> int:
    failures: list[str] = []
    for rel in PYTHON_EXAMPLES:
        result = subprocess.run([sys.executable, rel], cwd=PROJECT_ROOT, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            failures.append(f"{rel} failed: {result.stderr or result.stdout}")
    for rel in JS_EXAMPLES:
        text = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
        if "fetch(" in text or "http://" in text or "https://" in text:
            failures.append(f"{rel} must verify offline without live API calls")
        if "@project-parva/local-kernel" in text:
            failures.append(f"{rel} should import local source in repo smoke examples before publication")
        if "verify" not in text and "replay" not in text:
            failures.append(f"{rel} must call a proof verification/replay helper")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Offline SDK proof examples passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
