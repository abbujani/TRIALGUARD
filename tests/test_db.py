"""tests/test_db.py — Phase 8: SQLite layer tests."""
import os, tempfile, pytest

# Use a temp DB for every test
@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    import importlib, db
    importlib.reload(db)
    db.init_db()
    return db

def test_init_db_creates_tables(tmp_db):
    import db
    stats = db.get_stats()
    assert stats == {"participants": 0, "checkins": 0, "outcomes": 0, "agent_runs": 0}

def test_upsert_and_get_participant(tmp_db):
    import db
    db.upsert_participant("P402", "Participant 402", "TRIAL-001", "Active")
    p = db.get_participant("P402")
    assert p is not None
    assert p["id"] == "P402"
    assert p["display_name"] == "Participant 402"

def test_upsert_participant_updates(tmp_db):
    import db
    db.upsert_participant("P402", "Old Name")
    db.upsert_participant("P402", "New Name")
    assert db.get_participant("P402")["display_name"] == "New Name"

def test_list_participants(tmp_db):
    import db
    db.upsert_participant("P001", "P1"); db.upsert_participant("P002", "P2")
    assert len(db.list_participants()) == 2

def test_get_participant_missing_returns_none(tmp_db):
    import db
    assert db.get_participant("MISSING") is None

def test_save_and_get_checkin(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_checkin("ci-001", "P402", "2026-03-10T10:00:00Z", "Participant reports nausea.")
    ci = db.get_checkin("ci-001")
    assert ci["participant_id"] == "P402"
    assert "nausea" in ci["raw_text"]

def test_list_checkins(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_checkin("ci-001", "P402", "2026-03-10T10:00:00Z", "Text 1")
    db.save_checkin("ci-002", "P402", "2026-04-10T10:00:00Z", "Text 2")
    assert len(db.list_checkins("P402")) == 2

def test_save_and_get_outcome(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_outcome("out-001", "P402", "Symptoms improved.", description="Follow-up")
    o = db.get_outcome("out-001")
    assert o["outcome_text"] == "Symptoms improved."

def test_save_and_get_agent_run(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_checkin("ci-001", "P402", "2026-03-10T10:00:00Z", "text")
    db.save_agent_run(
        run_id="run-001", checkin_id="ci-001", mode="hindsight",
        final_output={"current_issue": "nausea"}, hindsight_query="previous nausea",
        retrieved_memories=[{"text": "Month 1 nausea"}]
    )
    run = db.get_agent_run("run-001")
    assert run["mode"] == "hindsight"
    assert run["final_output"]["current_issue"] == "nausea"
    assert len(run["retrieved_memories"]) == 1

def test_agent_run_json_roundtrip(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_checkin("ci-001", "P402", "2026-03-10T10:00:00Z", "text")
    complex_output = {"a": [1, 2], "b": {"nested": True}}
    db.save_agent_run("run-002", "ci-001", "baseline", final_output=complex_output)
    run = db.get_agent_run("run-002")
    assert run["final_output"] == complex_output

def test_recent_agent_runs(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_checkin("ci-001", "P402", "2026-03-10T10:00:00Z", "text")
    db.save_agent_run("run-001", "ci-001", "hindsight", final_output={})
    db.save_agent_run("run-002", "ci-001", "baseline",  final_output={})
    runs = db.recent_agent_runs(limit=10)
    assert len(runs) == 2

def test_get_stats(tmp_db):
    import db
    db.upsert_participant("P402", "P402")
    db.save_checkin("ci-001", "P402", "2026-03-10T10:00:00Z", "text")
    db.save_outcome("out-001", "P402", "Improved.")
    db.save_agent_run("run-001", "ci-001", "hindsight", final_output={})
    stats = db.get_stats()
    assert stats["participants"] == 1
    assert stats["checkins"]     == 1
    assert stats["outcomes"]     == 1
    assert stats["agent_runs"]   == 1
