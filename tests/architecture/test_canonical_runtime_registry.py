from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_canonical_runtime.py"

spec = importlib.util.spec_from_file_location("check_canonical_runtime", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)


def test_canonical_runtime_registry_is_complete_and_resolvable() -> None:
    registry = canonical.load_registry()

    failures: list[str] = []
    failures.extend(canonical.check_registry_structure(registry))
    failures.extend(canonical.check_canonical_paths(registry))
    failures.extend(canonical.check_test_references(registry))
    failures.extend(canonical.check_sdk_paths(registry))

    assert not failures, "\n".join(failures)


def test_registry_covers_required_phase03_domain_concepts() -> None:
    registry = canonical.load_registry()
    area_ids = {area["id"] for area in registry["areas"]}

    assert set(registry["required_area_ids"]).issubset(area_ids)
    assert {
        "bs_ad_conversion",
        "tithi_panchanga",
        "festivals_observances",
        "source_confidence_taxonomy",
        "sdk_clients",
        "public_validation_artifacts",
    }.issubset(area_ids)
