from __future__ import annotations

from datetime import date


def test_rule_service_upcoming_merges_partial_precomputed_with_computed_years(monkeypatch):
    import app.rules.service as service_module

    cached_row = {
        "festival_id": "cached-festival",
        "start_date": date(2028, 12, 30),
        "end_date": date(2028, 12, 30),
        "year": 2028,
        "method": "precomputed",
        "lunar_month": None,
        "is_adhik_year": False,
    }

    monkeypatch.setattr(
        service_module,
        "load_precomputed_festivals_between_report",
        lambda start, end: {
            "rows": [cached_row],
            "loaded_years": [2028],
            "missing_years": [2029],
            "partial_hit": True,
            "full_hit": False,
        },
    )
    monkeypatch.setattr(service_module, "list_festivals_v2", lambda: ["cached-festival", "computed-festival"])

    def _calculate(festival_id: str, year: int):
        if festival_id == "computed-festival" and year == 2029:
            return service_module.FestivalDate(
                festival_id=festival_id,
                start_date=date(2029, 1, 2),
                end_date=date(2029, 1, 2),
                year=year,
                method="calculated",
                lunar_month=None,
                is_adhik_year=False,
            )
        return None

    monkeypatch.setattr(service_module, "calculate_festival_v2", _calculate)

    results = service_module.FestivalRuleService().upcoming(date(2028, 12, 25), days=15)

    assert [festival_id for festival_id, _ in results] == ["cached-festival", "computed-festival"]
    assert results[0][1].method == "precomputed"
    assert results[1][1].method == "calculated"
