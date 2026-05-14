#!/usr/bin/env python3
"""Validate the Phase 03 canonical runtime registry and import boundaries."""

from __future__ import annotations

import ast
import fnmatch
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
APP_ROOT = BACKEND_ROOT / "app"
REGISTRY_PATH = PROJECT_ROOT / "config" / "canonical-runtime.yaml"


class CanonicalRuntimeError(AssertionError):
    """Raised when a canonical runtime invariant fails."""


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load the registry. The file is JSON syntax, which is valid YAML."""
    if not path.exists():
        raise CanonicalRuntimeError(f"Missing registry: {path.relative_to(PROJECT_ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CanonicalRuntimeError(f"Registry is not valid JSON/YAML subset: {exc}") from exc
    if not isinstance(payload, dict):
        raise CanonicalRuntimeError("Registry root must be an object.")
    return payload


def module_to_path(module_name: str) -> Path | None:
    """Map an app module name to the file or package path in backend/app."""
    if not module_name.startswith("app."):
        return None
    rel_parts = module_name.split(".")[1:]
    module_file = APP_ROOT.joinpath(*rel_parts).with_suffix(".py")
    if module_file.exists():
        return module_file
    package_init = APP_ROOT.joinpath(*rel_parts, "__init__.py")
    if package_init.exists():
        return package_init
    package_dir = APP_ROOT.joinpath(*rel_parts)
    if package_dir.exists():
        return package_dir
    return module_file


def module_name_for_path(path: Path) -> str:
    rel = path.relative_to(BACKEND_ROOT).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    module_name = module_name_for_path(path)
    package_parts = module_name.split(".")[:-1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.level == 0:
                    imports.add(node.module)
                else:
                    prefix = (
                        package_parts[: -(node.level - 1)] if node.level > 1 else package_parts
                    )
                    imports.add(".".join(prefix + node.module.split(".")))
            elif node.level > 0:
                prefix = package_parts[: -(node.level - 1)] if node.level > 1 else package_parts
                imports.add(".".join(prefix))
    return imports


def import_matches(imported: str, target: str) -> bool:
    return imported == target or imported.startswith(f"{target}.")


def module_matches(module_name: str, pattern: str) -> bool:
    return fnmatch.fnmatch(module_name, pattern)


def runtime_python_files() -> list[Path]:
    return sorted(APP_ROOT.rglob("*.py"))


def files_for_glob(pattern: str) -> list[Path]:
    return sorted(path for path in PROJECT_ROOT.glob(pattern) if path.is_file())


def check_registry_structure(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    areas = registry.get("areas")
    if not isinstance(areas, list) or not areas:
        return ["Registry must contain a non-empty areas list."]

    ids = {area.get("id") for area in areas if isinstance(area, dict)}
    for required_id in registry.get("required_area_ids", []):
        if required_id not in ids:
            failures.append(f"Missing required canonical area: {required_id}")

    required_fields = {
        "id",
        "lane",
        "maturity",
        "canonical_modules",
        "canonical_paths",
        "public_routes",
        "tests",
        "compatibility_modules",
        "deprecated_modules",
        "deprecated_paths",
        "research_private_dependencies",
        "verification_command",
        "owner_team",
    }
    for area in areas:
        missing = sorted(required_fields - set(area))
        if missing:
            failures.append(f"{area.get('id', '<unknown>')}: missing fields {', '.join(missing)}")
    return failures


def check_canonical_paths(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for area in registry.get("areas", []):
        area_id = area.get("id", "<unknown>")
        for rel_path in area.get("canonical_paths", []):
            if not (PROJECT_ROOT / rel_path).exists():
                failures.append(f"{area_id}: missing canonical path {rel_path}")
        for module_name in area.get("canonical_modules", []):
            mapped = module_to_path(module_name)
            if mapped is not None and not mapped.exists():
                failures.append(f"{area_id}: missing canonical module {module_name}")
    return failures


def check_test_references(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for area in registry.get("areas", []):
        area_id = area.get("id", "<unknown>")
        for test in area.get("tests", []):
            path = str(test.get("path", ""))
            status = test.get("status")
            if status == "exists" and not (PROJECT_ROOT / path).exists():
                failures.append(f"{area_id}: missing referenced test {path}")
            if status not in {"exists", "planned_todo"}:
                failures.append(f"{area_id}: test {path} has invalid status {status!r}")
            if status == "planned_todo" and not test.get("reason"):
                failures.append(f"{area_id}: planned TODO test {path} needs a reason")
    return failures


def _deprecated_module_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for area in registry.get("areas", []):
        for row in area.get("deprecated_modules", []):
            if isinstance(row, dict):
                rows.append(row)
    return rows


def check_deprecated_imports(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    deprecated = _deprecated_module_rows(registry)
    if not deprecated:
        return failures

    for path in runtime_python_files():
        importer = module_name_for_path(path)
        imports = imported_modules(path)
        for row in deprecated:
            module_name = row["module"]
            if not any(import_matches(imported, module_name) for imported in imports):
                continue
            allowed = row.get("allowed_importers", [])
            if any(module_matches(importer, pattern) for pattern in allowed):
                continue
            failures.append(
                f"{importer} imports deprecated {module_name}; replacement is {row.get('replacement')}"
            )
    return failures


def check_public_route_research_imports(registry: dict[str, Any]) -> list[str]:
    checks = registry.get("checks", {})
    research_modules = checks.get("research_private_modules", [])
    allowed_importers = checks.get("research_private_allowed_public_route_importers", [])
    failures: list[str] = []

    for module_name in checks.get("public_route_modules", []):
        mapped = module_to_path(module_name)
        if mapped is None or not mapped.exists() or mapped.is_dir():
            failures.append(f"Public route module path missing for {module_name}")
            continue
        imports = imported_modules(mapped)
        for imported in imports:
            if any(import_matches(imported, private) for private in research_modules):
                if any(module_matches(module_name, pattern) for pattern in allowed_importers):
                    continue
                failures.append(f"{module_name} imports research/private module {imported}")
    return failures


def check_runtime_fixture_dependencies(registry: dict[str, Any]) -> list[str]:
    checks = registry.get("checks", {})
    fragments = checks.get("forbidden_runtime_path_fragments", [])
    failures: list[str] = []

    for pattern in checks.get("runtime_scan_globs", []):
        for path in files_for_glob(pattern):
            text = path.read_text(encoding="utf-8")
            normalized = text.replace("\\", "/")
            for fragment in fragments:
                normalized_fragment = fragment.replace("\\", "/")
                if fragment in text or normalized_fragment in normalized:
                    failures.append(
                        f"{path.relative_to(PROJECT_ROOT)} references forbidden runtime path {fragment}"
                    )
    return sorted(set(failures))


def check_sdk_paths(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    sdk_area = next((area for area in registry.get("areas", []) if area.get("id") == "sdk_clients"), None)
    if sdk_area is None:
        return ["Missing sdk_clients area."]
    for rel_path in sdk_area.get("canonical_paths", []):
        if not (PROJECT_ROOT / rel_path).exists():
            failures.append(f"sdk_clients: missing canonical SDK path {rel_path}")
    return failures


def check_forbidden_imports(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    rules = registry.get("checks", {}).get("forbidden_imports", [])
    if not rules:
        return failures

    for path in runtime_python_files():
        importer = module_name_for_path(path)
        imports = imported_modules(path)
        for rule in rules:
            if not module_matches(importer, rule["importer_glob"]):
                continue
            if any(import_matches(imported, rule["module"]) for imported in imports):
                failures.append(
                    f"{importer} imports forbidden {rule['module']}: {rule.get('reason', '')}"
                )
    return failures


def run_checks() -> list[str]:
    registry = load_registry()
    failures: list[str] = []
    checks = [
        check_registry_structure,
        check_canonical_paths,
        check_test_references,
        check_deprecated_imports,
        check_public_route_research_imports,
        check_runtime_fixture_dependencies,
        check_sdk_paths,
        check_forbidden_imports,
    ]
    for check in checks:
        failures.extend(check(registry))
    return failures


def main() -> int:
    failures = run_checks()
    if failures:
        for failure in failures:
            print(f"[canonical-runtime] {failure}")
        return 1
    print("Canonical runtime registry check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
