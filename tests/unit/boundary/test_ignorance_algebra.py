from __future__ import annotations

from app.boundary.ignorance import IgnoranceKind, IgnoranceState, compose_ignorance


def test_ignorance_states_are_distinct_artifacts() -> None:
    unsupported = IgnoranceState(IgnoranceKind.UNSUPPORTED, "outside_supported_source_universe")
    deferred = IgnoranceState(IgnoranceKind.AUTHORITY_DEFERRED, "official_source_missing")
    assert unsupported.as_dict()["kind"] != deferred.as_dict()["kind"]
    assert deferred.review_required is True


def test_required_phase_03_ignorance_states_exist() -> None:
    required = {
        "untouched",
        "under_specified",
        "interpretation_ambiguous",
        "source_unconsulted",
        "source_silent",
        "source_exhausted",
        "source_conflict",
        "authority_deferred",
        "temporally_precluded",
        "resolved",
    }
    assert required.issubset({kind.value for kind in IgnoranceKind})


def test_ignorance_composition_keeps_strongest_boundary() -> None:
    state = compose_ignorance(
        IgnoranceState(IgnoranceKind.SOURCE_SILENT, "source did not speak"),
        IgnoranceState(IgnoranceKind.AUTHORITY_DEFERRED, "authority not available"),
    )
    assert state.kind == IgnoranceKind.AUTHORITY_DEFERRED
    assert state.review_required is True
