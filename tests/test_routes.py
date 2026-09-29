"""
tests/test_routes.py — Phase 13/15: Flask routes + audit trace.

All tests use a temp SQLite DB and mock the agent so no Groq/Hindsight
calls are made.
"""

import json
import os
import importlib
from unittest.mock import MagicMock, patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def app_client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH",           str(tmp_path / "test.db"))
    monkeypatch.setenv("GROQ_API_KEY",      "test-groq")
    monkeypatch.setenv("HINDSIGHT_BASE_URL","http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    monkeypatch.setenv("HINDSIGHT_API_KEY", "test-key")

    import db, app as flask_app
    importlib.reload(db)
    importlib.reload(flask_app)

    flask_app.app.config["TESTING"]    = True
    flask_app.app.config["SECRET_KEY"] = "test-secret"

    with flask_app.app.test_client() as client:
        with flask_app.app.app_context():
            db.init_db()
            # Seed one participant
            db.upsert_participant("P402", "Participant 402", "TRIAL-001", "Active")
        yield client


MOCK_AGENT_RESULT = {
    "brief": {
        "current_issue":                  "Participant reports nausea.",
        "participant_concern":            "Considering withdrawal.",
        "historical_matches":             [
            {"date": "Month 1", "event": "Nausea after dosage", "relevance": "Same symptom"}
        ],
        "historical_pattern":             "Recurring nausea after dosage events.",
        "previous_outcome":               "Symptoms improved after intervention.",
        "recommended_coordinator_action": "Review with clinical team.",
        "safety_note":                    "Not for clinical use.",
        "memory_used":                    True,
        "memories_count":                 1,
    },
    "retrieved_memories": [{"text": "Month 1 nausea", "document_id": "checkin:P402:001", "tags": [], "metadata": {}}],
    "hindsight_query":    "previous nausea and dosage changes",
    "mode":               "hindsight",
}


# ── Dashboard ─────────────────────────────────────────────────────────────────

def test_dashboard_loads(app_client):
    with patch("memory.get_version", return_value="1.0.0"):
        resp = app_client.get("/")
    assert resp.status_code == 200
    assert b"TrialGuard" in resp.data
    assert b"P402" in resp.data


def test_dashboard_hindsight_down(app_client):
    with patch("memory.get_version", side_effect=Exception("down")):
        resp = app_client.get("/")
    assert resp.status_code == 200
    assert b"unavailable" in resp.data.lower() or b"TrialGuard" in resp.data


# ── Participant page ──────────────────────────────────────────────────────────

def test_participant_page_loads(app_client):
    resp = app_client.get("/participants/P402")
    assert resp.status_code == 200
    assert b"Participant 402" in resp.data


def test_participant_page_404(app_client):
    resp = app_client.get("/participants/NOTEXIST")
    assert resp.status_code == 404


# ── Check-in form ─────────────────────────────────────────────────────────────

def test_checkin_form_loads(app_client):
    resp = app_client.get("/participants/P402/checkin")
    assert resp.status_code == 200
    assert b"Check-in" in resp.data


def test_checkin_form_404_unknown_participant(app_client):
    resp = app_client.get("/participants/P999/checkin")
    assert resp.status_code == 404


# ── Analyze route ─────────────────────────────────────────────────────────────

def test_analyze_redirects_to_result(app_client):
    with patch("agent.run_agent", return_value=MOCK_AGENT_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op-1")):
        resp = app_client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Severe nausea again.", "occurred_at": "2026-09-02", "mode": "hindsight"},
        )
    assert resp.status_code == 302
    assert "/runs/" in resp.headers["Location"]


def test_analyze_saves_checkin_to_db(app_client):
    import db
    with patch("agent.run_agent", return_value=MOCK_AGENT_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op-1")):
        app_client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Month 6 nausea.", "occurred_at": "2026-09-02", "mode": "hindsight"},
        )
    checkins = db.list_checkins("P402")
    assert len(checkins) == 1
    assert "nausea" in checkins[0]["raw_text"]


def test_analyze_saves_agent_run_to_db(app_client):
    import db
    with patch("agent.run_agent", return_value=MOCK_AGENT_RESULT), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op-1")):
        app_client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "Nausea.", "occurred_at": "2026-09-02", "mode": "hindsight"},
        )
    stats = db.get_stats()
    assert stats["agent_runs"] == 1


