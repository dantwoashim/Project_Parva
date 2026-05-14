"""Public-safe temporal trust infrastructure for release audit surfaces."""

from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from app.core.paths import data_dir, project_root
from app.core.source_authority import PUBLIC_RELEASE_SOURCE_TIERS, normalize_source_tier
from app.core.source_metadata import NOT_LEGAL_AUTHORITY, PUBLIC_DATA_VERSION
from app.services.calendar_conversion_service import (
    build_bs_to_gregorian_payload,
    build_conversion_payload,
    parse_iso_date,
)
from app.services.compliance_service import evaluate_date_payload

PROJECT_ROOT = project_root()
PUBLIC_RELEASE_DIR = data_dir() / "public" / "releases"
DEFAULT_RELEASE_ID = "parva-bs-public-demo"
DEFAULT_MANIFEST_PATH = PUBLIC_RELEASE_DIR / f"{DEFAULT_RELEASE_ID}.manifest.json"
DEFAULT_SOURCE_REGISTRY_PATH = PUBLIC_RELEASE_DIR / f"{DEFAULT_RELEASE_ID}.sources.json"
DEFAULT_TRUST_LOG_PATH = data_dir() / "public" / "trust" / "parva-trust-log.jsonl"
PUBLIC_SIGNATURE_STATUS = "unsigned_public_preview"
ALLOWED_SOURCE_TIERS = frozenset(PUBLIC_RELEASE_SOURCE_TIERS)


