"""Validation suite for calendar plugins."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json

from .registry import get_plugin_registry


@dataclass
class ValidationCase:
    plugin: str
    gregorian: str
    expected: dict
    source_class: str | None = None
    source_ref: str | None = None


class PluginValidationSuite:
    """Run per-plugin corpus checks against conversion outputs."""

    def __init__(self) -> None:
        self.registry = get_plugin_registry()

    def load_cases(self, path: Path) -> list[ValidationCase]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("cases", [])
        cases: list[ValidationCase] = []
        for row in rows:
            cases.append(
                ValidationCase(
                    plugin=row["plugin"],
                    gregorian=row["gregorian"],
                    expected=row["expected"],
                    source_class=row.get("source_class"),
                    source_ref=row.get("source_ref"),
                )
            )
        return cases

    def run(self, cases: list[ValidationCase]) -> dict:
        results = []
        passed = 0

        for case in cases:
            plugin = self.registry.get(case.plugin)
            y, m, d = [int(v) for v in case.gregorian.split("-")]
            out = plugin.convert_from_gregorian(date(y, m, d))
            actual = {
                "year": out.year,
                "month": out.month,
                "day": out.day,
            }
            ok = all(actual.get(k) == v for k, v in case.expected.items())
            results.append({
                "plugin": case.plugin,
                "gregorian": case.gregorian,
                "expected": case.expected,
                "actual": actual,
                "source_class": case.source_class,
                "source_ref": case.source_ref,
                "pass": ok,
            })
            if ok:
                passed += 1

        total = len(results)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100.0) if total else 100.0,
            "results": results,
        }
