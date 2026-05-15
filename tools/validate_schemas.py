from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATHS = [
    ROOT / "schemas" / "parva-date.schema.json",
    ROOT / "schemas" / "calendar-release.schema.json",
    ROOT / "schemas" / "release-manifest.schema.json",
    ROOT / "schemas" / "source-ref.schema.json",
    ROOT / "schemas" / "source-registry.schema.json",
    ROOT / "schemas" / "artifact-hash.schema.json",
    ROOT / "schemas" / "signature.schema.json",
    ROOT / "schemas" / "transparency-log-entry.schema.json",
    ROOT / "schemas" / "temporal-sbom.schema.json",
    ROOT / "schemas" / "calculation-trace.schema.json",
    ROOT / "schemas" / "future-risk.schema.json",
    ROOT / "schemas" / "blinded-audit-report.schema.json",
    ROOT / "schemas" / "reconciliation-event.schema.json",
    ROOT / "schemas" / "festival-occurrence.schema.json",
    ROOT / "schemas" / "panchanga-day.schema.json",
    ROOT / "schemas" / "nepal-fiscal-year.schema.json",
    ROOT / "schemas" / "external-temporal-rules.schema.json",
]
SCHEMA_PATHS.extend(sorted((ROOT / "schemas" / "parva-protocol").glob("*.schema.json")))

PUBLIC_SAFETY_PATTERNS = [
    re.compile("cracked" + r"\s+Panchanga", re.IGNORECASE),
    re.compile("guaranteed" + r"\s+future", re.IGNORECASE),
    re.compile("official" + r"\s+future\s+calendar", re.IGNORECASE),
    re.compile("99%" + r"\s+future\s+accuracy", re.IGNORECASE),
]


class SchemaValidationError(ValueError):
    pass


def _json_type(instance: Any) -> str:
    if instance is None:
        return "null"
    if isinstance(instance, bool):
        return "boolean"
    if isinstance(instance, int) and not isinstance(instance, bool):
        return "integer"
    if isinstance(instance, float):
        return "number"
    if isinstance(instance, str):
        return "string"
    if isinstance(instance, list):
        return "array"
    if isinstance(instance, dict):
        return "object"
    return type(instance).__name__


def _type_matches(instance: Any, expected: str | list[str]) -> bool:
    allowed = expected if isinstance(expected, list) else [expected]
    actual = _json_type(instance)
    if actual == "integer" and "number" in allowed:
        return True
    return actual in allowed


def _load_ref_schema(root_path: Path, ref: str) -> tuple[dict[str, Any], Path, str]:
    if "#" in ref:
        file_part, pointer = ref.split("#", 1)
        pointer = f"#{pointer}"
    else:
        file_part, pointer = ref, "#"
    target_path = root_path if not file_part else (root_path.parent / file_part).resolve()
    if not target_path.exists():
        raise SchemaValidationError(f"Reference file not found: {ref}")
    with target_path.open("r", encoding="utf-8") as handle:
        return json.load(handle), target_path, pointer


