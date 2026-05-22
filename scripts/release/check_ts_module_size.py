#!/usr/bin/env python3
"""Fail when TypeScript SDK modules grow past explicit size budgets."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAIL_LINES = 700
GRANDFATHERED_BUDGETS = {
    Path("packages/parva-js/src/index.ts"): 1_280,
}
CHECK_ROOTS = (
    PROJECT_ROOT / "packages" / "parva-js" / "src",
    PROJECT_ROOT / "packages" / "parva-local-kernel" / "src",
)


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> int:
    failures: list[str] = []
    for root in CHECK_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.ts"):
            relative = path.relative_to(PROJECT_ROOT)
            budget = GRANDFATHERED_BUDGETS.get(relative, DEFAULT_FAIL_LINES)
            count = _line_count(path)
            if count > budget:
                failures.append(f"{relative.as_posix()} has {count} lines; budget is {budget}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("TypeScript module size checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
