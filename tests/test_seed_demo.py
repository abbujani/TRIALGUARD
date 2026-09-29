"""
tests/test_seed_demo.py

Phase 6 tests — seed_demo.py and data/demo_data.json.

No live Hindsight server required. Covers:
  1.  demo_data.json exists and parses
  2.  Exactly 10 participants present
  3.  All participant IDs match blueprint Section 50
  4.  P402 is present (hero participant)
  5.  P402 has exactly 8 check-ins covering the Month 1–6 hero timeline
  6.  P402 hero timeline contains required event_types in correct order
  7.  Every check-in has required fields: checkin_id, occurred_at, event_type, text
  8.  Every check-in text is non-empty and contains participant ID
  9.  document_id format is "checkin:<pid>:<checkin_id>"
 10.  Tags always include participant:<id> and trial:<trial_id>
 11.  Metadata contains all required keys
 12.  load_demo_data() returns dict with trial and participants keys
 13.  seed() dry-run completes without errors and returns correct summary
 14.  seed() unknown participant calls sys.exit(1)
 15.  seed() live path calls ensure_bank_exists once then retain per check-in
 16.  seed() --participant P402 only seeds P402 check-ins
 17.  retain_checkin() dry-run prints document_id in output
 18.  retain_checkin() live path passes correct args to Hindsight client
 19.  retain_checkin() uses ISO timestamp for Hindsight temporal retrieval
 20.  All 10 participants have at least 3 check-ins
"""

import importlib
import json
import os
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

# ── helpers ───────────────────────────────────────────────────────────────────

def load_data():
    return json.loads((DATA_DIR / "demo_data.json").read_text(encoding="utf-8"))


def get_participant(pid: str) -> dict:
    data = load_data()
    return next(p for p in data["participants"] if p["id"] == pid)


# ── 1. File exists and parses ─────────────────────────────────────────────────

def test_demo_data_file_exists():
    assert (DATA_DIR / "demo_data.json").exists()


def test_demo_data_parses():
    data = load_data()
    assert isinstance(data, dict)
    assert "participants" in data
    assert "trial" in data


# ── 2. Exactly 10 participants ────────────────────────────────────────────────

def test_exactly_ten_participants():
    data = load_data()
    assert len(data["participants"]) == 10


# ── 3. All IDs match blueprint Section 50 ────────────────────────────────────

def test_participant_ids_match_blueprint():
    expected = {"P402", "P117", "P209", "P314", "P501",
                "P607", "P722", "P811", "P905", "P990"}
    data = load_data()
    actual = {p["id"] for p in data["participants"]}
    assert actual == expected


# ── 4. P402 present ───────────────────────────────────────────────────────────

def test_p402_present():
    data = load_data()
    ids = [p["id"] for p in data["participants"]]
    assert "P402" in ids


# ── 5. P402 has 8 check-ins ───────────────────────────────────────────────────

def test_p402_has_eight_checkins():
    p402 = get_participant("P402")
    assert len(p402["checkins"]) == 8


# ── 6. P402 hero timeline event_types in order ────────────────────────────────

def test_p402_hero_timeline_event_types():
    p402    = get_participant("P402")
    types   = [c["event_type"] for c in p402["checkins"]]
    # Must contain dosage_change, symptom_report, outcome, and concern
    assert "dosage_change"  in types
    assert "symptom_report" in types
    assert "outcome"        in types
    assert "concern"        in types
    # concern (withdrawal) must be the last check-in
    assert types[-1] == "concern"


# ── 7. Every check-in has required fields ─────────────────────────────────────

def test_all_checkins_have_required_fields():
    data = load_data()
    required = {"checkin_id", "occurred_at", "event_type", "text"}
    for p in data["participants"]:
        for ci in p["checkins"]:
            missing = required - ci.keys()
            assert not missing, f"{p['id']} checkin {ci.get('checkin_id')} missing {missing}"


# ── 8. Check-in text is non-empty and contains participant ID ─────────────────