def _resolve_ref(root_schema: dict[str, Any], root_path: Path, ref: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    if not ref.startswith("#"):
        ref_schema, ref_path, pointer = _load_ref_schema(root_path, ref)
        if pointer == "#":
            return ref_schema, ref_schema, ref_path
        return _resolve_ref(ref_schema, ref_path, pointer)
    if not ref.startswith("#/"):
        if ref == "#":
            return root_schema, root_schema, root_path
        raise SchemaValidationError(f"Unsupported ref pointer: {ref}")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    if not isinstance(node, dict):
        raise SchemaValidationError(f"Reference does not resolve to a schema object: {ref}")
    return node, root_schema, root_path


def _check_format(value: str, fmt: str, path: str) -> None:
    if fmt == "date":
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise SchemaValidationError(f"{path}: invalid date format: {value}") from exc
    elif fmt == "date-time":
        candidate = value.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(candidate)
        except ValueError as exc:
            raise SchemaValidationError(f"{path}: invalid date-time format: {value}") from exc
    elif fmt == "uri":
        if not re.match(r"^https?://", value):
            raise SchemaValidationError(f"{path}: URI must start with http or https")


def _validate(
    instance: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    root_path: Path,
    path: str,
) -> None:
    if "$ref" in schema:
        ref_schema, next_root, next_root_path = _resolve_ref(root_schema, root_path, schema["$ref"])
        _validate(instance, ref_schema, next_root, next_root_path, path)
        return

    if "allOf" in schema:
        for index, option in enumerate(schema["allOf"]):
            _validate(instance, option, root_schema, root_path, f"{path}.allOf[{index}]")
        return

    if "oneOf" in schema:
        errors: list[str] = []
        matches = 0
        for option in schema["oneOf"]:
            try:
                _validate(instance, option, root_schema, root_path, path)
                matches += 1
            except SchemaValidationError as exc:
                errors.append(str(exc))
        if matches != 1:
            detail = "; ".join(errors[:3])
            raise SchemaValidationError(f"{path}: expected exactly one oneOf match, got {matches}. {detail}")
        return

    if "const" in schema and instance != schema["const"]:
        raise SchemaValidationError(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaValidationError(f"{path}: {instance!r} is not in enum")

    if "type" in schema and not _type_matches(instance, schema["type"]):
        raise SchemaValidationError(f"{path}: expected type {schema['type']}, got {_json_type(instance)}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaValidationError(f"{path}: string shorter than minLength")
        if "pattern" in schema and not re.match(schema["pattern"], instance):
            raise SchemaValidationError(f"{path}: string does not match pattern {schema['pattern']}")
        if "format" in schema:
            _check_format(instance, schema["format"], path)

    if isinstance(instance, int) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaValidationError(f"{path}: integer below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaValidationError(f"{path}: integer above maximum")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise SchemaValidationError(f"{path}: array shorter than minItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                _validate(item, item_schema, root_schema, root_path, f"{path}[{index}]")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise SchemaValidationError(f"{path}: missing required key {key!r}")

        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                _validate(value, properties[key], root_schema, root_path, f"{path}.{key}")
            else:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    raise SchemaValidationError(f"{path}: unexpected key {key!r}")
                if isinstance(additional, dict):
                    _validate(value, additional, root_schema, root_path, f"{path}.{key}")


def _check_public_safety(path: Path, schema: dict[str, Any]) -> None:
    text = json.dumps(schema, ensure_ascii=False)
    for pattern in PUBLIC_SAFETY_PATTERNS:
        if pattern.search(text):
            raise SchemaValidationError(f"{path}: public-safety pattern matched: {pattern.pattern}")

    if path.name == "future-risk.schema.json":
        for example in schema.get("examples", []):
            if example.get("publication_status") != "computed_prediction_not_official":
                raise SchemaValidationError(f"{path}: future-risk example must be computed_prediction_not_official")
            if example.get("corrected_value_included") is not False:
                raise SchemaValidationError(f"{path}: public future-risk example must not include corrected values")


def validate_schema_file(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise SchemaValidationError(f"{path}: expected JSON Schema draft 2020-12")
    if not schema.get("title"):
        raise SchemaValidationError(f"{path}: missing title")

    examples = schema.get("examples")
    if not isinstance(examples, list) or not examples:
        raise SchemaValidationError(f"{path}: missing non-empty examples array")

    for index, example in enumerate(examples):
        _validate(example, schema, schema, path, f"{path.name}.examples[{index}]")

    _check_public_safety(path, schema)


def main() -> int:
    missing = [path for path in SCHEMA_PATHS if not path.exists()]
    if missing:
        for path in missing:
            print(f"missing schema: {path}", file=sys.stderr)
        return 1

    failures: list[str] = []
    for path in SCHEMA_PATHS:
        try:
            validate_schema_file(path)
            print(f"ok: {path.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    if failures:
        print("\nSchema validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"validated {len(SCHEMA_PATHS)} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
