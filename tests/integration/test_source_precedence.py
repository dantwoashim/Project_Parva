"""Source precedence tests (Week 8)."""

from app.sources.loader import get_source_loader, DEFAULT_PRIORITY
from app.calendar.overrides import get_festival_override_info


def test_source_priority_order_matches_policy_doc():
    loader = get_source_loader()
    assert loader.get_source_priority() == DEFAULT_PRIORITY
    assert loader.get_source_priority()[0] == "ground_truth_overrides"


def test_override_source_has_precedence_data():
    # dashain has official override entries in existing dataset
    info = get_festival_override_info("dashain", 2026)
    assert info is not None
    # Source metadata may be None in legacy rows; when present, it should be non-empty.
    if info.get("source") is not None:
        assert isinstance(info["source"], str)
        assert info["source"]
