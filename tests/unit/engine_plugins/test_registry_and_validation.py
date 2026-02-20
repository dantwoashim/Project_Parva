from __future__ import annotations

from datetime import date
from pathlib import Path

from app.engine.plugins import get_plugin_registry
from app.engine.plugins.validation import PluginValidationSuite


def test_registry_lists_expected_plugins():
    registry = get_plugin_registry()
    ids = registry.list_ids()
    assert "bs" in ids
    assert "ns" in ids
    assert "tibetan" in ids
    assert "islamic" in ids
    assert "hebrew" in ids
    assert "chinese" in ids
    assert "julian" in ids


def test_bs_plugin_conversion_basic():
    registry = get_plugin_registry()
    out = registry.convert("bs", date(2026, 2, 15))
    assert out.year == 2082
    assert out.month == 11
    assert out.day == 3


def test_validation_suite_with_fixture_passes():
    suite = PluginValidationSuite()
    cases = suite.load_cases(Path("tests/fixtures/plugins/plugin_validation_cases.json"))
    report = suite.run(cases)
    assert report["failed"] == 0


def test_stage1_validation_fixture_covers_first_four_plugins():
    suite = PluginValidationSuite()
    cases = suite.load_cases(Path("tests/fixtures/plugins/plugin_validation_stage1_cases.json"))
    report = suite.run(cases)

    assert report["failed"] == 0

    plugins = {row["plugin"] for row in report["results"]}
    assert {"bs", "ns", "tibetan", "islamic"}.issubset(plugins)

    for plugin_id in ("bs", "ns", "tibetan", "islamic"):
        plugin_rows = [row for row in report["results"] if row["plugin"] == plugin_id]
        assert len(plugin_rows) >= 6
        assert all(row["source_class"] is not None for row in plugin_rows)
