"""Loan impact tests."""

from app.future_bs.day_count_conventions import SUPPORTED_DAY_COUNT_METHODS, interest_difference


def test_day_count_methods_are_registered():
    assert {"actual_365", "actual_360", "actual_actual", "30_360", "monthly_flat", "product_specific"} <= SUPPORTED_DAY_COUNT_METHODS


def test_interest_difference_supports_actual_360():
    delta = interest_difference(
        principal=1_000_000,
        annual_rate=12,
        day_difference=1,
        day_count_method="actual_360",
    )

    assert round(delta, 2) == 333.33
