"""Islamic observance plugin with tabular/announced modes."""

from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path
import json

from app.engine.plugins.islamic.plugin import IslamicCalendarPlugin
from app.rules.plugins.base import ObservanceDate, ObservanceRule


_RULES: dict[str, tuple[int, int]] = {
    "islamic-new-year": (1, 1),
    "eid-al-fitr": (10, 1),
    "eid-al-adha": (12, 10),
    "shab-e-barat": (8, 15),
}

OVERRIDE_PATH = Path(__file__).resolve().parents[5] / "data" / "islamic" / "announced_dates.json"


@lru_cache(maxsize=1)
def _load_overrides() -> dict:
    if not OVERRIDE_PATH.exists():
        return {}
    payload = json.loads(OVERRIDE_PATH.read_text(encoding="utf-8"))
    return payload.get("overrides", {})


class IslamicObservancePlugin:
    plugin_id = "islamic"

    def __init__(self) -> None:
        self.calendar = IslamicCalendarPlugin()

    def list_rules(self) -> list[ObservanceRule]:
        return [
            ObservanceRule(
                id=rid,
                name=rid.replace("-", " ").title(),
                calendar_family="islamic",
                method="tabular_or_announced",
                confidence="computed",
            )
            for rid in sorted(_RULES)
        ]

    def _candidate_dates(self, rule_id: str, year: int) -> list[date]:
        month, day = _RULES[rule_id]
        # Gregorian year roughly = Hijri + 579
        hijri_guess = year - 579
        candidates: list[date] = []
        for hy in (hijri_guess - 1, hijri_guess, hijri_guess + 1):
            try:
                g = self.calendar.convert_to_gregorian(hy, month, day)
                if g.year == year:
                    candidates.append(g)
            except Exception:
                continue
        return sorted(set(candidates))

    def calculate(self, rule_id: str, year: int, mode: str = "computed") -> ObservanceDate | None:
        if rule_id not in _RULES:
            return None

        if mode == "announced":
            override = _load_overrides().get(str(year), {}).get(rule_id)
            if override:
                y, m, d = [int(v) for v in override.split("-")]
                start = date(y, m, d)
                return ObservanceDate(
                    rule_id=rule_id,
                    start_date=start,
                    end_date=start,
                    confidence="official",
                    method="announced_override",
                )

        candidates = self._candidate_dates(rule_id, year)
        if not candidates:
            return None

        start = candidates[0]
        method = "tabular"
        confidence = "computed"
        if mode == "astronomical":
            # Placeholder mode name to keep API explicit until visibility logic is added.
            method = "astronomical_proxy"
            confidence = "approximate"

        return ObservanceDate(
            rule_id=rule_id,
            start_date=start,
            end_date=start,
            confidence=confidence,
            method=method,
        )
