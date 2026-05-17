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

    operation_verifiers = {
        "convert_bs_to_ad": "bs_to_gregorian",
        "ad_to_bs": "gregorian_to_bs",
        "validate_bs_date": "is_valid_bs_date",
        "holiday": "holiday_membership",
        "working_day": "working_day_policy",
        "fiscal_year": "fiscal_year_payload",
        "bs_months": "bs_months_payload",
        "panchanga_summary": "build_panchanga_summary_capsule",
    }
    for operation, recompute_marker in operation_verifiers.items():
        replay = PROJECT_ROOT / f"backend/app/membranes/operation_verifiers/{operation}.py"
        if not replay.exists():
            failures.append(f"{operation} operation replay verifier is missing")
            continue
        replay_source = replay.read_text(encoding="utf-8")
        common_marker = (
            "replayed_result_mismatch"
            if operation in {"convert_bs_to_ad", "panchanga_summary"}
            else "verify_common_replay"
        )
        if recompute_marker not in replay_source or common_marker not in replay_source:
            failures.append(f"{operation} replay verifier must recompute operation results")
        if operation not in {"convert_bs_to_ad", "panchanga_summary"} and "expected_result" not in replay_source:
            failures.append(f"{operation} replay verifier must compare expected_result")

    common_replay = _read("backend/app/membranes/operation_verifiers/common.py")
    if "source_docket_resolution_mismatch" not in common_replay:
        failures.append("civil replay verifier must enforce source docket resolution")
    if "source_authority_overclaim" not in common_replay:
        failures.append("civil replay verifier must reject source authority overclaims")

    local_kernel = _read("packages/parva-local-kernel/src/membranes.ts")
    if "Boolean(membrane.identity_hash && membrane.witness_hash)" in local_kernel:
        failures.append("local kernel verifyMembrane must not be field-presence-only")
    if "identity_hash_mismatch" not in local_kernel or "witness_hash_mismatch" not in local_kernel:
        failures.append("local kernel verifyMembrane must validate identity and witness hashes")
    if "proof_pack_result_hash_mismatch" not in local_kernel or "source_snapshot_hash_mismatch" not in local_kernel:
        failures.append("local kernel verifyMembrane must validate proof-pack and source snapshot linkage")
    if "replayMembrane" not in local_kernel or "fixture_not_found" not in local_kernel:
        failures.append("local kernel must perform fixture-backed membrane replay")
    if not (PROJECT_ROOT / "packages/parva-local-kernel/package.json").exists():
        failures.append("local kernel must be a buildable npm package")
    if len(list((PROJECT_ROOT / "tests/fixtures/proof/civil").glob("*.json"))) < 12:
        failures.append("shared civil proof fixtures must cover core replay cases")
    if not list((PROJECT_ROOT / "tests/fixtures/proof/panchanga").glob("*.json")):
        failures.append("Panchanga proof fixtures are missing")

    routes = _read("backend/app/calendar/routes.py")
    if "proof: str | None" not in routes or "build_convert_bs_to_ad_capsule" not in routes:
        failures.append("core BS-to-AD route must expose membrane proof mode")
    for route_marker in ("build_ad_to_bs_capsule", "build_validate_bs_date_capsule"):
        if route_marker not in routes:
            failures.append(f"calendar route must expose proof mode via {route_marker}")
    if "build_panchanga_summary_capsule" not in routes:
        failures.append("Panchanga route must expose method-docketed proof mode")

    panchanga_provider = _read("backend/app/panchanga/ephemeris_provider.py")
    if "JplEphemerisProvider" not in panchanga_provider or "kernel_hash" not in panchanga_provider:
        failures.append("Panchanga ephemeris layer must expose JPL provider interface with kernel hash")
    panchanga_proof = _read("backend/app/panchanga/proof.py")
    for marker in ("not_panchanga_authority", "not_ritual_final_authority", "ephemeris_metadata", "method_dockets"):
        if marker not in panchanga_proof:
            failures.append(f"Panchanga proof path missing {marker}")

    compliance_routes = _read("backend/app/api/compliance_routes.py")
    for route_marker in ("build_holiday_capsule", "build_working_day_capsule"):
        if route_marker not in compliance_routes:
            failures.append(f"compliance route must expose proof mode via {route_marker}")

    enterprise_routes = _read("backend/app/api/enterprise_routes.py")
    for route_marker in ("build_fiscal_year_capsule", "build_bs_months_capsule"):
        if route_marker not in enterprise_routes:
            failures.append(f"enterprise route must expose proof mode via {route_marker}")

    try:
        ast.parse(_read("backend/app/membranes/capsule.py"))
        ast.parse(_read("backend/app/membranes/verifier.py"))
        ast.parse(_read("backend/app/panchanga/proof.py"))
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
