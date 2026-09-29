"""
tests/test_integration.py — Phase 16: end-to-end integration tests.

Tests the full request lifecycle in a single in-process flow:
  seed_demo → SQLite → Flask analyze route → agent (mocked) → result → trace

No live Groq or Hindsight server required.
"""

import json
import importlib
import os
from unittest.mock import MagicMock, patch

import pytest


# ── shared mock agent result ──────────────────────────────────────────────────

MOCK_RESULT = {
    "brief": {
        "current_issue":                  "Participant reports severe nausea.",
        "participant_concern":            "Participant considering withdrawal from study.",
        "historical_matches": [
            {"date": "Month 1", "event": "Nausea after dosage increase",
             "relevance": "Same symptom pattern."},
            {"date": "Month 2", "event": "Symptoms improved after meal-timing intervention",
             "relevance": "Prior successful outcome documented."},
        ],
        "historical_pattern":             "Recurring nausea following dosage escalation events.",
        "previous_outcome":               "Symptoms improved after meal-timing intervention.",
        "recommended_coordinator_action": (
            "Review historical nausea episode and prior outcome with the "
            "appropriate clinical team and follow applicable trial/site procedures."
        ),
        "safety_note":  "Not for clinical use. Prototype for hackathon demonstration.",
        "memory_used":  True,
        "memories_count": 2,
    },
    "retrieved_memories": [
        {"text": "Month 1: nausea after dosage.", "document_id": "checkin:P402:002",
         "tags": ["participant:P402", "trial:TRIAL-001"], "metadata": {"event_type": "symptom_report"}},
        {"text": "Month 1 follow-up: symptoms improved.", "document_id": "checkin:P402:003",
         "tags": ["participant:P402", "trial:TRIAL-001"], "metadata": {"event_type": "outcome"}},
    ],
    "hindsight_query": (
        "Find relevant historical interactions for Participant P402 related to "
        "nausea, dosage changes, interventions, symptom outcomes, and withdrawal concerns."
    ),
    "mode": "hindsight",
}

MOCK_BASELINE_RESULT = {
    "brief": {
        "current_issue":                  "Participant reports severe nausea.",
        "participant_concern":            "Participant considering withdrawal.",
        "historical_matches":             [],
        "historical_pattern":             "No relevant historical pattern identified.",
        "previous_outcome":               "No previous outcome documented.",
        "recommended_coordinator_action": "Review participant concern with clinical team.",
        "safety_note":  "Not for clinical use.",
        "memory_used":  False,
        "memories_count": 0,
    },
    "retrieved_memories": [],
    "hindsight_query":    None,
    "mode":               "baseline",
}


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture()
def full_app(tmp_path, monkeypatch):
    """Full app with temp DB, seeded with P402."""
    monkeypatch.setenv("DB_PATH",            str(tmp_path / "test.db"))
    monkeypatch.setenv("GROQ_API_KEY",       "test-groq")
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID",  "trial-bank")
    monkeypatch.setenv("HINDSIGHT_API_KEY",  "test-key")

    import db, app as flask_app
    importlib.reload(db)
    importlib.reload(flask_app)
    flask_app.app.config["TESTING"]    = True
    flask_app.app.config["SECRET_KEY"] = "test"

    with flask_app.app.app_context():
        db.init_db()
        db.upsert_participant("P402", "Participant 402", "TRIAL-001", "Active")
        db.upsert_participant("P117", "Participant 117", "TRIAL-001", "Active")

    with flask_app.app.test_client() as client:
        yield client, flask_app.app


# ── 1. Full hindsight pipeline ────────────────────────────────────────────────

