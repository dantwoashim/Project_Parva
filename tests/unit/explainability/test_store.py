from __future__ import annotations

from app.explainability.store import create_reason_trace


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
