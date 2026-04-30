"""Regression checks for calibrated near-future BS estimated mode."""

from __future__ import annotations

from datetime import date

from app.calendar.bikram_sambat import bs_to_gregorian, gregorian_to_bs


def test_first_calibrated_future_year_starts_on_expected_boundary():
    assert bs_to_gregorian(2096, 1, 1) == date(2039, 4, 16)
    assert gregorian_to_bs(date(2039, 4, 16)) == (2096, 1, 1)


def test_calibrated_future_cycle_keeps_known_midrange_sample_stable():
    assert gregorian_to_bs(date(2050, 2, 15)) == (2106, 11, 1)
    assert bs_to_gregorian(2106, 11, 1) == date(2050, 2, 15)


def test_calibrated_future_year_boundary_no_longer_rolls_early():
    assert gregorian_to_bs(date(2040, 4, 15)) == (2097, 1, 1)
