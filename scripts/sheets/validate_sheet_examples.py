#!/usr/bin/env python3
"""Validate spreadsheet distribution examples."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages" / "parva-sheets"

REQUIRED = {
    "README.md",
    "google-apps-script/Code.gs",
    "google-apps-script/appsscript.json",
    "excel-office-script/parva-functions.ts",
    "examples/sample-sheet.md",
}
FUNCTIONS = {
    "BS_TO_AD",
    "AD_TO_BS",
    "IS_NEPALI_HOLIDAY",
    "NEPALI_FISCAL_YEAR",
    "WORKING_DAY_NP",
}
FORBIDDEN_ROUTE_FRAGMENTS = (
    "/admin",
    "/billing",
    "/private",
    "/research",
    "/future-bs/exact",
    "/trust/mutate",
)


def validate_sheet_examples() -> list[str]:
    issues: list[str] = []
    for rel in sorted(REQUIRED):
        path = PACKAGE / rel
        if not path.exists():
            issues.append(f"missing {path.relative_to(ROOT).as_posix()}")
        elif path.is_file() and path.stat().st_size == 0:
            issues.append(f"empty {path.relative_to(ROOT).as_posix()}")

    code_paths = [
        PACKAGE / "google-apps-script" / "Code.gs",
        PACKAGE / "excel-office-script" / "parva-functions.ts",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in code_paths if path.exists())
    for function_name in sorted(FUNCTIONS):
        if not re.search(rf"\b{function_name}\b", combined):
            issues.append(f"missing spreadsheet function {function_name}")

    lower = combined.lower()
    for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
        if fragment in lower:
            issues.append(f"forbidden route fragment exposed: {fragment}")
    if "/v3/api/" not in combined:
        issues.append("examples must call stable /v3/api routes")

    readme = (PACKAGE / "README.md").read_text(encoding="utf-8") if (PACKAGE / "README.md").exists() else ""
    if "marketplace" in readme.lower() and "not marketplace" not in readme.lower():
        issues.append("README must not imply marketplace publication")
    if "not government" not in readme.lower() or "not_authority" not in combined:
        issues.append("spreadsheet examples must preserve no-authority boundary")
    return issues


def main() -> int:
    issues = validate_sheet_examples()
    if issues:
        for issue in issues:
            print(f"[sheets] {issue}")
        return 1
    print("Spreadsheet examples validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

