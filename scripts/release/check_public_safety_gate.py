#!/usr/bin/env python3
"""Public release safety gate for Project Parva."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

PRIVATE_FUTURE_PATHS = {
    "/v4/api/future-bs/month-lengths/{bs_year}",
    "/v4/api/future-bs/month-lengths/range",
    "/v4/api/future-bs/month-lengths/export.csv",
    "/v4/api/future-bs/export.csv",
    "/v4/api/future-bs/export.xlsx",
    "/v4/api/future-bs/month-lengths/explain",
    "/v4/api/future-bs/boundary-risk",
    "/v4/api/future-bs/backtest",
    "/v4/api/future-bs/backtest/residuals",
    "/v4/api/future-bs/model-runs",
    "/v4/api/future-bs/loan-impact/simulate",
    "/v4/api/future-bs/month-lengths/import-excel",
    "/v4/api/future-bs/month-lengths/compare",
    "/v5/api/calendar-model-risk/prediction/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/prediction-set/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/committee-posterior/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/perturbation-robustness/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/audit-external-sheet",
    "/v5/api/calendar-model-risk/calendar-var",
    "/v5/api/calendar-model-risk/stress-test",
    "/v5/api/calendar-model-risk/red-team/2083-ashwin",
    "/v5/api/calendar-model-risk/claim-readiness",
}

PUBLIC_DEMO_BLOCKED_PREFIXES = (
    "/v3/api/agent",
    "/v3/api/protocol",
    "/v3/api/impact",
)

SCAN_ROOTS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "examples",
    PROJECT_ROOT / "frontend" / "src",
]

PROHIBITED_TEXT_PATTERNS = [
    re.compile(r"InfoDevelopers", re.IGNORECASE),
    re.compile(r"\binfodev\b", re.IGNORECASE),
    re.compile(r"cracked\s+Panchanga", re.IGNORECASE),
    re.compile(r"guaranteed\s+future", re.IGNORECASE),
    re.compile(r"official\s+future\s+calendar", re.IGNORECASE),
    re.compile(r"99%\s+future\s+accuracy", re.IGNORECASE),
]

PRIVATE_ROUTE_TOKENS = [
    "/v4/api/future-bs/month-lengths/",
    "/v4/api/future-bs/export.csv",
    "/v4/api/future-bs/export.xlsx",
    "/v4/api/future-bs/model-runs",
    "/v4/api/future-bs/backtest",
    "/v4/api/future-bs/loan-impact",
]

FUTURE_VECTOR_RE = re.compile(
    r"\b20(?:8[4-9]|9\d)\b[\s\S]{0,180}\[(?:\s*(?:29|30|31|32)\s*,){11}\s*(?:29|30|31|32)\s*\]",
    re.MULTILINE,
)


def _reset_env() -> None:
    os.environ["PARVA_ENABLE_EXPERIMENTAL_API"] = "false"
    os.environ["PARVA_SHOW_PRIVATE_SCHEMA"] = "false"
    os.environ["PARVA_RATE_LIMIT_ENABLED"] = "false"
    os.environ["PARVA_REQUIRE_PRECOMPUTED"] = "false"


def _client(*, public_demo: bool = False, allow_future: bool = False) -> TestClient:
    _reset_env()
    os.environ["PARVA_ENV"] = "public" if public_demo else "test"
    os.environ["PARVA_ROUTE_PROFILE"] = "public_demo" if public_demo else "full"
    os.environ["PARVA_SOURCE_URL"] = "https://github.com/dantwoashim/Project_Parva"
    os.environ["PARVA_ALLOW_PUBLIC_UNVERIFIED_FUTURE_CONVERSION"] = "true" if allow_future else "false"
    from app.bootstrap.app_factory import create_app

    return TestClient(create_app())


def _iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
        else:
            files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".json", ".ts", ".tsx", ".js", ".jsx", ".css", ".html"})
    return files


def _check_public_openapi() -> list[str]:
    client = _client()
    paths = set(client.get("/openapi.json").json()["paths"])
    failures = [f"private future path exposed in public OpenAPI: {path}" for path in sorted(PRIVATE_FUTURE_PATHS & paths)]
    return failures


def _check_public_demo_profile() -> list[str]:
    client = _client(public_demo=True)
    paths = set(client.get("/openapi.json").json()["paths"])
    failures = []
    for path in sorted(paths):
        if path.startswith(PUBLIC_DEMO_BLOCKED_PREFIXES):
            failures.append(f"public_demo exposes gated route: {path}")
    return failures


def _check_future_conversion_policy() -> list[str]:
    client = _client(public_demo=True)
    response = client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2084, "month": 1, "day": 1},
    )
    if response.status_code == 403 and "gregorian" not in response.json():
        return []
    return [f"public_demo exposed exact unverified future conversion: status={response.status_code} body={response.text[:200]}"]


def _check_protocol_schema_validation() -> list[str]:
    result = subprocess.run(
        [sys.executable, "tools/validate_schemas.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    return ["protocol schema validation failed:\n" + (result.stdout + result.stderr)[-4000:]]


def _check_public_text() -> list[str]:
    failures: list[str] = []
    for path in _iter_scan_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(PROJECT_ROOT)
        for pattern in PROHIBITED_TEXT_PATTERNS:
            if pattern.search(text):
                failures.append(f"{relative}: prohibited phrase matched {pattern.pattern}")
        for token in PRIVATE_ROUTE_TOKENS:
            if token in text:
                failures.append(f"{relative}: private route token exposed: {token}")
        if FUTURE_VECTOR_RE.search(text):
            failures.append(f"{relative}: possible full future month-length vector")
    return failures


def main() -> int:
    checks = [
        ("public OpenAPI future route boundary", _check_public_openapi),
        ("public demo route boundary", _check_public_demo_profile),
        ("public future conversion policy", _check_future_conversion_policy),
        ("protocol schema validation", _check_protocol_schema_validation),
        ("public text safety", _check_public_text),
    ]
    failures: list[str] = []
    for label, check in checks:
        result = check()
        if result:
            failures.extend(f"{label}: {failure}" for failure in result)
            print(f"FAIL {label}")
        else:
            print(f"PASS {label}")
    if failures:
        print("\nPublic safety gate failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Public safety gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
