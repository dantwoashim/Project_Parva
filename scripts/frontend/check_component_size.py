#!/usr/bin/env python3
"""Guard against renewed growth in known large frontend component files."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUDGETS = {
    "frontend/src/redesign/ParvaRedesign.jsx": 168_000,
    "frontend/src/redesign/components/VerificationComponents.jsx": 4_000,
}


def main() -> int:
    failures: list[str] = []
    for relative, max_bytes in BUDGETS.items():
        path = PROJECT_ROOT / relative
        if not path.exists():
            failures.append(f"Missing component file: {relative}")
            continue
        size = path.stat().st_size
        if size > max_bytes:
            failures.append(f"{relative} is {size} bytes, budget is {max_bytes} bytes")

    if failures:
        print("\n".join(failures))
        return 1

    print("Frontend component size budgets verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
