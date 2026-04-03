from __future__ import annotations

from app.explainability.store import create_reason_trace, get_reason_trace


def test_reason_trace_id_is_deterministic_for_same_payload():
    kwargs = dict(
        trace_type="festival_date_explain",
        subject={"festival_id": "dashain"},
        inputs={"year": 2026},
        outputs={"start_date": "2026-10-10"},
        steps=[{"step_type": "load_rule", "input": {}, "output": {}}],
        provenance={"snapshot_id": "snap_x"},
    )

    trace1 = create_reason_trace(**kwargs)
    trace2 = create_reason_trace(**kwargs)
    assert trace1["trace_id"] == trace2["trace_id"]


def test_private_reason_trace_is_redacted_and_not_publicly_readable():
    trace = create_reason_trace(
        trace_type="kundali",
        subject={"datetime": "2026-02-15T06:00:00+05:45"},
        inputs={"datetime": "2026-02-15T06:00:00+05:45", "lat": 27.7, "lon": 85.3},
        outputs={"lagna": "Aries"},
        steps=[{"step_type": "kundali"}],
        provenance={"snapshot_id": "snap_x"},
    )

    assert trace["visibility"] == "private"
    assert trace["redacted"] is True
    assert trace["inputs"]["datetime"] == "[redacted]"
    assert get_reason_trace(trace["trace_id"]) is None
    assert get_reason_trace(trace["trace_id"], include_private=True) is not None
