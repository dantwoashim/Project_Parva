#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

try:
    from .common import ROOT, TRUST_LOG_PATH, TrustToolError, load_json, repo_path
except ImportError:  # pragma: no cover - direct script execution
    from common import ROOT, TRUST_LOG_PATH, TrustToolError, load_json, repo_path

SHA256_REF_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
SUPPORTED_EVENTS = {
    "calendar.release.published",
    "calendar.official_release.verified",
    "calendar.release.diff_available",
    "calendar.risk_label.changed",
    "calendar.schedule.review_required",
    "calendar.future_assumption.resolved",
}
FORBIDDEN_TEXT = [
    re.compile("Info" + r"Developers", re.IGNORECASE),
    re.compile(r"\b" + "info" + r"dev\b", re.IGNORECASE),
    re.compile("cracked" + r"\s+Panchanga", re.IGNORECASE),
    re.compile("guaranteed" + r"\s+future", re.IGNORECASE),
    re.compile("official" + r"\s+future\s+calendar", re.IGNORECASE),
    re.compile("99%" + r"\s+future\s+accuracy", re.IGNORECASE),
]


def load_log_rows(log_path: Path = TRUST_LOG_PATH) -> list[dict[str, Any]]:
    log_path = repo_path(log_path)
    if not log_path.exists():
        raise TrustToolError(f"transparency log not found: {log_path}")
    rows: list[dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise TrustToolError(f"{log_path}:{line_number}: invalid JSONL row: {exc}") from exc
            if not isinstance(row, dict):
                raise TrustToolError(f"{log_path}:{line_number}: row must be an object")
            rows.append(row)
    if not rows:
        raise TrustToolError(f"transparency log has no entries: {log_path}")
    return rows


def _validate_row(row: dict[str, Any], *, line_number: int) -> None:
    required = {
        "event",
        "release_id",
        "artifact_hash",
        "source_registry_hash",
        "timestamp",
        "signature_ref",
    }
    missing = required - set(row)
    if missing:
        raise TrustToolError(f"line {line_number}: missing keys: {', '.join(sorted(missing))}")
    extra = set(row) - required - {"entry_id"}
    if extra:
        raise TrustToolError(f"line {line_number}: unexpected keys: {', '.join(sorted(extra))}")
    if "entry_id" in row:
        try:
            UUID(str(row["entry_id"]))
        except ValueError as exc:
            raise TrustToolError(f"line {line_number}: entry_id must be a UUID") from exc
    if row["event"] not in SUPPORTED_EVENTS:
        raise TrustToolError(f"line {line_number}: unsupported event {row['event']!r}")
    for key in ("artifact_hash", "source_registry_hash"):
        if not isinstance(row[key], str) or not SHA256_REF_RE.match(row[key]):
            raise TrustToolError(f"line {line_number}: {key} must be sha256:<hex>")
    signature_ref = row["signature_ref"]
    if not isinstance(signature_ref, str) or not signature_ref:
        raise TrustToolError(f"line {line_number}: signature_ref must be a string")
    signature_path = repo_path(signature_ref)
    if not signature_path.exists():
        raise TrustToolError(f"line {line_number}: signature_ref does not exist: {signature_ref}")
    load_json(signature_path)
    text = json.dumps(row, ensure_ascii=False)
    for pattern in FORBIDDEN_TEXT:
        if pattern.search(text):
            raise TrustToolError(f"line {line_number}: public-safety text matched")


def verify_log(log_path: Path = TRUST_LOG_PATH) -> dict[str, object]:
    rows = load_log_rows(log_path)
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, start=1):
        _validate_row(row, line_number=index)
        key = (str(row["release_id"]), str(row["artifact_hash"]))
        if key in seen:
            raise TrustToolError(f"line {index}: duplicate release artifact entry")
        seen.add(key)
    return {
        "valid": True,
        "log_path": str(repo_path(log_path).relative_to(ROOT)).replace("\\", "/"),
        "total_entries": len(rows),
        "events": sorted({str(row["event"]) for row in rows}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the alpha public transparency log JSONL file.")
    parser.add_argument("--log", default=str(TRUST_LOG_PATH.relative_to(ROOT)))
    args = parser.parse_args(argv)

    try:
        result = verify_log(Path(args.log))
    except TrustToolError as exc:
        print(f"transparency log verification failed: {exc}", file=sys.stderr)
        return 1

    print("Project Parva transparency log verification")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("transparency log verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
