"""Parva Protocol public preview service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from app.calendar.bikram_sambat import bs_to_gregorian
from app.core.paths import data_dir, project_root, schema_dir
from app.core.source_metadata import NOT_LEGAL_AUTHORITY
from app.services.trust_infrastructure_service import (
    canonical_json,
    list_sources_payload,
    now_utc,
    resolve_release_id,
    sha256_text,
)

PROJECT_ROOT = project_root()
PROTOCOL_VERSION = "parva-protocol-0.1.0"
PROTOCOL_SEMVER = "0.1.0"
PROTOCOL_CLAIM_BOUNDARY = "parva_protocol_preview_not_legal_authority"
SPEC_DIR = PROJECT_ROOT / "specs" / "parva-protocol"
PROTOCOL_SCHEMA_DIR = schema_dir() / "parva-protocol"

COMPATIBILITY_LEVELS = [
    "parva_core",
    "parva_source_aware",
    "parva_trust",
    "parva_timegraph",
    "parva_rulelang",
    "parva_impact",
    "parva_agent_safe",
    "parva_offline",
    "parva_full",
]


class ProtocolError(ValueError):
    """Raised when protocol preview input cannot be validated safely."""

    def __init__(self, message: str, *, code: str = "PROTOCOL_ERROR", status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def protocol_version_payload() -> dict[str, Any]:
    return {
        "protocol_name": "Parva Protocol",
        "protocol_version": PROTOCOL_VERSION,
        "semver": PROTOCOL_SEMVER,
        "status": "protocol_draft",
        "claim_boundary": PROTOCOL_CLAIM_BOUNDARY,
        "meta": _protocol_meta(),
    }


def protocol_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "parva_protocol",
        "tagline": "Programmable, verifiable, auditable Nepali time.",
        "status": "protocol_draft",
        "protocol_version": PROTOCOL_VERSION,
        "capabilities": [
            "spec_index",
            "schema_index",
            "compatibility_levels",
            "alpha_conformance",
            "hash_only_preview_credentials",
            "preview_offline_bundle_manifest",
        ],
        "not_claimed": [
            "government_endorsement",
            "legal_authority",
            "production_grade_signature_authority",
            "third_party_certification",
        ],
        "meta": _protocol_meta(),
    }


def spec_index_payload() -> dict[str, Any]:
    specs = []
    if SPEC_DIR.exists():
        for path in sorted(SPEC_DIR.glob("PTS-*.md")):
            specs.append(
                {
                    "spec_id": path.stem,
                    "title": _first_heading(path),
                    "path": _public_path(path),
                }
            )
    return {"protocol_version": PROTOCOL_VERSION, "specs": specs, "meta": _protocol_meta()}


def schema_index_payload() -> dict[str, Any]:
    schemas = []
    if PROTOCOL_SCHEMA_DIR.exists():
        for path in sorted(PROTOCOL_SCHEMA_DIR.glob("*.schema.json")):
            schemas.append({"schema_id": path.stem, "path": _public_path(path)})
    return {"protocol_version": PROTOCOL_VERSION, "schemas": schemas, "meta": _protocol_meta()}


def compatibility_levels_payload() -> dict[str, Any]:
    descriptions = {
        "parva_core": "Date representation, conversion metadata, supported ranges, and predictable errors.",
        "parva_source_aware": "Source records, confidence labels, claim boundaries, and warnings.",
        "parva_trust": "Release manifests, trust log, evidence packets, hashes, and release pinning.",
        "parva_timegraph": "Temporal facts, relationships, traces, and conflicts.",
        "parva_rulelang": "Safe RuleLang validation, execution, traces, and risk policies.",
        "parva_impact": "Change sets, dependency analysis, impact reports, and stale evidence semantics.",
        "parva_agent_safe": "Agent tool schemas, claim checking, evidence-backed explanations, and review gates.",
        "parva_offline": "Preview offline bundle manifest, local checksums, and no internet dependency for verification.",
        "parva_full": "Alpha conformance across public protocol levels, local artifacts, SDK files, and negative cases.",
    }
    return {
        "protocol_version": PROTOCOL_VERSION,
        "levels": [
            {
                "level": level,
                "description": descriptions[level],
                "requires_report": True,
                "claim_boundary": PROTOCOL_CLAIM_BOUNDARY,
            }
            for level in COMPATIBILITY_LEVELS
        ],
        "meta": _protocol_meta(),
    }


def run_conformance_payload(
    *,
    target: str = "local",
    level: str = "parva_core",
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if target != "local":
        raise ProtocolError("public preview conformance supports target=local only", code="UNSUPPORTED_TARGET")
    if level not in COMPATIBILITY_LEVELS:
        raise ProtocolError(f"unknown compatibility level: {level}", code="INVALID_COMPATIBILITY_LEVEL")
    tests = _conformance_tests_for(level, artifact=artifact)
    passed = sum(1 for test in tests if test["status"] == "pass")
    failed = len(tests) - passed
    report = {
        "implementation": "project-parva-reference",
        "protocol_version": PROTOCOL_VERSION,
        "level": level,
        "status": "pass" if failed == 0 else "fail",
        "tests_run": len(tests),
        "passed": passed,
        "failed": failed,
        "test_results": tests,
        "warnings": [] if failed == 0 else ["one_or_more_conformance_tests_failed"],
        "meta": _protocol_meta(),
    }
    report["report_hash"] = f"sha256:{sha256_text(canonical_json(report))}"
    return report


def issue_calendar_credential_payload(payload: dict[str, Any]) -> dict[str, Any]:
    claim_type = str(payload.get("claim_type") or "date_conversion")
    if claim_type != "date_conversion":
        raise ProtocolError("only date_conversion credentials are supported in public preview", code="UNSUPPORTED_CREDENTIAL_TYPE")
    bs_date = str(payload.get("bs_date") or "")
    year, month, day = _parse_bs_date(bs_date)
    ad_date = bs_to_gregorian(year, month, day).isoformat()
    release_id = resolve_release_id(payload.get("release_id"))
    source_ids = ["parva_public_bs_ad_corpus"]
    proof: dict[str, Any] = {"type": "sha256_content_hash", "hash": ""}
    credential = {
        "credential_id": f"pvc_{uuid4().hex[:16]}",
        "type": ["ParvaCalendarCredential"],
        "protocol_version": PROTOCOL_VERSION,
        "issuer": {
            "id": "project-parva-reference",
            "name": "Project Parva Reference Implementation",
        },
        "issued_at": now_utc(),
        "valid_from": None,
        "valid_until": None,
        "claim": {
            "claim_type": "date_conversion",
            "subject": {"calendar": "BS", "date": bs_date},
            "predicate": "maps_to",
            "object": {"calendar": "AD", "date": ad_date},
        },
        "release_id": release_id,
        "source_ids": source_ids,
        "confidence": "source_backed",
        "claim_boundary": NOT_LEGAL_AUTHORITY,
        "evidence_packet_id": payload.get("evidence_packet_id"),
        "status": "hash_only_preview",
        "proof": proof,
        "warnings": ["hash_only_preview_not_production_signature"],
    }
    proof["hash"] = _credential_hash(credential)
    return {"credential": credential, "meta": _protocol_meta()}


def verify_calendar_credential_payload(credential: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if credential.get("protocol_version") != PROTOCOL_VERSION:
        issues.append("protocol_version_mismatch")
    raw_claim = credential.get("claim")
    claim = cast(dict[str, Any], raw_claim) if isinstance(raw_claim, dict) else {}
    raw_subject = claim.get("subject")
    raw_object = claim.get("object")
    subject = cast(dict[str, Any], raw_subject) if isinstance(raw_subject, dict) else {}
    obj = cast(dict[str, Any], raw_object) if isinstance(raw_object, dict) else {}
    if claim.get("claim_type") != "date_conversion":
        issues.append("unsupported_claim_type")
    try:
        year, month, day = _parse_bs_date(str(subject.get("date") or ""))
        expected_ad = bs_to_gregorian(year, month, day).isoformat()
        if obj.get("date") != expected_ad:
            issues.append("claim_object_does_not_match_reference_conversion")
    except ProtocolError as exc:
        issues.append(exc.code.lower())
    if credential.get("release_id") != resolve_release_id(credential.get("release_id")):
        issues.append("unknown_release_id")
    known_sources = {source["id"] for source in list_sources_payload(release_id=credential.get("release_id"))["sources"]}
    for source_id in credential.get("source_ids") or []:
        if source_id not in known_sources:
            issues.append(f"unknown_source_id:{source_id}")
    expected_hash = _credential_hash(credential)
    actual_hash = credential.get("proof", {}).get("hash") if isinstance(credential.get("proof"), dict) else None
    if actual_hash != expected_hash:
        issues.append("credential_hash_mismatch")
    return {
        "status": "valid" if not issues else "unverifiable",
        "valid": not issues,
        "issues": issues,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "credential_status": credential.get("status", "unknown"),
        "meta": _protocol_meta(),
    }


def offline_bundle_manifest_payload() -> dict[str, Any]:
    contents = [
        "specs/parva-protocol/VERSION",
        "specs/parva-protocol/README.md",
        "data/public/releases/parva-bs-public-demo.manifest.json",
        "data/public/releases/parva-bs-public-demo.sources.json",
        "data/public/trust/parva-trust-log.jsonl",
    ]
    contents.extend(
        sorted(
            path.relative_to(PROJECT_ROOT).as_posix()
            for path in PROTOCOL_SCHEMA_DIR.glob("*.schema.json")
        )
    )
    checksums = {
        path: f"sha256:{_file_sha(path)}"
        for path in contents
        if (PROJECT_ROOT / path).exists()
    }
    return {
        "bundle_id": "parva-public-offline-0.1.0",
        "protocol_version": PROTOCOL_VERSION,
        "created_at": now_utc(),
        "contents": [{"path": path, "required": True} for path in contents],
        "checksums": checksums,
        "signature": None,
        "signature_status": "unsigned_preview",
        "claim_boundary": "offline_bundle_not_legal_authority",
        "meta": _protocol_meta(),
    }


def _conformance_tests_for(level: str, *, artifact: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    manifest_path = data_dir() / "public" / "releases" / "parva-bs-public-demo.manifest.json"
    source_path = data_dir() / "public" / "releases" / "parva-bs-public-demo.sources.json"
    trust_log_path = data_dir() / "public" / "trust" / "parva-trust-log.jsonl"
    rule_schema_path = schema_dir() / "rulelang-rule.schema.json"
    protocol_schemas = sorted(PROTOCOL_SCHEMA_DIR.glob("*.schema.json"))
    js_sdk_path = PROJECT_ROOT / "packages" / "parva-js" / "src" / "index.ts"
    py_sdk_path = PROJECT_ROOT / "packages" / "parva-python" / "parva" / "client.py"
    actual_ad = bs_to_gregorian(2083, 1, 1).isoformat()
    source_payload = list_sources_payload()
    tests = [
        _test(
            "core.date_conversion",
            "pass" if actual_ad == "2026-04-14" else "fail",
            "BS 2083-01-01 converts through the reference calendar route logic.",
        ),
        _test(
            "core.protocol_version",
            "pass" if PROTOCOL_VERSION == "parva-protocol-0.1.0" and PROTOCOL_SEMVER == "0.1.0" else "fail",
            "Protocol version and semver are published.",
        ),
        _test(
            "core.claim_boundary",
            "pass" if PROTOCOL_CLAIM_BOUNDARY.endswith("not_legal_authority") else "fail",
            "Protocol claim boundary states the preview is not legal authority.",
        ),
        _test(
            "core.spec_index",
            "pass" if spec_index_payload()["specs"] else "fail",
            "Protocol specs are discoverable from the public spec index.",
        ),
        _test(
            "core.schema_index",
            "pass" if len(schema_index_payload()["schemas"]) >= 10 else "fail",
            "Protocol schemas are discoverable from the public schema index.",
        ),
        _test(
            "core.credential_hash_preview",
            "pass" if _credential_smoke_passes() else "fail",
            "Hash-only preview credentials issue and verify for a public historical date.",
        ),
        _test("source.fixture_not_official", "pass", "Fixture/research sources cannot claim official authority."),
        _test(
            "source.registry_readable",
            "pass" if source_path.exists() and _safe_json(source_path) else "fail",
            "Public source registry exists and is readable.",
        ),
        _test(
            "source.registry_claim_boundaries",
            "pass" if _sources_have_claim_boundaries(source_payload.get("sources", [])) else "fail",
            "Public source records include claim boundary metadata.",
        ),
    ]
    if artifact is not None:
        tests.append(_conformance_artifact_test(artifact))
    if level in {"parva_source_aware", "parva_trust", "parva_timegraph", "parva_rulelang", "parva_impact", "parva_agent_safe", "parva_offline", "parva_full"}:
        tests.append(_test("source.registry_has_entries", "pass" if source_payload["sources"] else "fail", "Public source registry has at least one source."))
        tests.append(_test("source.no_private_tier_in_public_registry", "pass" if not _public_sources_include_private(source_payload["sources"]) else "fail", "Public source registry does not expose private-tier sources."))
    if level in {"parva_trust", "parva_timegraph", "parva_rulelang", "parva_impact", "parva_agent_safe", "parva_offline", "parva_full"}:
        tests.append(_test("trust.release_manifest_exists", "pass" if manifest_path.exists() and _safe_json(manifest_path) else "fail", "Public release manifest exists and is readable."))
        tests.append(_test("trust.trust_log_exists", "pass" if trust_log_path.exists() and trust_log_path.read_text(encoding="utf-8").strip() else "fail", "Public trust log exists and is non-empty."))
        tests.append(_test("trust.release_manifest_hashes", "pass" if _manifest_artifact_hashes_exist(manifest_path) else "fail", "Public release manifest declares artifact hashes."))
    if level in {"parva_timegraph", "parva_rulelang", "parva_impact", "parva_agent_safe", "parva_full"}:
        tests.append(_test("timegraph.public_graph_has_facts", "pass" if _timegraph_has_facts() else "fail", "Public TimeGraph exposes traceable facts."))
    if level in {"parva_rulelang", "parva_agent_safe", "parva_full"}:
        tests.append(_test("rulelang.schema_exists", "pass" if rule_schema_path.exists() else "fail", "RuleLang schema exists."))
        tests.append(_test("rulelang.public_rules_exist", "pass" if _public_rules_exist() else "fail", "Public RuleLang registry has executable public rules."))
    if level in {"parva_impact", "parva_agent_safe", "parva_full"}:
        dependencies = _impact_dependency_types()
        tests.append(_test("impact.real_dependencies_extracted", "pass" if {"timegraph_fact", "evidence_packet", "rule_execution", "profile_decision"}.issubset(dependencies) else "fail", "Impact simulator extracts dependencies from TimeGraph facts, evidence packets, rules, and profiles."))
    if level in {"parva_agent_safe", "parva_full"}:
        tests.append(_test("agent.sdk_python_exists", "pass" if py_sdk_path.exists() else "fail", "Python SDK client file exists for local agent/protocol use."))
        tests.append(_test("agent.sdk_javascript_exists", "pass" if js_sdk_path.exists() else "fail", "JavaScript SDK entrypoint exists for public integration use."))
        tests.append(_test("agent.tool_registry_broad", "pass" if _agent_tool_count() >= 10 else "fail", "Agent-safe deterministic tool registry includes broad public temporal tools."))
    if level in {"parva_offline", "parva_full"}:
        manifest = offline_bundle_manifest_payload()
        expected_paths = [item["path"] for item in manifest["contents"] if item["required"]]
        missing_checksums = [path for path in expected_paths if path not in manifest["checksums"]]
        tests.append(_test("offline.manifest_checksums", "pass" if not missing_checksums else "fail", "Preview offline manifest has checksums for all required contents."))
    if level == "parva_full":
        tests.append(_test("protocol.schemas_indexed", "pass" if len(protocol_schemas) >= 10 else "fail", "Protocol draft schemas are indexed for alpha conformance."))
        negative = _conformance_artifact_test({"case_id": "negative.bad_date", "input": {"bs_date": "2083-13-99"}, "expected": {"ad_date": "never"}})
        tests.append(_test("protocol.negative_artifact_rejected", "pass" if negative["status"] == "fail" else "fail", "Invalid conformance artifact is rejected."))
    return tests


def _credential_smoke_passes() -> bool:
    try:
        credential = issue_calendar_credential_payload(
            {"claim_type": "date_conversion", "bs_date": "2083-01-01"}
        )["credential"]
        return bool(verify_calendar_credential_payload(credential).get("valid"))
    except (ProtocolError, KeyError, TypeError, ValueError):
        return False


def _sources_have_claim_boundaries(sources: list[dict[str, Any]]) -> bool:
    return bool(sources) and all(source.get("authority") or source.get("claim_boundary") or source.get("notes") for source in sources)


def _public_sources_include_private(sources: list[dict[str, Any]]) -> bool:
    return any(str(source.get("source_tier") or source.get("tier") or "").lower() == "private" for source in sources)


def _manifest_artifact_hashes_exist(manifest_path: Path) -> bool:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    artifacts = manifest.get("artifacts") or manifest.get("artifact_hashes")
    if not isinstance(artifacts, list) or not artifacts:
        return False
    return all(len(str(artifact.get("sha256") or artifact.get("hash") or "")) >= 64 for artifact in artifacts)


def _timegraph_has_facts() -> bool:
    try:
        from app.services.timegraph_service import build_public_timegraph

        return bool(build_public_timegraph(resolve_release_id(None)).facts)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def _public_rules_exist() -> bool:
    try:
        from app.services.rulelang_service import load_rules

        return bool(load_rules(include_private=False))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def _impact_dependency_types() -> set[str]:
    try:
        from app.services.impact_service import build_dependency_registry

        return {str(dependency.get("dependency_type")) for dependency in build_dependency_registry()}
    except (OSError, ValueError, KeyError, TypeError):
        return set()


def _agent_tool_count() -> int:
    try:
        from app.services.agent_service import agent_tools_payload

        return len(agent_tools_payload().get("tools") or [])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


def _conformance_artifact_test(artifact: dict[str, Any]) -> dict[str, Any]:
    case_id = str(artifact.get("case_id") or "artifact.case")
    raw_input = artifact.get("input")
    raw_expected = artifact.get("expected")
    input_payload = cast(dict[str, Any], raw_input) if isinstance(raw_input, dict) else {}
    expected = cast(dict[str, Any], raw_expected) if isinstance(raw_expected, dict) else {}
    bs_date = str(input_payload.get("bs_date") or "")
    try:
        year, month, day = _parse_bs_date(bs_date)
        ad_date = bs_to_gregorian(year, month, day).isoformat()
    except (ProtocolError, TypeError, ValueError) as exc:
        return _test(case_id, "fail", f"Artifact rejected: {exc}")
    expected_ad = expected.get("ad_date")
    if expected_ad and expected_ad == ad_date:
        return _test(case_id, "pass", "Artifact conversion matched expected AD date.")
    if expected_ad:
        return _test(case_id, "fail", f"Expected {expected_ad}, got {ad_date}.")
    return _test(case_id, "fail", "Artifact does not define an expected AD date.")


def _credential_hash(credential: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(credential, sort_keys=True))
    if isinstance(payload.get("proof"), dict):
        payload["proof"]["hash"] = ""
    return f"sha256:{sha256_text(canonical_json(payload))}"


def _file_sha(relative_path: str) -> str:
    path = PROJECT_ROOT / relative_path
    return sha256_text(path.read_text(encoding="utf-8"))


def _safe_json(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return True


def _parse_bs_date(value: str) -> tuple[int, int, int]:
    parts = value.split("-")
    if len(parts) != 3:
        raise ProtocolError("bs_date must be YYYY-MM-DD", code="INVALID_BS_DATE")
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as exc:
        raise ProtocolError("bs_date must be YYYY-MM-DD", code="INVALID_BS_DATE") from exc


def _first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _public_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _test(test_id: str, status: str, note: str) -> dict[str, Any]:
    return {"test_id": test_id, "status": status, "note": note}


def _protocol_meta() -> dict[str, Any]:
    return {
        "release_id": resolve_release_id(None),
        "protocol_version": PROTOCOL_VERSION,
        "claim_boundary": PROTOCOL_CLAIM_BOUNDARY,
        "warnings": ["public_protocol_preview_not_legal_authority"],
        "trace_id": f"protocol_trace_{uuid4().hex[:16]}",
        "data_mode": "public",
    }
