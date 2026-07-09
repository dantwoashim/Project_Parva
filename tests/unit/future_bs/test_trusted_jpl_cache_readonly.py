import pytest
from app.research.future_bs.solar_ingress_cache import (
    cached_events_for_gregorian_year,
    solar_ingress_cache_status,
)

pytestmark = pytest.mark.research_artifact


def test_trusted_jpl_cache_can_serve_readonly_when_active_label_is_swiss():
    status = solar_ingress_cache_status()
    assert status["available"] is True
    if status["ephemeris"] == "jpl_de440":
        events = cached_events_for_gregorian_year(2027, ephemeris_label="swiss_moshier")
        assert events
        assert status["served_from_trusted_precomputed_jpl_cache"] is True
