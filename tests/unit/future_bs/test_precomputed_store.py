"""Precomputed store tests."""

import pytest
from app.research.future_bs.precomputed_store import get_precomputed_year, precomputed_store_status

pytestmark = pytest.mark.research_artifact


def test_precomputed_store_loads_future_year_instantly():
    status = precomputed_store_status()
    prediction = get_precomputed_year(2112)

    assert status["available"] is True
    assert prediction is not None
    assert prediction["served_from"] == "precomputed_prediction_store"
    assert prediction["publication_status"] == "computed_prediction_not_official"
