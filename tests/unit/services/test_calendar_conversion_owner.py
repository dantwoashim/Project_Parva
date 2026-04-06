from datetime import date

from app.services import calendar_conversion_service
from app.services import calendar_surface_service


def test_calendar_surface_conversion_builders_delegate_to_canonical_service():
    target_date = date(2026, 2, 15)

    assert calendar_surface_service.parse_iso_date("2026-02-15") == calendar_conversion_service.parse_iso_date(
        "2026-02-15"
    )
    assert calendar_surface_service.build_conversion_payload(target_date) == calendar_conversion_service.build_conversion_payload(
        target_date
    )
    assert calendar_surface_service.build_compare_conversion_payload(
        target_date
    ) == calendar_conversion_service.build_compare_conversion_payload(target_date)
    assert calendar_surface_service.build_dual_month_payload(2026, 2) == calendar_conversion_service.build_dual_month_payload(
        2026, 2
    )
