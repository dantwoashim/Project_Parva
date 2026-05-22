#!/usr/bin/env python3
"""Check that public verification does not depend on local-only artifacts."""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PUBLIC_FILES = (
    "reports/phase_07_future_bs_governance/module_classification.md",
    "reports/phase_08_performance_sre/latency_baseline.json",
    "reports/red_check_closure/README.md",
    "reports/next_roadmap_execution/README.md",
    "reports/next_roadmap_execution/verification_matrix.json",
    "reports/external_reviewer_packet/README.md",
    "reports/external_reviewer_packet/ci_status.md",
    "reports/external_reviewer_packet/release_readiness.md",
    "reports/release_readiness/README.md",
    "reports/release_readiness/release_checklist.md",
    "reports/release_readiness/public_claims_checklist.md",
    "reports/release_readiness/final_verification_matrix.json",
    "reports/distribution_readiness/README.md",
    "reports/distribution_readiness/baseline.md",
    "reports/distribution_readiness/duplicate_runtime_cleanup.md",
    "public-benchmark/benchmark.json",
    "public-benchmark/schema.json",
    "public-benchmark/validate_benchmark.py",
    "public-benchmark/runners/run_against_static_baseline.py",
    "public-benchmark/runners/run_against_parva.py",
    "public-benchmark/runners/compare_results.py",
    "public-benchmark/results/latest-parva.json",
    "public-benchmark/results/latest-static-baseline.json",
    "public-benchmark/results/comparison.json",
    "public-benchmark/results/benchmark.svg",
    "public-benchmark/results/benchmark-summary.json",
    "scripts/release/check_import_cycles.py",
    "scripts/release/check_mypy_scope.py",
    "scripts/release/check_python_module_size.py",
    "scripts/release/check_ts_module_size.py",
    "scripts/resolve_npm_command.py",
)

OPTIONAL_PRIVATE_INPUTS = (
    "data/ephemeris/jpl/de440.bsp",
    "data/ephemeris/jpl/de441_part-1.bsp",
    "data/ephemeris/jpl/de441_part-2.bsp",
    "data/source_archive",
    "data/future_bs/private",
)

SCANNED_SOURCE_SUFFIXES = frozenset({".css", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".py"})
JS_EXTENSION_CANDIDATES = (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".json")
INDEX_CANDIDATES = tuple(f"index{suffix}" for suffix in JS_EXTENSION_CANDIDATES)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\()?['\"]([^'\"]+)['\"]", re.IGNORECASE)
JS_IMPORT_RE = re.compile(
    r"(?:import|export)\s+(?:[^'\"\n]*?\s+from\s+)?['\"](\.{1,2}/[^'\"]+)['\"]"
)
JS_FROM_RE = re.compile(r"\bfrom\s+['\"](\.{1,2}/[^'\"]+)['\"]")
JS_DYNAMIC_IMPORT_RE = re.compile(r"\bimport\s*\(\s*['\"](\.{1,2}/[^'\"]+)['\"]\s*\)")
ALLOW_GENERATED_IMPORT_TARGETS = frozenset(
    {
        "packages/parva-js/dist/index.js",
        "packages/parva-local-kernel/dist/index.js",
    }
)


def _git_ls_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return set(result.stdout.splitlines())


def _is_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode == 0


def _to_repo_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _candidate_paths(base: Path, *, include_js_variants: bool) -> list[Path]:
    candidates: list[Path] = []
    if base.suffix:
        candidates.append(base)
        if include_js_variants and base.suffix in JS_EXTENSION_CANDIDATES:
            stem = base.with_suffix("")
            for suffix in JS_EXTENSION_CANDIDATES:
                alternate = stem.with_suffix(suffix)
                if alternate not in candidates:
                    candidates.append(alternate)
    else:
        if include_js_variants:
            candidates.extend(base.with_suffix(suffix) for suffix in JS_EXTENSION_CANDIDATES)
            candidates.extend(base / index for index in INDEX_CANDIDATES)
        else:
            candidates.append(base)
    if base.is_dir():
        candidates.extend(base / index for index in INDEX_CANDIDATES)
    return candidates


def _resolve_relative_import(importer: Path, specifier: str, *, include_js_variants: bool) -> list[Path]:
    if not specifier.startswith(("./", "../")):
        return []
    return _candidate_paths((importer.parent / specifier).resolve(), include_js_variants=include_js_variants)


def _module_to_python_candidates(module_name: str) -> list[Path]:
    if not module_name.startswith("app."):
        return []
    module_path = PROJECT_ROOT / "backend" / Path(*module_name.split("."))
    return [module_path.with_suffix(".py"), module_path / "__init__.py"]


def _python_module_name(relative: str) -> str | None:
    path = Path(relative)
    parts = path.with_suffix("").parts
    if len(parts) < 3 or parts[0] != "backend" or parts[1] != "app":
        return None
    module_parts = ("app", *parts[2:])
    if module_parts[-1] == "__init__":
        module_parts = module_parts[:-1]
    return ".".join(module_parts)