def test_analyze_empty_text_returns_400(app_client):
    resp = app_client.post(
        "/participants/P402/analyze",
        data={"checkin_text": "", "occurred_at": "2026-09-02", "mode": "hindsight"},
    )
    assert resp.status_code == 400


def test_analyze_unknown_participant_404(app_client):
    resp = app_client.post(
        "/participants/P999/analyze",
        data={"checkin_text": "text", "occurred_at": "2026-09-02", "mode": "hindsight"},
    )
    assert resp.status_code == 404


def test_analyze_participant_id_comes_from_url_not_form(app_client):
    """Blueprint Section 23: participant_id must be taken from URL, not form data."""
    captured = {}

    def fake_agent(checkin_text, participant_id, **kwargs):
        captured["participant_id"] = participant_id
        return MOCK_AGENT_RESULT

    with patch("agent.run_agent", side_effect=fake_agent), \
         patch("memory.retain",   return_value=MagicMock(items_count=1, operation_id="op")):
        app_client.post(
            "/participants/P402/analyze",
            data={"checkin_text": "text", "occurred_at": "2026-09-02",
                  "mode": "hindsight", "participant_id": "P999"},  # attacker injects P999
        )

    # Must always be P402 (from URL), never P999 (from form)
    assert captured["participant_id"] == "P402"


# ── Result page ───────────────────────────────────────────────────────────────

def test_result_page_loads(app_client):
    import db
    db.save_checkin("ci-001", "P402", "2026-09-02T00:00:00Z", "Nausea.")
    db.save_agent_run(
        "run-001", "ci-001", "hindsight",
        final_output=MOCK_AGENT_RESULT["brief"],
        hindsight_query="previous nausea",
        retrieved_memories=MOCK_AGENT_RESULT["retrieved_memories"],
    )
    resp = app_client.get("/runs/run-001")
    assert resp.status_code == 200
    assert b"Coordinator Action Brief" in resp.data
    assert b"nausea" in resp.data.lower()


def test_result_page_404_unknown_run(app_client):
    resp = app_client.get("/runs/NOTEXIST")
    assert resp.status_code == 404


def test_result_shows_memory_used_indicator(app_client):
    import db
    db.save_checkin("ci-001", "P402", "2026-09-02T00:00:00Z", "text")
    db.save_agent_run("run-001", "ci-001", "hindsight", final_output=MOCK_AGENT_RESULT["brief"])
    resp = app_client.get("/runs/run-001")
    assert b"Hindsight queried" in resp.data or b"memories retrieved" in resp.data


# ── Memory trace page (Phase 15) ──────────────────────────────────────────────

def test_trace_page_loads(app_client):
    import db
    db.save_checkin("ci-001", "P402", "2026-09-02T00:00:00Z", "Nausea.")
    db.save_agent_run(
        "run-001", "ci-001", "hindsight",
        final_output=MOCK_AGENT_RESULT["brief"],
        hindsight_query="previous nausea",
        retrieved_memories=MOCK_AGENT_RESULT["retrieved_memories"],
    )
    resp = app_client.get("/runs/run-001/trace")
    assert resp.status_code == 200
    assert b"Memory Trace" in resp.data
    assert b"previous nausea" in resp.data


def test_trace_page_shows_document_id(app_client):
    import db
    db.save_checkin("ci-001", "P402", "2026-09-02T00:00:00Z", "text")
    db.save_agent_run(
        "run-001", "ci-001", "hindsight",
        final_output={},
        hindsight_query="query",
        retrieved_memories=[{"text": "m1", "document_id": "checkin:P402:001", "tags": [], "metadata": {}}],
    )
    resp = app_client.get("/runs/run-001/trace")
    assert b"checkin:P402:001" in resp.data


def test_trace_page_404_unknown_run(app_client):
    resp = app_client.get("/runs/NOTEXIST/trace")
    assert resp.status_code == 404


# ── API endpoints ─────────────────────────────────────────────────────────────

def test_api_stats(app_client):
    resp = app_client.get("/api/stats")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "participants" in data
    assert data["participants"] == 1


def test_api_participants(app_client):
    resp = app_client.get("/api/participants")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert data[0]["id"] == "P402"


# ── Error pages ───────────────────────────────────────────────────────────────

def test_404_page(app_client):
    resp = app_client.get("/nonexistent-route")
    assert resp.status_code == 404