class TrustInfrastructureError(ValueError):
    """Raised when release or trust input cannot be satisfied safely."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def active_release_id() -> str:
    return os.getenv("PARVA_ACTIVE_RELEASE_ID", DEFAULT_RELEASE_ID).strip() or DEFAULT_RELEASE_ID


def _repo_path(relative_path: str) -> Path:
    path = (PROJECT_ROOT / relative_path).resolve()
    try:
        path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise TrustInfrastructureError("release artifact path escapes repository root") from exc
    return path


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TrustInfrastructureError(f"invalid JSON artifact: {path.name}") from exc
    if not isinstance(payload, dict):
        raise TrustInfrastructureError(f"JSON artifact root must be an object: {path.name}")
    return payload


def _manifest_path_for(release_id: str) -> Path:
    if release_id != DEFAULT_RELEASE_ID:
        raise TrustInfrastructureError(f"unknown public release id: {release_id}", status_code=404)
    return DEFAULT_MANIFEST_PATH


def resolve_release_id(release_id: str | None = None) -> str:
    selected = release_id or active_release_id()
    _manifest_path_for(selected)
    return selected


def _load_manifest(release_id: str | None = None) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    path = _manifest_path_for(selected)
    if not path.exists():
        raise TrustInfrastructureError(f"release manifest not found: {selected}", status_code=404)
    manifest = _read_json(path)
    if manifest.get("release_id") != selected:
        raise TrustInfrastructureError("release manifest id does not match requested release")
    return manifest


def _load_source_registry_for_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    registry_path = DEFAULT_SOURCE_REGISTRY_PATH
    for artifact in manifest.get("artifact_hashes", []):
        if isinstance(artifact, dict) and artifact.get("artifact_id") == "source-registry":
            registry_path = _repo_path(str(artifact["path"]))
            break
    if not registry_path.exists():
        raise TrustInfrastructureError("source registry artifact is missing", status_code=404)
    return _read_json(registry_path)


def list_sources_payload(*, release_id: str | None = None) -> dict[str, Any]:
    manifest = _load_manifest(release_id)
    registry = _load_source_registry_for_manifest(manifest)
    sources = [_normalize_source_record(source) for source in registry.get("sources", [])]
    return {
        "release_id": manifest["release_id"],
        "registry_id": registry.get("registry_id"),
        "version": registry.get("version"),
        "generated_at": registry.get("generated_at"),
        "sources": sources,
        "claim_boundary": registry.get("claim_boundary", {}),
    }


def get_source_payload(source_id: str, *, release_id: str | None = None) -> dict[str, Any]:
    payload = list_sources_payload(release_id=release_id)
    for source in payload["sources"]:
        if source["id"] == source_id:
            return {
                "release_id": payload["release_id"],
                "source": source,
                "claim_boundary": payload["claim_boundary"],
            }
    raise TrustInfrastructureError(f"unknown source id: {source_id}", status_code=404)


def list_releases_payload() -> dict[str, Any]:
    active = active_release_id()
    releases = []
    for path in sorted(PUBLIC_RELEASE_DIR.glob("*.manifest.json")):
        try:
            manifest = _read_json(path)
        except TrustInfrastructureError:
            continue
        release_id = str(manifest.get("release_id") or "")
        if release_id:
            releases.append(_public_manifest(manifest, active_release_id=active))
    return {
        "active_release_id": active,
        "default_release_id": DEFAULT_RELEASE_ID,
        "releases": releases,
    }


def get_release_payload(release_id: str | None = None) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    manifest = _load_manifest(selected)
    return {
        "active_release_id": active_release_id(),
        "release": _public_manifest(manifest, active_release_id=active_release_id()),
    }


def _public_manifest(manifest: dict[str, Any], *, active_release_id: str) -> dict[str, Any]:
    payload = deepcopy(manifest)
    payload["is_active"] = manifest.get("release_id") == active_release_id
    payload["manifest_hash"] = f"sha256:{sha256_file(_manifest_path_for(str(manifest['release_id'])))}"
    return payload


def _normalize_source_record(source: dict[str, Any]) -> dict[str, Any]:
    tier = normalize_source_tier(str(source.get("source_tier") or "unknown"))
    if tier not in ALLOWED_SOURCE_TIERS:
        tier = "unknown"
    return {
        "id": source.get("source_id"),
        "label": source.get("source_name"),
        "tier": tier,
        "authority": source.get("claim_support_level", "unknown"),
        "description": source.get("description"),
        "url": source.get("url"),
        "reviewed_at": source.get("reviewed_at"),
        "notes": source.get("notes"),
    }


def load_trust_log_payload(*, release_id: str | None = None) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    if not DEFAULT_TRUST_LOG_PATH.exists():
        return {
            "release_id": selected,
            "log_path": str(DEFAULT_TRUST_LOG_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "entries": [],
            "warnings": ["trust_log_not_found"],
        }
    entries: list[dict[str, Any]] = []
    with DEFAULT_TRUST_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            row = json.loads(raw)
            if row.get("release_id") == selected:
                entries.append(row)
    return {
        "release_id": selected,
        "log_path": str(DEFAULT_TRUST_LOG_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "entries": entries,
        "warnings": [],
    }


def diff_releases_payload(from_release: str, to_release: str) -> dict[str, Any]:
    from_manifest = _load_manifest(from_release)
    to_manifest = _load_manifest(to_release)
    from_sources = list_sources_payload(release_id=from_release)["sources"]
    to_sources = list_sources_payload(release_id=to_release)["sources"]
    source_changes = _diff_by_id(from_sources, to_sources, id_key="id")
    artifact_changes = _diff_by_id(
        from_manifest.get("artifact_hashes", []),
        to_manifest.get("artifact_hashes", []),
        id_key="artifact_id",
    )
    capability_changes = _diff_values(
        from_manifest.get("capabilities", []),
        to_manifest.get("capabilities", []),
    )
    return {
        "from_release": from_release,
        "to_release": to_release,
        "diff_scope": "manifest_source_artifact_only",
        "summary": {
            "sources_added": len(source_changes["added"]),
            "sources_removed": len(source_changes["removed"]),
            "sources_changed": len(source_changes["changed"]),
            "artifacts_added": len(artifact_changes["added"]),
            "artifacts_removed": len(artifact_changes["removed"]),
            "artifacts_changed": len(artifact_changes["changed"]),
            "capabilities_added": len(capability_changes["added"]),
            "capabilities_removed": len(capability_changes["removed"]),
        },
        "changes": {
            "sources": source_changes,
            "artifacts": artifact_changes,
            "capabilities": capability_changes,
        },
        "warnings": [
            "Release diff is metadata-level only. It does not claim semantic holiday or business-day impact."
        ],
    }


def _diff_by_id(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    *,
    id_key: str,
) -> dict[str, list[Any]]:
    before_map = {str(item.get(id_key)): item for item in before if isinstance(item, dict)}
    after_map = {str(item.get(id_key)): item for item in after if isinstance(item, dict)}
    before_keys = set(before_map)
    after_keys = set(after_map)
    common = before_keys & after_keys
    return {
        "added": sorted(after_keys - before_keys),
        "removed": sorted(before_keys - after_keys),
        "changed": sorted(key for key in common if before_map[key] != after_map[key]),
    }


def _diff_values(before: list[Any], after: list[Any]) -> dict[str, list[Any]]:
    before_set = {json.dumps(value, sort_keys=True) for value in before}
    after_set = {json.dumps(value, sort_keys=True) for value in after}
    return {
        "added": sorted(json.loads(value) for value in after_set - before_set),
        "removed": sorted(json.loads(value) for value in before_set - after_set),
    }


def trust_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "temporal_trust_infrastructure",
        "status": "public_preview",
        "active_release_id": active_release_id(),
        "default_release_id": DEFAULT_RELEASE_ID,
        "public_surfaces": [
            "source_registry",
            "release_manifest",
            "release_diff",
            "trust_log",
            "date_conversion_evidence_packet",
            "compliance_decision_evidence_packet",
            "rule_execution_evidence_packet",
        ],
        "version_pinning": {
            "query_parameter": "release_id",
            "header": "x-parva-release-id",
            "unknown_release_behavior": "clear_404_error",
        },
        "claim_boundary": NOT_LEGAL_AUTHORITY,
        "not_claimed": [
            "official_calendar_publication",
            "legal_or_tax_authority",
            "production_grade_cryptographic_signature",
        ],
    }


def build_date_conversion_evidence_packet(
    *,
    release_id: str | None = None,
    ad_date: str | None = None,
    bs_date: str | None = None,
    trace_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    if bool(ad_date) == bool(bs_date):
        raise TrustInfrastructureError("provide exactly one of ad_date or bs_date")
    if ad_date:
        parsed = parse_iso_date(ad_date)
        result = build_conversion_payload(parsed, trace_id=trace_id)
        request_input: dict[str, Any] = {"ad_date": parsed.isoformat(), "direction": "ad_to_bs"}
    else:
        year, month, day = _parse_bs_date_string(str(bs_date))
        result = build_bs_to_gregorian_payload(year, month, day, trace_id=trace_id)
        request_input = {
            "bs_date": f"{year:04d}-{month:02d}-{day:02d}",
            "direction": "bs_to_ad",
        }
    return build_evidence_packet(
        packet_type="date_conversion",
        input_payload=request_input,
        result=result,
        release_id=selected,
        trace_id=trace_id,
        generated_at=generated_at,
    )


def build_compliance_decision_evidence_packet(
    *,
    release_id: str | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
    decision_intent: str = "general",
    trace_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    result = evaluate_date_payload(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        decision_intent=decision_intent,
        trace_id=trace_id,
    )
    return build_evidence_packet(
        packet_type="compliance_decision",
        input_payload={
            "profile_id": profile_id,
            "bs_date": bs_date,
            "ad_date": ad_date,
            "decision_intent": decision_intent,
        },
        result=result,
        release_id=selected,
        trace_id=trace_id,
        generated_at=generated_at,
    )


def build_rule_execution_evidence_packet(
    *,
    release_id: str | None = None,
    rule_id: str,
    input_payload: dict[str, Any],
    trace_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    from app.services.rulelang_service import RuleLangError, evaluate_rule_payload  # noqa: PLC0415

    try:
        result = evaluate_rule_payload(
            rule_id,
            input_payload,
            release_id=selected,
            trace_id=trace_id,
            include_evidence=False,
        )
    except RuleLangError as exc:
        raise TrustInfrastructureError(str(exc), status_code=exc.status_code) from exc
    return build_evidence_packet(
        packet_type="rule_execution",
        input_payload={
            "rule_id": rule_id,
            "input": input_payload,
        },
        result=result,
        release_id=selected,
        trace_id=trace_id,
        generated_at=generated_at,
    )


def _parse_bs_date_string(value: str) -> tuple[int, int, int]:
    parts = value.split("-")
    if len(parts) != 3:
        raise TrustInfrastructureError("bs_date must be YYYY-MM-DD")
    try:
        year, month, day = (int(part) for part in parts)
    except ValueError as exc:
        raise TrustInfrastructureError("bs_date must be YYYY-MM-DD") from exc
    return year, month, day


def build_evidence_packet(
    *,
    packet_type: str,
    input_payload: dict[str, Any],
    result: dict[str, Any],
    release_id: str,
    trace_id: str | None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    manifest = _load_manifest(release_id)
    raw_meta = result.get("meta")
    meta = cast(dict[str, Any], raw_meta) if isinstance(raw_meta, dict) else {}
    from app.services.timegraph_service import (  # noqa: PLC0415
        fact_ids_for_compliance_result,
        fact_ids_for_date_conversion_result,
    )

    if packet_type == "date_conversion":
        fact_ids = fact_ids_for_date_conversion_result(result)
    elif packet_type == "compliance_decision":
        fact_ids = fact_ids_for_compliance_result(result)
    elif packet_type == "rule_execution":
        fact_ids = list(result.get("fact_ids") or [])
    else:
        fact_ids = []
    sources = _sources_for_result(meta, release_id=release_id)
    warnings = list(meta.get("warnings") or [])
    if manifest.get("claim_boundary", {}).get("not_legal_or_banking_authority"):
        warnings.append("not_legal_or_banking_contract_authority")
    body = {
        "packet_id": "",
        "packet_type": packet_type,
        "generated_at": generated_at or now_utc(),
        "input": input_payload,
        "result": result,
        "release": {
            "release_id": release_id,
            "data_version": meta.get("data_version") or PUBLIC_DATA_VERSION,
            "manifest_hash": f"sha256:{sha256_file(_manifest_path_for(release_id))}",
        },
        "sources": sources,
        "confidence": meta.get("confidence", "unknown"),
        "claim_boundary": meta.get("claim_boundary") or NOT_LEGAL_AUTHORITY,
        "warnings": sorted(set(warnings)),
        "trace_id": trace_id or meta.get("trace_id"),
        "fact_ids": fact_ids,
    }
    packet_id_hash = sha256_text(canonical_json({**body, "packet_id": ""}))[:24]
    body["packet_id"] = f"evidence_{packet_id_hash}"
    packet_hash = sha256_text(canonical_json(body))
    body["integrity"] = {
        "packet_hash": f"sha256:{packet_hash}",
        "signature": None,
        "signature_status": PUBLIC_SIGNATURE_STATUS,
    }
    return body


def _sources_for_result(meta: dict[str, Any], *, release_id: str) -> list[dict[str, Any]]:
    source = meta.get("source") if isinstance(meta.get("source"), dict) else None
    registry_sources = {
        source_record["id"]: source_record
        for source_record in list_sources_payload(release_id=release_id)["sources"]
    }
    if not source:
        return []
    source_id = source.get("id")
    normalized = dict(registry_sources.get(source_id, {}))
    if not normalized:
        normalized = {
            "id": source_id,
            "label": source.get("label"),
            "tier": source.get("tier", "unknown"),
            "authority": source.get("authority", "unknown"),
        }
    normalized["checksum"] = source_registry_checksum(release_id=release_id)
    return [normalized]


def source_registry_checksum(*, release_id: str | None = None) -> str:
    manifest = _load_manifest(release_id)
    for artifact in manifest.get("artifact_hashes", []):
        if isinstance(artifact, dict) and artifact.get("artifact_id") == "source-registry":
            return f"sha256:{artifact['sha256']}"
    return ""


def validate_public_trust_artifacts() -> dict[str, Any]:
    releases = list_releases_payload()
    active = releases["active_release_id"]
    manifest = _load_manifest(active)
    registry = _load_source_registry_for_manifest(manifest)
    issues: list[str] = []
    source_ids: set[str] = set()
    for source in registry.get("sources", []):
        source_id = source.get("source_id")
        if not source_id:
            issues.append("source missing source_id")
            continue
        if source_id in source_ids:
            issues.append(f"duplicate source id: {source_id}")
        source_ids.add(str(source_id))
        tier = normalize_source_tier(str(source.get("source_tier") or "unknown"))
        if tier not in ALLOWED_SOURCE_TIERS:
            issues.append(f"{source_id}: invalid source tier {tier!r}")
    artifact_results = []
    for artifact in manifest.get("artifact_hashes", []):
        path = _repo_path(str(artifact["path"]))
        expected = str(artifact["sha256"])
        if not path.exists():
            issues.append(f"missing artifact: {artifact['path']}")
            continue
        actual = sha256_file(path)
        artifact_results.append(
            {
                "artifact_id": artifact.get("artifact_id"),
                "path": artifact.get("path"),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "ok": expected == actual,
            }
        )
        if expected != actual:
            issues.append(f"{artifact['artifact_id']}: sha256 mismatch")
    log = load_trust_log_payload(release_id=active)
    return {
        "ok": not issues,
        "active_release_id": active,
        "source_count": len(registry.get("sources", [])),
        "artifact_results": artifact_results,
        "trust_log_entries": len(log["entries"]),
        "issues": issues,
    }
