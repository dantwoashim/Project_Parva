from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_canonical_runtime.py"

spec = importlib.util.spec_from_file_location("check_canonical_runtime", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)


def test_tithi_import_resolves_to_canonical_package_not_shadow_stub() -> None:
    module = importlib.import_module("app.calendar.tithi")
    assert module.__file__ is not None
    normalized = module.__file__.replace("\\", "/")
    assert normalized.endswith("backend/app/calendar/tithi/__init__.py")


def test_legacy_festival_calculators_remain_compatibility_only() -> None:
    registry = canonical.load_registry()
    festival_area = next(area for area in registry["areas"] if area["id"] == "festivals_observances")

    deprecated = {row["module"]: row for row in festival_area["deprecated_modules"]}
    assert deprecated["app.calendar.calculator"]["replacement"] == "app.rules.service"
    assert deprecated["app.calendar.calculator_v2"]["replacement"] == "app.rules.service"
    assert "app.calendar.calculator_v2" not in festival_area["canonical_modules"]


def test_public_runtime_checks_catch_deprecated_primary_imports() -> None:
    registry = canonical.load_registry()
    failures: list[str] = []
    failures.extend(canonical.check_deprecated_imports(registry))
    failures.extend(canonical.check_forbidden_imports(registry))

    assert not failures, "\n".join(failures)
