from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_canonical_runtime.py"

spec = importlib.util.spec_from_file_location("check_canonical_runtime", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)


def test_deprecated_modules_are_only_imported_by_allowed_compatibility_wrappers() -> None:
    registry = canonical.load_registry()
    failures = canonical.check_deprecated_imports(registry)

    assert not failures, "\n".join(failures)


def test_public_route_modules_do_not_import_forbidden_legacy_paths() -> None:
    registry = canonical.load_registry()
    failures = canonical.check_forbidden_imports(registry)

    assert not failures, "\n".join(failures)
