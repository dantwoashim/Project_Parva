#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
PUBLICATION_STATUSES = {
    "official_verified",
    "printed_verified",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "needs_review",
    "computed_prediction_not_official",
}
SOURCE_POLICIES = {
    "official_strict",
    "printed_reviewed",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "experimental_shadow",
    "public_demo",
}
SOURCE_TIERS = {
    "official_verified",
    "printed_verified",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "needs_review",
}
FORBIDDEN_TEXT = [
    re.compile("Info" + r"Developers", re.IGNORECASE),
    re.compile(r"\b" + "info" + r"dev\b", re.IGNORECASE),
    re.compile("cracked" + r"\s+Panchanga", re.IGNORECASE),
    re.compile("99%" + r"\s+future\s+accuracy", re.IGNORECASE),
]
FORBIDDEN_FUTURE_YEAR_TEXT = ("20" + "84", "20" + "85", "20" + "99", "22" + "00")


class ReleaseVerificationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ReleaseVerificationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleaseVerificationError(f"{path}: root must be an object")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_keys(payload: dict[str, Any], keys: list[str], context: str) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise ReleaseVerificationError(f"{context}: missing required keys: {', '.join(missing)}")


def assert_public_safe(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    for pattern in FORBIDDEN_TEXT:
        if pattern.search(text):
            raise ReleaseVerificationError(f"{path}: forbidden public-safety text matched")
    if any(year_text in text for year_text in FORBIDDEN_FUTURE_YEAR_TEXT):
        raise ReleaseVerificationError(f"{path}: public demo release must not include future table years")


def validate_source_registry(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    require_keys(payload, ["registry_id", "version", "generated_at", "sources", "claim_boundary"], str(path))
    if not isinstance(payload["sources"], list) or not payload["sources"]:
        raise ReleaseVerificationError(f"{path}: sources must be a non-empty array")
    for index, source in enumerate(payload["sources"]):
        if not isinstance(source, dict):
            raise ReleaseVerificationError(f"{path}: sources[{index}] must be an object")
        require_keys(
            source,
            ["source_id", "source_name", "source_tier", "description", "claim_support_level", "notes"],
            f"{path}: sources[{index}]",
        )
        if source["source_tier"] not in SOURCE_TIERS:
            raise ReleaseVerificationError(f"{path}: sources[{index}].source_tier is invalid")
    boundary = payload["claim_boundary"]
    if not isinstance(boundary, dict):
        raise ReleaseVerificationError(f"{path}: claim_boundary must be an object")
    if boundary.get("future_outputs_status") != "computed_prediction_not_official":
        raise ReleaseVerificationError(
            f"{path}: claim_boundary.future_outputs_status must be computed_prediction_not_official"
        )
    assert_public_safe(path, payload)
    return payload


def validate_manifest(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    require_keys(
        payload,
        [
            "release_id",
            "calendar",
            "coverage",
            "source_policy",
            "publication_status",
            "artifact_hashes",
            "generated_at",
            "schemas_used",
            "claim_boundary",
        ],
        str(path),
    )
    if payload["source_policy"] not in SOURCE_POLICIES:
        raise ReleaseVerificationError(f"{path}: invalid source_policy")
    if payload["publication_status"] not in PUBLICATION_STATUSES:
        raise ReleaseVerificationError(f"{path}: invalid publication_status")
    coverage = payload["coverage"]
    if not isinstance(coverage, dict):
        raise ReleaseVerificationError(f"{path}: coverage must be an object")
    require_keys(
        coverage,
        ["bs_year_start", "bs_year_end", "ad_date_start", "ad_date_end", "scope", "future_values_included"],
        f"{path}: coverage",
    )
    if coverage.get("future_values_included") is not False:
        raise ReleaseVerificationError(f"{path}: public release must not include future values")
    if not isinstance(payload["artifact_hashes"], list) or not payload["artifact_hashes"]:
        raise ReleaseVerificationError(f"{path}: artifact_hashes must be a non-empty array")
    if not isinstance(payload["schemas_used"], list) or not payload["schemas_used"]:
        raise ReleaseVerificationError(f"{path}: schemas_used must be a non-empty array")
    boundary = payload["claim_boundary"]
    if not isinstance(boundary, dict):
        raise ReleaseVerificationError(f"{path}: claim_boundary must be an object")
    if boundary.get("future_outputs_status") != "computed_prediction_not_official":
        raise ReleaseVerificationError(
            f"{path}: claim_boundary.future_outputs_status must be computed_prediction_not_official"
        )
    assert_public_safe(path, payload)
    return payload


def resolve_repo_path(value: str) -> Path:
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ReleaseVerificationError(f"artifact path escapes repository root: {value}") from exc
    return candidate


def verify_artifacts(manifest: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    seen: set[str] = set()
    for index, artifact in enumerate(manifest["artifact_hashes"]):
        if not isinstance(artifact, dict):
            raise ReleaseVerificationError(f"artifact_hashes[{index}] must be an object")
        require_keys(artifact, ["artifact_id", "path", "sha256", "media_type"], f"artifact_hashes[{index}]")
        artifact_id = str(artifact["artifact_id"])
        if artifact_id in seen:
            raise ReleaseVerificationError(f"duplicate artifact_id: {artifact_id}")
        seen.add(artifact_id)
        expected = str(artifact["sha256"])
        if not SHA256_RE.match(expected):
            raise ReleaseVerificationError(f"{artifact_id}: invalid sha256 value")
        artifact_path = resolve_repo_path(str(artifact["path"]))
        if not artifact_path.exists():
            raise ReleaseVerificationError(f"{artifact_id}: missing artifact {artifact_path}")
        actual = sha256_file(artifact_path)
        if actual != expected:
            raise ReleaseVerificationError(
                f"{artifact_id}: hash mismatch for {artifact['path']}: expected {expected}, got {actual}"
            )
        if str(artifact["path"]).endswith(".sources.json"):
            validate_source_registry(artifact_path)
        messages.append(f"ok: {artifact_id} {artifact['path']} sha256:{actual}")
    return messages


def verify_schema_paths(manifest: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for schema_path in manifest["schemas_used"]:
        path = resolve_repo_path(str(schema_path))
        if not path.exists():
            raise ReleaseVerificationError(f"missing schema listed in schemas_used: {schema_path}")
        load_json(path)
        messages.append(f"ok: schema {schema_path}")
    return messages


def verify_release(manifest_path: Path) -> list[str]:
    manifest = validate_manifest(manifest_path)
    messages = [f"ok: manifest {manifest_path}"]
    messages.extend(verify_schema_paths(manifest))
    messages.extend(verify_artifacts(manifest))
    return messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a Project Parva public release manifest.")
    parser.add_argument("manifest", help="Path to release manifest JSON")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path

    try:
        messages = verify_release(manifest_path.resolve())
    except Exception as exc:  # noqa: BLE001
        print(f"release verification failed: {exc}", file=sys.stderr)
        return 1

    print("Project Parva release verification")
    for message in messages:
        print(message)
    print("release verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
