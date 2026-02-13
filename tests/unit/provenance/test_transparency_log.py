from __future__ import annotations

from pathlib import Path

from app.provenance import transparency


def test_transparency_log_append_and_verify(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(transparency, "TRANSPARENCY_DIR", tmp_path)
    monkeypatch.setattr(transparency, "TRANSPARENCY_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(transparency, "ANCHOR_LOG", tmp_path / "anchors.jsonl")

    entry1 = transparency.append_entry("manual_event", {"k": "v"})
    entry2 = transparency.append_snapshot_event("snap_x", "dhash", "rhash")

    rows = transparency.load_log_entries()
    assert len(rows) == 2
    assert rows[0]["entry_id"] == entry1.entry_id
    assert rows[1]["entry_id"] == entry2.entry_id

    audit = transparency.verify_log_integrity()
    assert audit["valid"] is True
    assert audit["total_entries"] == 2


def test_transparency_replay_and_anchor(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(transparency, "TRANSPARENCY_DIR", tmp_path)
    monkeypatch.setattr(transparency, "TRANSPARENCY_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(transparency, "ANCHOR_LOG", tmp_path / "anchors.jsonl")

    transparency.append_snapshot_event("snap_1", "d1", "r1")
    state = transparency.replay_state()
    assert state["latest_snapshot"]["snapshot_id"] == "snap_1"

    payload = transparency.prepare_anchor_payload("note")
    assert payload["head_hash"]
    saved = transparency.record_anchor("0xabc", "testnet", payload)
    assert saved["tx_ref"] == "0xabc"

    anchors = transparency.list_anchors()
    assert len(anchors) == 1