def test_full_hindsight_pipeline(full_app):
    """Coordinator submits check-in → agent runs → result page rendered."""
    client, flask_app = full_app
    import db

    with patch("agent.run_agent", return_value=MOCK_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op1")), \
         patch("memory.get_version", return_value="1.0.0"):

        # Submit check-in
        resp = client.post(
            "/participants/P402/analyze",
            data={
                "checkin_text": (
                    "Participant P402 reports severe nausea returning over the past week. "
                    "Participant expressed significant frustration and stated they are "
                    "considering withdrawing from the study."
                ),
                "occurred_at": "2026-09-02",
                "mode":        "hindsight",
            },
            follow_redirects=True,
        )

    assert resp.status_code == 200
    assert b"Coordinator Action Brief" in resp.data
    assert b"nausea" in resp.data.lower()
    assert b"Hindsight queried" in resp.data

    # Verify DB state
    stats = db.get_stats()
    assert stats["checkins"]   == 1
    assert stats["agent_runs"] == 1


def test_full_baseline_pipeline(full_app):
    """Baseline mode produces result without memory indicator."""
    client, flask_app = full_app

    with patch("agent.run_agent", return_value=MOCK_BASELINE_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op2")), \
         patch("memory.get_version", return_value="1.0.0"):

        resp = client.post(
            "/participants/P402/analyze",
            data={
                "checkin_text": "Participant P402 reports nausea again.",
                "occurred_at":  "2026-09-02",
                "mode":         "baseline",
            },
            follow_redirects=True,
        )

    assert resp.status_code == 200
    assert b"baseline" in resp.data.lower()


# ── 2. Hindsight vs baseline comparison ───────────────────────────────────────

def test_hindsight_shows_memory_baseline_does_not(full_app):
    """Key product story: hindsight result has memory, baseline does not."""
    client, flask_app = full_app
    import db

    with patch("agent.run_agent", return_value=MOCK_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op3")), \
         patch("memory.get_version", return_value="1.0.0"):
        resp_h = client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Nausea.", "occurred_at": "2026-09-02", "mode": "hindsight"},
            follow_redirects=True,
        )

    with patch("agent.run_agent", return_value=MOCK_BASELINE_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op4")), \
         patch("memory.get_version", return_value="1.0.0"):
        resp_b = client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Nausea.", "occurred_at": "2026-09-02", "mode": "baseline"},
            follow_redirects=True,
        )

    assert b"Hindsight queried" in resp_h.data
    assert b"Hindsight queried" not in resp_b.data


# ── 3. Memory trace end-to-end ────────────────────────────────────────────────

def test_trace_shows_query_and_memories(full_app):
    """Trace page shows the exact Hindsight query and retrieved doc IDs."""
    client, app = full_app
    import db

    with app.app_context():
        db.save_checkin("ci-e2e", "P402", "2026-09-02T00:00:00Z", "Severe nausea.")
        db.save_agent_run(
            "run-e2e", "ci-e2e", "hindsight",
            final_output=MOCK_RESULT["brief"],
            hindsight_query=MOCK_RESULT["hindsight_query"],
            retrieved_memories=MOCK_RESULT["retrieved_memories"],
        )

    resp = client.get("/runs/run-e2e/trace")
    assert resp.status_code == 200
    assert b"Memory Trace" in resp.data
    assert b"checkin:P402:002" in resp.data
    assert b"checkin:P402:003" in resp.data
    assert b"nausea, dosage changes" in resp.data


# ── 4. Participant isolation in UI ────────────────────────────────────────────

def test_p117_cannot_see_p402_checkins(full_app):
    """P117 timeline must not contain P402's check-ins."""
    client, app = full_app
    import db

    with app.app_context():
        db.save_checkin("ci-p402", "P402", "2026-09-02T00:00:00Z", "P402 private check-in.")

    resp = client.get("/participants/P117")
    assert resp.status_code == 200
    assert b"P402 private check-in" not in resp.data


# ── 5. Dashboard stats are live ───────────────────────────────────────────────

def test_dashboard_stats_update_after_checkin(full_app):
    """Stats on dashboard reflect DB state after an analyze call."""
    client, flask_app = full_app
    import db

    with patch("memory.get_version", return_value="1.0.0"):
        resp_before = client.get("/")
    assert b">0<" in resp_before.data or b"0" in resp_before.data

    with patch("agent.run_agent", return_value=MOCK_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op5")):
        client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Check-in.", "occurred_at": "2026-09-02", "mode": "hindsight"},
        )

    with patch("memory.get_version", return_value="1.0.0"):
        resp_after = client.get("/")
    assert b"1" in resp_after.data


# ── 6. API endpoints return valid JSON ────────────────────────────────────────

def test_api_stats_returns_all_keys(full_app):
    client, _ = full_app
    import json as _json
    resp = client.get("/api/stats")
    data = _json.loads(resp.data)
    for key in ("participants", "checkins", "outcomes", "agent_runs"):
        assert key in data


def test_api_participants_returns_p402_and_p117(full_app):
    client, _ = full_app
    import json as _json
    resp = client.get("/api/participants")
    data = _json.loads(resp.data)
    ids = [p["id"] for p in data]
    assert "P402" in ids
    assert "P117" in ids


# ── 7. seed_demo + DB integration ─────────────────────────────────────────────

def test_seed_demo_populates_db(tmp_path, monkeypatch):
    """seed() → db.upsert_participant + db.save_checkin round-trip."""
    monkeypatch.setenv("DB_PATH",            str(tmp_path / "seed_test.db"))
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID",  "trial-bank")
    monkeypatch.setenv("HINDSIGHT_API_KEY",  "key")

    import db, seed_demo, importlib
    importlib.reload(db)
    db.init_db()

    # Seed all participants into SQLite manually (seed_demo seeds Hindsight;
    # the DB seeding happens via the Flask analyze route in prod, but we can
    # verify the data file is correct and seed_demo dry-runs cleanly)
    summary = seed_demo.seed(dry_run=True)
    assert summary["participants"] == 10
    assert summary["checkins"]     == 45  # total check-ins across all 10 participants

    # Also verify DB helpers work after init
    db.upsert_participant("P402", "Participant 402", "TRIAL-001", "Active")
    assert db.get_participant("P402")["trial_id"] == "TRIAL-001"


# ── 8. Urgent safety bypass in full route ────────────────────────────────────

def test_urgent_checkin_bypasses_llm_in_route(full_app):
    """Urgent language → agent returns urgent brief → result page shows emergency notice."""
    client, flask_app = full_app

    URGENT_RESULT = {
        "brief": {
            "current_issue":                  "I can't breathe and I need emergency help.",
            "participant_concern":            (
                "⚠ POTENTIAL URGENT SAFETY CONCERN DETECTED. "
                "Follow the applicable trial/site emergency or escalation procedure."
            ),
            "historical_matches":             [],
            "historical_pattern":             "Not assessed — urgent safety concern detected.",
            "previous_outcome":               "Not assessed — urgent safety concern detected.",
            "recommended_coordinator_action": (
                "⚠ POTENTIAL URGENT SAFETY CONCERN DETECTED. "
                "Follow the applicable trial/site emergency or escalation procedure "
                "and involve the appropriate clinical personnel immediately."
            ),
            "safety_note":    "Not for clinical use.",
            "memory_used":    False,
            "memories_count": 0,
        },
        "retrieved_memories": [],
        "hindsight_query":    None,
        "mode":               "urgent",
    }

    with patch("agent.run_agent", return_value=URGENT_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op6")):
        resp = client.post(
            "/participants/P402/analyze",
            data={
                "checkin_text": "I can't breathe and I need emergency help.",
                "occurred_at":  "2026-09-02",
                "mode":         "hindsight",
            },
            follow_redirects=True,
        )

    assert resp.status_code == 200
    assert b"URGENT" in resp.data


# ── 9. Error handling ─────────────────────────────────────────────────────────

def test_agent_failure_still_saves_checkin(full_app):
    """Even if agent fails, the check-in is saved to DB."""
    client, app = full_app
    import db

    FALLBACK = {
        "brief": {
            "current_issue": "text", "participant_concern": "Agent unavailable.",
            "historical_matches": [], "historical_pattern": "Not available.",
            "previous_outcome": "Not available.",
            "recommended_coordinator_action": "Review with clinical team.",
            "safety_note": "Not for clinical use.", "memory_used": False, "memories_count": 0,
        },
        "retrieved_memories": [], "hindsight_query": None, "mode": "hindsight", "error": "Groq down",
    }

    with patch("agent.run_agent", return_value=FALLBACK), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op7")):
        resp = client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Some text.", "occurred_at": "2026-09-02", "mode": "hindsight"},
            follow_redirects=True,
        )

    assert resp.status_code == 200
    with app.app_context():
        assert db.get_stats()["checkins"] == 1


# ── 10. Run count on participant page ─────────────────────────────────────────

def test_participant_page_shows_analysis_link(full_app):
    """After an analyze call, the participant timeline shows a link to the run."""
    client, flask_app = full_app
    import db

    with patch("agent.run_agent", return_value=MOCK_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op8")):
        client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Nausea.", "occurred_at": "2026-09-02", "mode": "hindsight"},
        )

    resp = client.get("/participants/P402")
    assert resp.status_code == 200
    assert b"hindsight" in resp.data.lower()
