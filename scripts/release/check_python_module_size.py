#!/usr/bin/env python3
"""Fail when production Python modules grow past explicit size budgets."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAIL_LINES = 1_000
GRANDFATHERED_BUDGETS = {
    Path("backend/app/services/rulelang_service.py"): 1_760,
    Path("packages/parva-python/parva/client.py"): 1_680,
    Path("backend/app/future_bs/data_acquisition.py"): 1_360,
    Path("backend/app/services/timegraph_service.py"): 1_120,
    Path("backend/app/future_bs/month_start/inversion_workbench.py"): 1_000,
}
CHECK_ROOTS = (
    PROJECT_ROOT / "backend" / "app",
    PROJECT_ROOT / "packages" / "parva-python",
    PROJECT_ROOT / "packages" / "parva-mcp-server",
    PROJECT_ROOT / "packages" / "parva-agent-tools",
)


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> int:
    failures: list[str] = []
    for root in CHECK_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts or "build" in path.parts:
                continue
            relative = path.relative_to(PROJECT_ROOT)
            budget = GRANDFATHERED_BUDGETS.get(relative, DEFAULT_FAIL_LINES)
            count = _line_count(path)
            if count > budget:
                failures.append(f"{relative.as_posix()} has {count} lines; budget is {budget}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Python module size checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
