#!/usr/bin/env python3
"""Generate a machine-readable public trust status report."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.protocol_service import (  # noqa: E402
    PROTOCOL_VERSION,
    offline_bundle_manifest_payload,
)
from app.services.trust_infrastructure_service import (  # noqa: E402
    active_release_id,
    source_registry_checksum,
    validate_public_trust_artifacts,
)

from tools.validate_schemas import SCHEMA_PATHS, validate_schema_file  # noqa: E402


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sanitize_text(value: str) -> str:
    sanitized = value
    replacements = {
        str(PROJECT_ROOT): "<project-root>",
        PROJECT_ROOT.as_posix(): "<project-root>",
        str(Path(tempfile.gettempdir())): "<temp-dir>",
        Path(tempfile.gettempdir()).as_posix(): "<temp-dir>",
        sys.executable: "python",
    }
    for raw, replacement in replacements.items():
        if raw:
            sanitized = sanitized.replace(raw, replacement)
            sanitized = sanitized.replace(raw.replace("\\", "\\\\"), replacement)
    sanitized = re.sub(
        r"[A-Za-z]:\\\\Users\\\\[^\\\\\s\"]+(?:\\\\[^\\\\\s\"]+)*",
        "<local-user-path>",
        sanitized,
    )
    sanitized = re.sub(
        r"[A-Za-z]:\\Users\\[^\\\s\"]+(?:\\[^\\\s\"]+)*",
        "<local-user-path>",
        sanitized,
    )
    return sanitized


def _sanitize_command(command: list[str]) -> list[str]:
    return [_sanitize_text(arg) for arg in command]


def _run(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": _sanitize_command(command),
        "returncode": result.returncode,
        "ok": result.returncode == 0,
        "stdout_tail": [_sanitize_text(line) for line in result.stdout.strip().splitlines()[-5:]],
        "stderr_tail": [_sanitize_text(line) for line in result.stderr.strip().splitlines()[-5:]],
    }


def _schema_status() -> dict[str, Any]:
    failures: list[str] = []
    for path in SCHEMA_PATHS:
        try:
            validate_schema_file(path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.relative_to(PROJECT_ROOT)}: {exc}")
    return {"ok": not failures, "schema_count": len(SCHEMA_PATHS), "failures": failures}


def _offline_bundle_status() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="parva-trust-status-") as tmp:
        bundle_path = Path(tmp) / "bundle"
        bundle = _run([sys.executable, "scripts/parva_offline_bundle.py", "--output", str(bundle_path)])
        verify = _run([sys.executable, "scripts/parva_offline_verify.py", str(bundle_path)])
    manifest = offline_bundle_manifest_payload()
    return {
        "ok": bundle["ok"] and verify["ok"],
        "bundle": bundle,
        "verify": verify,
        "bundle_id": manifest.get("bundle_id"),
        "content_count": len(manifest.get("contents", [])),
        "checksum_count": len(manifest.get("checksums", {})),
        "signature_status": manifest.get("signature_status"),
    }


def build_report() -> dict[str, Any]:
    trust = validate_public_trust_artifacts()
    schema = _schema_status()
    leak = _run([sys.executable, "scripts/check_path_leaks.py"])
    offline = _offline_bundle_status()
    return {
        "generated_at": _now_utc(),
        "active_release_id": active_release_id(),
        "protocol_version": PROTOCOL_VERSION,
        "source_registry_hash": source_registry_checksum(),
        "manifest_status": {
            "ok": trust.get("ok"),
            "artifact_count": len(trust.get("artifact_results", [])),
            "issues": trust.get("issues", []),
        },
        "trust_verification_status": trust,
        "schema_validation_status": schema,
        "offline_bundle_status": offline,
        "public_private_leak_status": {
            "ok": leak["ok"],
            "command": leak["command"],
            "returncode": leak["returncode"],
            "stdout_tail": leak["stdout_tail"],
            "stderr_tail": leak["stderr_tail"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    report = build_report()
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output), "active_release_id": report["active_release_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
