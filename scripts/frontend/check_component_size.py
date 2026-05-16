#!/usr/bin/env python3
"""Fail on oversized frontend source files and report near-limit files."""

from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
SOURCE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx"}
WARN_LINE_BUDGET = 700
FAIL_LINE_BUDGET = 1_000
GRANDFATHERED_LINE_BUDGETS = {
    # FeedSubscriptionsPage predates the public-beta shell and is scheduled for
    # follow-up extraction; keep the allowance narrow and explicit.
    Path("frontend/src/pages/FeedSubscriptionsPage.jsx"): 1_050,
}


def _is_test_path(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)
    return "test" in relative.parts or path.name.endswith((".test.js", ".test.jsx", ".test.ts", ".test.tsx"))


def iter_large_files(max_lines: int) -> list[tuple[int, Path, int | None]]:
    rows: list[tuple[int, Path, int | None]] = []
    for path in FRONTEND_SRC.rglob("*"):
        if path.suffix not in SOURCE_SUFFIXES or not path.is_file() or _is_test_path(path):
            continue
        try:
            count = len(path.read_text(encoding="utf-8").splitlines())
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(PROJECT_ROOT)
        budget = GRANDFATHERED_LINE_BUDGETS.get(relative)
        if count > max_lines:
            rows.append((count, relative, budget))
    return sorted(rows, key=lambda row: row[0], reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-lines", type=int, default=WARN_LINE_BUDGET)
    parser.add_argument("--fail-lines", type=int, default=FAIL_LINE_BUDGET)
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    rows = iter_large_files(args.max_lines)
    if not rows:
        print(f"No frontend source files exceed {args.max_lines} lines.")
        return 0

    failures = []
    print(f"Frontend component size report: {len(rows)} production files exceed {args.max_lines} lines.")
    for count, path, budget in rows:
        if budget is None:
            print(f"{count:5d} {path.as_posix()} over warning budget={args.max_lines}")
            if count > args.fail_lines:
                failures.append(f"{path.as_posix()} exceeded hard limit: {count} > {args.fail_lines}")
            continue
        status = "within-budget" if count <= budget else "over-budget"
        print(f"{count:5d} {path.as_posix()} {status} budget={budget}")
        if count > budget:
            failures.append(f"{path.as_posix()} exceeded budget: {count} > {budget}")

    if failures and not args.warn_only:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
