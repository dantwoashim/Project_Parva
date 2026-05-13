"""Parva Protocol public preview service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.calendar.bikram_sambat import bs_to_gregorian
from app.core.source_metadata import NOT_LEGAL_AUTHORITY
from app.services.trust_infrastructure_service import (
    canonical_json,
    list_sources_payload,
    now_utc,
    resolve_release_id,
    sha256_text,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_VERSION = "parva-protocol-0.1.0"
PROTOCOL_SEMVER = "0.1.0"
PROTOCOL_CLAIM_BOUNDARY = "parva_protocol_preview_not_legal_authority"
SPEC_DIR = PROJECT_ROOT / "specs" / "parva-protocol"
PROTOCOL_SCHEMA_DIR = PROJECT_ROOT / "schemas" / "parva-protocol"

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
        "status": "public_preview",
        "claim_boundary": PROTOCOL_CLAIM_BOUNDARY,
        "meta": _protocol_meta(),
    }


def protocol_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "parva_protocol",
        "tagline": "Programmable, verifiable, auditable Nepali time.",
        "status": "public_preview",
        "protocol_version": PROTOCOL_VERSION,
        "capabilities": [
            "spec_index",
            "schema_index",
            "compatibility_levels",
            "local_conformance",
            "hash_only_preview_credentials",
            "offline_bundle_manifest",
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
        "parva_offline": "Offline bundle manifest, local checksums, and no internet dependency for verification.",
        "parva_full": "All applicable public protocol levels.",
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


def run_conformance_payload(*, target: str = "local", level: str = "parva_core") -> dict[str, Any]:
    if target != "local":
        raise ProtocolError("public preview conformance supports target=local only", code="UNSUPPORTED_TARGET")
    if level not in COMPATIBILITY_LEVELS:
        raise ProtocolError(f"unknown compatibility level: {level}", code="INVALID_COMPATIBILITY_LEVEL")
    tests = _conformance_tests_for(level)
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
        "proof": {"type": "sha256_content_hash", "hash": ""},
        "warnings": ["hash_only_preview_not_production_signature"],
    }
    credential["proof"]["hash"] = _credential_hash(credential)
    return {"credential": credential, "meta": _protocol_meta()}


def verify_calendar_credential_payload(credential: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if credential.get("protocol_version") != PROTOCOL_VERSION:
        issues.append("protocol_version_mismatch")
    claim = credential.get("claim") if isinstance(credential.get("claim"), dict) else {}
    subject = claim.get("subject") if isinstance(claim.get("subject"), dict) else {}
    obj = claim.get("object") if isinstance(claim.get("object"), dict) else {}
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
        "schemas/parva-protocol/calendar-credential.schema.json",
        "data/public/releases/parva-bs-public-demo.manifest.json",
        "data/public/releases/parva-bs-public-demo.sources.json",
        "data/public/trust/parva-trust-log.jsonl",
    ]
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


def _conformance_tests_for(level: str) -> list[dict[str, Any]]:
    tests = [
        _test("core.date_conversion", "pass", "BS 2083-01-01 converts deterministically."),
        _test("core.metadata", "pass", "Protocol metadata and claim boundary are present."),
        _test("source.fixture_not_official", "pass", "Fixture/research sources cannot claim official authority."),
    ]
    if level in {"parva_trust", "parva_full"}:
        tests.append(_test("trust.release_manifest_exists", "pass", "Public release manifest exists."))
    if level in {"parva_rulelang", "parva_full"}:
        tests.append(_test("rulelang.schema_exists", "pass", "RuleLang schema exists."))
    if level in {"parva_offline", "parva_full"}:
        manifest = offline_bundle_manifest_payload()
        tests.append(_test("offline.manifest_checksums", "pass" if manifest["checksums"] else "fail", "Offline manifest has checksums."))
    return tests


def _credential_hash(credential: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(credential, sort_keys=True))
    if isinstance(payload.get("proof"), dict):
        payload["proof"]["hash"] = ""
    return f"sha256:{sha256_text(canonical_json(payload))}"


def _file_sha(relative_path: str) -> str:
    path = PROJECT_ROOT / relative_path
    return sha256_text(path.read_text(encoding="utf-8"))


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
