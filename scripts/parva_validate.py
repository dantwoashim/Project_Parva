#!/usr/bin/env python3
"""Run Parva enterprise validation cases and emit a small report pack."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - depends on operator environment.
    requests = None


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    if requests is not None:
        response = requests.post(url, json=payload, timeout=20)
        return response.status_code, response.json()

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except json.JSONDecodeError:
            payload = {"detail": str(exc)}
        return exc.code, payload


def _get_json(url: str) -> tuple[int, dict]:
    if requests is not None:
        response = requests.get(url, timeout=20)
        return response.status_code, response.json()

    try:
        with request.urlopen(url, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except json.JSONDecodeError:
            payload = {"detail": str(exc)}
        return exc.code, payload


def _load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        cases = []
        for row in reader:
            cases.append(
                {
                    "id": (row.get("id") or "").strip(),
                    "type": (row.get("type") or "").strip(),
                    "input": (row.get("input") or "").strip(),
                    "expected": (row.get("expected") or "").strip(),
                    "category": (row.get("category") or "").strip(),
                    "notes": (row.get("notes") or "").strip(),
                }
            )
    return cases


def _fallback_convert(base_url: str, case: dict) -> tuple[bool, str | None, str | None]:
    case_type = case["type"]
    value = case["input"]
    if case_type == "ad_to_bs":
        status, body = _get_json(f"{base_url}/v3/api/calendar/convert?date={value}")
        if status != 200:
            return False, None, str(body.get("detail") or body)
        bs = body["bikram_sambat"]
        return True, f"{bs['year']:04d}-{bs['month']:02d}-{bs['day']:02d}", None
    if case_type == "bs_to_ad":
        try:
            year, month, day = [int(part) for part in value.split("-")]
        except ValueError:
            return False, None, f"Invalid BS date '{value}'. Use YYYY-MM-DD."
        status, body = _post_json(
            f"{base_url}/v3/api/calendar/bs-to-gregorian",
            {"year": year, "month": month, "day": day},
        )
        if status != 200:
            return False, None, str(body.get("detail") or body)
        return True, str(body["gregorian"]), None
    return False, None, f"Unsupported case type '{case_type}'."


def _fallback_validate(base_url: str, cases: list[dict]) -> dict:
    results = []
    passed = 0
    failed = 0
    generated_reference = 0

    for case in cases:
        ok, actual, err = _fallback_convert(base_url, case)
        expected = case["expected"]
        result = {
            "id": case["id"],
            "type": case["type"],
            "input": case["input"],
            "expected": expected,
            "actual": actual,
            "passed": False,
            "status": "failed",
        }
        if err:
            result["error"] = err

        if ok and expected == "":
            result["passed"] = True
            result["status"] = "generated_reference"
            generated_reference += 1
            passed += 1
        elif ok and expected == actual:
            result["passed"] = True
            result["status"] = "passed"
            passed += 1
        elif (not ok) and expected.upper() == "ERROR":
            result["passed"] = True
            result["status"] = "passed"
            passed += 1
        else:
            failed += 1

        results.append(result)

    total = len(cases)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "generated_reference": generated_reference,
        "pass_rate": round((passed / total) * 100.0, 2) if total else 0.0,
        "results": results,
    }


def _validate(base_url: str, cases: list[dict]) -> tuple[dict, str]:
    enterprise_cases = [
        {
            "id": row["id"],
            "type": row["type"],
            "input": row["input"],
            "expected": row["expected"],
        }
        for row in cases
    ]
    status, body = _post_json(f"{base_url}/v3/api/enterprise/validate", {"cases": enterprise_cases})
    if status == 200 and "results" in body:
        return body, "enterprise_validate"
    return _fallback_validate(base_url, cases), "calendar_fallback"


def _merge_case_metadata(cases: list[dict], summary: dict) -> list[dict]:
    case_meta = {case["id"]: case for case in cases}
    rows = []
    for result in summary["results"]:
        meta = case_meta.get(result["id"], {})
        rows.append(
            {
                **result,
                "category": meta.get("category", ""),
                "notes": meta.get("notes", ""),
            }
        )
    return rows


def _write_outputs(out_dir: Path, *, base_url: str, mode: str, rows: list[dict], summary: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    category_counts = Counter(row.get("category") or "uncategorized" for row in rows)
    summary_payload = {
        **{key: value for key, value in summary.items() if key != "results"},
        "generated_at": now,
        "base_url": base_url,
        "mode": mode,
        "category_breakdown": dict(sorted(category_counts.items())),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    fields = [
        "id",
        "type",
        "input",
        "expected",
        "actual",
        "passed",
        "status",
        "error",
        "category",
        "notes",
    ]
    with (out_dir / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    failed_rows = [row for row in rows if not row.get("passed")]
    generated_rows = [row for row in rows if row.get("status") == "generated_reference"]
    invalid_rows = [row for row in rows if row.get("expected", "").upper() == "ERROR"]
    lines = [
        "# Project Parva Validation Report",
        "",
        f"Generated: `{now}`",
        f"Base URL: `{base_url}`",
        f"Validation mode: `{mode}`",
        "",
        "## Summary",
        f"Total cases: {summary_payload['total']}",
        f"Passed: {summary_payload['passed']}",
        f"Failed: {summary_payload['failed']}",
        f"Generated reference cases: {summary_payload['generated_reference']}",
        f"Invalid input cases: {len(invalid_rows)}",
        f"Pass rate: {summary_payload['pass_rate']}%",
        "",
        "## Scope",
        "- AD to BS conversion",
        "- BS to AD conversion",
        "- fiscal boundary cases",
        "- month-end cases",
        "- invalid date handling",
        "",
        "## Category Breakdown",
        "",
        "| Category | Cases |",
        "|---|---:|",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(["", "## Mismatches And Errors", ""])
    if failed_rows:
        lines.extend(["| ID | Type | Input | Expected | Actual | Status | Error |", "|---|---|---|---|---|---|---|"])
        for row in failed_rows:
            lines.append(
                f"| {row.get('id', '')} | {row.get('type', '')} | {row.get('input', '')} | "
                f"{row.get('expected', '')} | {row.get('actual') or ''} | {row.get('status', '')} | "
                f"{row.get('error', '')} |"
            )
    else:
        lines.append("No mismatches or unexpected errors.")

    lines.extend(["", "## Generated Reference Cases", ""])
    if generated_rows:
        lines.extend(["| ID | Type | Input | Generated Actual | Category |", "|---|---|---|---|---|"])
        for row in generated_rows:
            lines.append(
                f"| {row.get('id', '')} | {row.get('type', '')} | {row.get('input', '')} | "
                f"{row.get('actual') or ''} | {row.get('category', '')} |"
            )
    else:
        lines.append("No generated reference cases.")

    lines.extend(
        [
            "",
            "## Notes",
            "This report is for technical evaluation, not final production certification.",
            "Holiday exclusion is not included in these conversion validation cases.",
            "",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Parva validation cases.")
    parser.add_argument("--input", required=True, help="CSV case file path")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--out-dir", default="validation_reports/latest")
    args = parser.parse_args()

    cases = _load_cases(Path(args.input))
    summary, mode = _validate(args.base_url.rstrip("/"), cases)
    rows = _merge_case_metadata(cases, summary)
    _write_outputs(Path(args.out_dir), base_url=args.base_url.rstrip("/"), mode=mode, rows=rows, summary=summary)

    print(f"Wrote {Path(args.out_dir) / 'summary.json'}")
    print(f"Wrote {Path(args.out_dir) / 'results.csv'}")
    print(f"Wrote {Path(args.out_dir) / 'report.md'}")
    return 0 if summary.get("failed", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
