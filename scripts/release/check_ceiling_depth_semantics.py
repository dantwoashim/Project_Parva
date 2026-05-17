#!/usr/bin/env python3
"""Semantic depth checks for proof-system primitives."""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def _failures() -> list[str]:
    failures: list[str] = []

    embed = _read("static/parva-embed.js")
    if "innerHTML" in embed:
        failures.append("static/parva-embed.js must not use innerHTML")
    if "textContent" not in embed or "replaceChildren" not in embed:
        failures.append("static/parva-embed.js must render via DOM text APIs")

    capsule = _read("backend/app/membranes/capsule.py")
    if "AuthorityTaint.STRUCTURED_OFFICIAL" in capsule:
        failures.append("membrane capsule must not hardcode structured_official authority")
    if "sample-2082-calendar-notice" in capsule:
        failures.append("membrane capsule must not hardcode the sample 2082 source docket")
    if "resolve_convert_bs_to_ad_source" not in capsule:
        failures.append("membrane capsule must use dynamic source resolution")

    verifier = _read("backend/app/membranes/verifier.py")
    if "replay_verify" not in verifier:
        failures.append("membrane verifier must dispatch to replay verification")

    replay = PROJECT_ROOT / "backend/app/membranes/operation_verifiers/convert_bs_to_ad.py"
    if not replay.exists():
        failures.append("convert_bs_to_ad operation replay verifier is missing")
    else:
        replay_source = replay.read_text(encoding="utf-8")
        if "bs_to_gregorian" not in replay_source or "replayed_result_mismatch" not in replay_source:
            failures.append("convert_bs_to_ad replay verifier must recompute conversion results")
        if "source_docket_resolution_mismatch" not in replay_source:
            failures.append("convert_bs_to_ad replay verifier must enforce source docket resolution")

    local_kernel = _read("packages/parva-local-kernel/src/membranes.ts")
    if "Boolean(membrane.identity_hash && membrane.witness_hash)" in local_kernel:
        failures.append("local kernel verifyMembrane must not be field-presence-only")
    if "identity_hash_mismatch" not in local_kernel or "witness_hash_mismatch" not in local_kernel:
        failures.append("local kernel verifyMembrane must validate identity and witness hashes")

    routes = _read("backend/app/calendar/routes.py")
    if "proof: str | None" not in routes or "build_convert_bs_to_ad_capsule" not in routes:
        failures.append("core BS-to-AD route must expose membrane proof mode")

    try:
        ast.parse(_read("backend/app/membranes/capsule.py"))
        ast.parse(_read("backend/app/membranes/verifier.py"))
    except SyntaxError as exc:
        failures.append(f"proof-system Python syntax error: {exc}")

    return failures


def main() -> int:
    failures = _failures()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Ceiling depth semantic checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
