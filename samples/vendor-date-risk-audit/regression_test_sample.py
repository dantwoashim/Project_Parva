"""Runnable regression checks accompanying the demonstration vendor audit."""

from datetime import date

import pytest
from app.calendar.bikram_sambat import bs_to_gregorian, gregorian_to_bs
from app.calendar.fiscal import fiscal_period_for_bs_date
from app.calendar.provenance import get_bs_year_provenance

from scripts.vendor_audit.run_vendor_date_risk_audit import AuditRow, audit_rows


def test_ashadh_shrawan_boundary_is_contiguous() -> None:
    assert bs_to_gregorian(2082, 3, 32) == date(2025, 7, 16)
    assert bs_to_gregorian(2082, 4, 1) == date(2025, 7, 17)


def test_attendance_sample_uses_the_correct_civil_day() -> None:
    assert bs_to_gregorian(2082, 4, 2) == date(2025, 7, 18)


def test_invalid_month_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid BS date"):
        bs_to_gregorian(2082, 13, 1)


def test_boundary_dates_round_trip() -> None:
    for expected in ((2082, 3, 32), (2082, 4, 1), (2082, 4, 2)):
        assert gregorian_to_bs(bs_to_gregorian(*expected)) == expected


def test_future_static_row_is_not_labelled_official() -> None:
    assert get_bs_year_provenance(2090).confidence != "official"


def test_shrawan_starts_the_nepal_fiscal_year() -> None:
    period = fiscal_period_for_bs_date(2082, 4, 1)

    assert period.fiscal_month == 1
    assert period.fiscal_year_label == "2082/83"


def test_unknown_future_policy_stays_review_required() -> None:
    report = audit_rows(
        [
            AuditRow(
                row_number=2,
                bs_date="2090-01-01",
                workflow_type="loan_repayment",
                expected_behavior="review_required",
                actual_ad_date=None,
                holiday_assumption="unknown_future_holiday_policy",
                fiscal_assumption="nepal_fiscal_year",
            )
        ]
    )

    assert report["source_conflicts"]
    assert report["review_required_cases"]