def _resolve_python_relative_import(importer_relative: str, node: ast.ImportFrom) -> list[Path]:
    importer_module = _python_module_name(importer_relative)
    if not importer_module or node.level <= 0:
        return []
    importer_path = Path(importer_relative)
    package_parts = list(importer_module.split("."))
    if importer_path.name != "__init__.py":
        package_parts = package_parts[:-1]
    if node.level > len(package_parts):
        return []
    base_parts = package_parts[: len(package_parts) - node.level + 1]
    if node.module:
        base_parts.extend(node.module.split("."))
    candidates: list[Path] = []
    if base_parts and base_parts[0] == "app":
        candidates.extend(_module_to_python_candidates(".".join(base_parts)))
    for alias in node.names:
        if alias.name == "*":
            continue
        alias_parts = [*base_parts, alias.name]
        if alias_parts and alias_parts[0] == "app":
            candidates.extend(_module_to_python_candidates(".".join(alias_parts)))
    return candidates


def _existing_or_primary(candidates: Iterable[Path]) -> Path | None:
    candidates = list(candidates)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else None


def _check_target_tracked(
    *,
    importer: str,
    target: Path,
    tracked: set[str],
    issues: list[str],
    label: str,
) -> None:
    try:
        repo_path = _to_repo_path(target)
    except ValueError:
        return
    if repo_path in ALLOW_GENERATED_IMPORT_TARGETS:
        return
    if target.exists() and repo_path not in tracked:
        issues.append(f"{importer}: {label} target {repo_path} exists locally but is not tracked")
    elif not target.exists() and repo_path not in ALLOW_GENERATED_IMPORT_TARGETS:
        issues.append(f"{importer}: {label} target {repo_path} is missing from the working tree")


def _verify_source_imports(tracked: set[str]) -> list[str]:
    issues: list[str] = []
    for relative in sorted(tracked):
        path = PROJECT_ROOT / relative
        if path.suffix not in SCANNED_SOURCE_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            issues.append(f"{relative}: source file is not valid UTF-8")
            continue

        if path.suffix == ".css":
            for specifier in CSS_IMPORT_RE.findall(text):
                if specifier.startswith(("http://", "https://")):
                    continue
                target = _existing_or_primary(
                    _resolve_relative_import(path, specifier, include_js_variants=False)
                )
                if target:
                    _check_target_tracked(
                        importer=relative,
                        target=target,
                        tracked=tracked,
                        issues=issues,
                        label=f"CSS import {specifier!r}",
                    )
            continue

        if path.suffix in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}:
            specifiers = {
                *JS_IMPORT_RE.findall(text),
                *JS_FROM_RE.findall(text),
                *JS_DYNAMIC_IMPORT_RE.findall(text),
            }
            for specifier in sorted(specifiers):
                target = _existing_or_primary(
                    _resolve_relative_import(path, specifier, include_js_variants=True)
                )
                if target:
                    _check_target_tracked(
                        importer=relative,
                        target=target,
                        tracked=tracked,
                        issues=issues,
                        label=f"JS import {specifier!r}",
                    )
            continue

        if path.suffix == ".py":
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError as exc:
                issues.append(f"{relative}: Python parse failed: {exc.msg}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target = _existing_or_primary(_module_to_python_candidates(alias.name))
                        if target:
                            _check_target_tracked(
                                importer=relative,
                                target=target,
                                tracked=tracked,
                                issues=issues,
                                label=f"Python import {alias.name!r}",
                            )
                elif isinstance(node, ast.ImportFrom):
                    candidates = (
                        _resolve_python_relative_import(relative, node)
                        if node.level
                        else _module_to_python_candidates(node.module or "")
                    )
                    target = _existing_or_primary(candidates)
                    if target:
                        label = f"Python import {'.' * node.level}{node.module or ''!r}"
                        _check_target_tracked(
                            importer=relative,
                            target=target,
                            tracked=tracked,
                            issues=issues,
                            label=label,
                        )
    return issues


def verify_clean_clone_assumptions() -> list[str]:
    tracked = _git_ls_files()
    issues: list[str] = []

    for path in REQUIRED_PUBLIC_FILES:
        full_path = PROJECT_ROOT / path
        if not full_path.exists():
            issues.append(f"{path}: required public file is missing")
            continue
        if full_path.is_file() and full_path.stat().st_size == 0:
            issues.append(f"{path}: required public file is empty")
        if path not in tracked:
            issues.append(f"{path}: required public file is not tracked")
        if _is_ignored(path) and path not in tracked:
            issues.append(f"{path}: required public file is ignored and untracked")

    for path in OPTIONAL_PRIVATE_INPUTS:
        if path in tracked:
            issues.append(f"{path}: private/large optional input must not be tracked")

    config_text = (PROJECT_ROOT / "config" / "ephemeris-kernels.yaml").read_text(encoding="utf-8")
    if '"public_runtime_required": true' in config_text or "public_runtime_required: true" in config_text:
        issues.append("config/ephemeris-kernels.yaml: JPL kernels must not be public-runtime required")
    local_drive_tokens = ("D:" + chr(92), "C:" + chr(92))
    if any(token in config_text for token in local_drive_tokens):
        issues.append("config/ephemeris-kernels.yaml: local absolute path leaked")

    issues.extend(_verify_source_imports(tracked))

    return issues


def main() -> int:
    issues = verify_clean_clone_assumptions()
    if issues:
        for issue in issues:
            print(f"[clean-clone] {issue}")
        return 1
    print("Clean-clone public verification assumptions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
