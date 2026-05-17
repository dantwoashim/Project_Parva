from __future__ import annotations

from app.membranes.negative import negative_membrane
from app.membranes.unsat import unsat_membrane


def test_negative_and_unsat_are_structured_membranes() -> None:
    negative = negative_membrane("holiday_on_2082_01_02", "not_found_in_supported_sources", ["w1"])
    unsat = unsat_membrane({"count": 99}, ["not_enough_working_days"], ["reduce_count"])
    assert negative["membrane_kind"] == "negative"
    assert unsat["membrane_kind"] == "unsat"
    assert unsat["relaxations"] == ["reduce_count"]
