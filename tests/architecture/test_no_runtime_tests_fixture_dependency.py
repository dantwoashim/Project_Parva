from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_canonical_runtime.py"

spec = importlib.util.spec_from_file_location("check_canonical_runtime", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)


def test_runtime_public_code_does_not_read_tests_fixtures() -> None:
    registry = canonical.load_registry()
    failures = canonical.check_runtime_fixture_dependencies(registry)

    assert not failures, "\n".join(failures)


def test_public_validation_artifact_inputs_are_in_data_validation_public() -> None:
    expected_paths = [
        "data/validation/public/calendar/tithi_boundaries_30.json",
        "data/validation/public/calendar/sankranti_24.json",
        "data/validation/public/calendar/adhik_maas_reference.json",
        "data/validation/public/plugins/plugin_validation_cases.json",
        "data/validation/public/plugins/plugin_validation_stage1_cases.json",
        "data/validation/public/plugins/plugin_validation_stage2_cases.json",
    ]

    missing = [path for path in expected_paths if not (PROJECT_ROOT / path).is_file()]
    assert not missing, "\n".join(missing)