def test_checkin_text_non_empty_and_contains_pid():
    data = load_data()
    for p in data["participants"]:
        for ci in p["checkins"]:
            assert ci["text"].strip(), f"{p['id']} checkin {ci['checkin_id']} has empty text"
            assert p["id"] in ci["text"], (
                f"Participant ID {p['id']} not found in checkin {ci['checkin_id']} text"
            )


# ── 9. document_id format ─────────────────────────────────────────────────────

def test_document_id_format():
    import seed_demo
    # The format is built in retain_checkin; verify it using the known formula
    doc_id = f"checkin:P402:001"
    assert doc_id == "checkin:P402:001"
    # Also verify dry-run output contains the doc_id
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        seed_demo.retain_checkin(
            participant_id="P402",
            trial_id="TRIAL-001",
            checkin_id="001",
            occurred_at="2026-03-10T10:00:00Z",
            event_type="dosage_change",
            text="Participant P402. Trial: TRIAL-001. Date: 2026-03-10. Test.",
            dry_run=True,
        )
    assert "checkin:P402:001" in buf.getvalue()


# ── 10. Tags include participant and trial ────────────────────────────────────

def test_retain_checkin_tags_correct(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    import seed_demo

    mock_client  = MagicMock()
    mock_resp    = MagicMock()
    mock_resp.items_count  = 1
    mock_resp.operation_id = "op-001"
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        seed_demo.retain_checkin(
            participant_id = "P402",
            trial_id       = "TRIAL-001",
            checkin_id     = "001",
            occurred_at    = "2026-03-10T10:00:00Z",
            event_type     = "dosage_change",
            text           = "Participant P402. Trial: TRIAL-001. Test content.",
        )

    kw = mock_client.retain.call_args.kwargs
    assert "participant:P402"  in kw["tags"]
    assert "trial:TRIAL-001"   in kw["tags"]


# ── 11. Metadata contains required keys ──────────────────────────────────────

def test_retain_checkin_metadata_keys(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    import seed_demo

    mock_client  = MagicMock()
    mock_resp    = MagicMock()
    mock_resp.items_count  = 1
    mock_resp.operation_id = "op-002"
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        seed_demo.retain_checkin(
            participant_id = "P402",
            trial_id       = "TRIAL-001",
            checkin_id     = "002",
            occurred_at    = "2026-03-14T09:30:00Z",
            event_type     = "symptom_report",
            text           = "Participant P402. Trial: TRIAL-001. Test content.",
        )

    meta = mock_client.retain.call_args.kwargs["metadata"]
    for key in ("participant_id", "trial_id", "event_type", "checkin_id",
                "occurred_at", "source"):
        assert key in meta, f"metadata missing key: {key}"
    assert meta["source"] == "synthetic_demo"


# ── 12. load_demo_data returns expected structure ─────────────────────────────

def test_load_demo_data_structure():
    import seed_demo
    data = seed_demo.load_demo_data()
    assert "trial"        in data
    assert "participants" in data
    assert data["trial"]["id"] == "TRIAL-001"


# ── 13. dry-run completes and returns correct summary ─────────────────────────

def test_seed_dry_run_returns_summary(capsys):
    import seed_demo
    summary = seed_demo.seed(dry_run=True)
    assert summary["participants"] == 10
    assert summary["checkins"]     >  0
    assert summary["hero"]         == "P402"
    captured = capsys.readouterr()
    assert "dry-run" in captured.out.lower() or "dry-run" in captured.out


# ── 14. Unknown participant calls sys.exit(1) ─────────────────────────────────

def test_seed_unknown_participant_exits():
    import seed_demo
    with pytest.raises(SystemExit) as exc:
        seed_demo.seed(participant_id="P999")
    assert exc.value.code == 1


# ── 15. Live path: ensure_bank_exists once + retain per check-in ──────────────

def test_seed_live_calls_ensure_and_retain(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    import seed_demo

    mock_client  = MagicMock()
    mock_resp    = MagicMock()
    mock_resp.items_count  = 1
    mock_resp.operation_id = "op-live"
    mock_client.retain.return_value       = mock_resp
    mock_client.create_bank.return_value  = MagicMock()

    data        = seed_demo.load_demo_data()
    total_cis   = sum(len(p["checkins"]) for p in data["participants"])

    with patch("memory._get_client", return_value=mock_client):
        seed_demo.seed()

    # create_bank called once (ensure_bank_exists)
    assert mock_client.create_bank.call_count == 1
    # retain called once per check-in
    assert mock_client.retain.call_count == total_cis


# ── 16. --participant P402 seeds only P402 ────────────────────────────────────

def test_seed_single_participant_only_seeds_that_one(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    import seed_demo

    mock_client  = MagicMock()
    mock_resp    = MagicMock()
    mock_resp.items_count  = 1
    mock_resp.operation_id = "op-p402"
    mock_client.retain.return_value      = mock_resp
    mock_client.create_bank.return_value = MagicMock()

    p402_cis = len(get_participant("P402")["checkins"])

    with patch("memory._get_client", return_value=mock_client):
        summary = seed_demo.seed(participant_id="P402")

    assert summary["participants"] == 1
    assert summary["checkins"]     == p402_cis
    assert mock_client.retain.call_count == p402_cis


# ── 17. dry-run prints document_id ───────────────────────────────────────────

def test_retain_checkin_dry_run_prints_doc_id(capsys):
    import seed_demo
    seed_demo.retain_checkin(
        participant_id = "P402",
        trial_id       = "TRIAL-001",
        checkin_id     = "008",
        occurred_at    = "2026-09-02T09:45:00Z",
        event_type     = "concern",
        text           = "Participant P402. Trial: TRIAL-001. Nausea, withdrawal concern.",
        dry_run        = True,
    )
    captured = capsys.readouterr()
    assert "checkin:P402:008" in captured.out
    assert "concern"          in captured.out


# ── 18. Live retain_checkin passes correct document_id ───────────────────────

def test_retain_checkin_passes_correct_document_id(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    import seed_demo

    mock_client  = MagicMock()
    mock_resp    = MagicMock()
    mock_resp.items_count  = 1
    mock_resp.operation_id = "op-docid"
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        seed_demo.retain_checkin(
            participant_id = "P402",
            trial_id       = "TRIAL-001",
            checkin_id     = "005",
            occurred_at    = "2026-05-06T09:00:00Z",
            event_type     = "dosage_change",
            text           = "Participant P402. Trial: TRIAL-001. Second dosage increase.",
        )

    kw = mock_client.retain.call_args.kwargs
    assert kw["document_id"] == "checkin:P402:005"
    assert kw["context"]     == "clinical_trial_checkin"


# ── 19. ISO timestamp parsed for temporal retrieval ──────────────────────────

def test_retain_checkin_parses_timestamp(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    import seed_demo

    mock_client  = MagicMock()
    mock_resp    = MagicMock()
    mock_resp.items_count  = 1
    mock_resp.operation_id = "op-ts"
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        seed_demo.retain_checkin(
            participant_id = "P402",
            trial_id       = "TRIAL-001",
            checkin_id     = "001",
            occurred_at    = "2026-03-10T10:00:00Z",
            event_type     = "dosage_change",
            text           = "Participant P402. Trial: TRIAL-001. Dosage increase.",
        )

    kw = mock_client.retain.call_args.kwargs
    # timestamp must be a datetime object, not a raw string
    assert isinstance(kw["timestamp"], datetime)


# ── 20. All participants have >= 3 check-ins ──────────────────────────────────

def test_all_participants_have_at_least_three_checkins():
    data = load_data()
    for p in data["participants"]:
        assert len(p["checkins"]) >= 3, (
            f"{p['id']} has only {len(p['checkins'])} check-in(s), expected >= 3"
        )
