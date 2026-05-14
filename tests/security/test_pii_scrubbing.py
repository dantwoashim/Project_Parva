from __future__ import annotations

import json
from pathlib import Path

from app.security.pii import REDACTION, scrub_structured_trace
from app.storage.file_stores import FileTraceStore, FileTransparencyLogStore


def test_structured_trace_scrubber_redacts_known_pii_patterns():
    scrubbed = scrub_structured_trace(
        {
            "email": "person@example.com",
            "note": "Call +977 9801234567 about account AB-123456",
            "source_id": "published_calendar",
        }
    )

    assert scrubbed["email"] == REDACTION
    assert "person@example.com" not in json.dumps(scrubbed)
    assert "9801234567" not in json.dumps(scrubbed)
    assert scrubbed["source_id"] == "published_calendar"


def test_public_trace_store_scrubs_sensitive_inputs_and_outputs(tmp_path: Path):
    store = FileTraceStore(
        tmp_path,
        public_trace_types=frozenset({"calendar"}),
        private_ttl_hours=24,
    )

    trace = store.create(
        trace_type="calendar",
        subject={"email": "person@example.com"},
        inputs={"phone": "+977 9801234567", "bs_date": "2080-01-01"},
        outputs={"note": "citizenship 12-345-678901"},
        steps=[{"result": {"address": "Ward 4, Sample Tole"}}],
        visibility="public",
    )

    serialized = json.dumps(trace)
    assert "person@example.com" not in serialized
    assert "9801234567" not in serialized
    assert "12-345-678901" not in serialized
    assert "Sample Tole" not in serialized


def test_transparency_payloads_are_scrubbed_before_hash_chain_write(tmp_path: Path):
    store = FileTransparencyLogStore(
        transparency_dir=tmp_path,
        log_path=tmp_path / "log.jsonl",
        anchor_path=tmp_path / "anchors.jsonl",
    )

    row = store.append_entry("manual_event", {"email": "person@example.com", "note": "ok"})

    assert row["payload"]["email"] == REDACTION
    assert "person@example.com" not in (tmp_path / "log.jsonl").read_text(encoding="utf-8")
