"""
db.py — SQLite application database for TrialGuard.

Blueprint Section 15 / Section 14:
  SQLite = exact application records (participants, checkins, outcomes, agent_runs)
  Hindsight = agent long-term memory

Tables
------
  participants  — id, display_name, trial_id, status, created_at
  checkins      — id, participant_id, occurred_at, raw_text, created_at
  outcomes      — id, participant_id, checkin_id, occurred_at, description, outcome_text
  agent_runs    — id, checkin_id, mode, hindsight_query, retrieved_memories,
                  final_output, created_at

All timestamps stored as ISO 8601 text (UTC).
Database file: data/trialguard.db  (path overrideable via DB_PATH env var)
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_HERE    = Path(__file__).parent
DB_PATH  = Path(os.environ.get("DB_PATH", str(_HERE / "data" / "trialguard.db")))

# ── Connection ────────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    """Open (or create) the SQLite database and return a connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row          # rows accessible as dicts
    con.execute("PRAGMA journal_mode=WAL")  # safer concurrent access
    con.execute("PRAGMA foreign_keys=ON")
    return con


# ── Schema ────────────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS participants (
    id           TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    trial_id     TEXT NOT NULL DEFAULT 'TRIAL-001',
    status       TEXT NOT NULL DEFAULT 'Active',
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkins (
    id             TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(id),
    occurred_at    TEXT NOT NULL,
    raw_text       TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outcomes (
    id             TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(id),
    checkin_id     TEXT REFERENCES checkins(id),
    occurred_at    TEXT NOT NULL,
    description    TEXT,
    outcome_text   TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id                  TEXT PRIMARY KEY,
    checkin_id          TEXT REFERENCES checkins(id),
    mode                TEXT NOT NULL DEFAULT 'hindsight',
    hindsight_query     TEXT,
    retrieved_memories  TEXT,
    final_output        TEXT,
    created_at          TEXT NOT NULL
);
"""


def init_db() -> None:
    """Create all tables if they don't exist. Safe to call repeatedly."""
    with _conn() as con:
        con.executescript(_SCHEMA)
    logger.info("Database initialised at %s", DB_PATH)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


# ── Participants ──────────────────────────────────────────────────────────────

def upsert_participant(
    participant_id: str,
    display_name: str,
    trial_id: str = "TRIAL-001",
    status: str = "Active",
) -> dict[str, Any]:
    """Insert or update a participant row. Returns the final row dict."""
    with _conn() as con:
        con.execute(
            """
            INSERT INTO participants (id, display_name, trial_id, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                display_name = excluded.display_name,
                trial_id     = excluded.trial_id,
                status       = excluded.status
            """,
            (participant_id, display_name, trial_id, status, _now()),
        )
    return get_participant(participant_id)


def get_participant(participant_id: str) -> dict[str, Any] | None:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM participants WHERE id = ?", (participant_id,)
        ).fetchone()
    return _row_to_dict(row)


def list_participants() -> list[dict[str, Any]]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM participants ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


# ── Check-ins ─────────────────────────────────────────────────────────────────

def save_checkin(
    checkin_id: str,
    participant_id: str,
    occurred_at: str,
    raw_text: str,
) -> dict[str, Any]:
    """Insert a check-in record. Returns the inserted row dict."""
    with _conn() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO checkins
                (id, participant_id, occurred_at, raw_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (checkin_id, participant_id, occurred_at, raw_text, _now()),
        )
    return get_checkin(checkin_id)


def get_checkin(checkin_id: str) -> dict[str, Any] | None:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM checkins WHERE id = ?", (checkin_id,)
        ).fetchone()
    return _row_to_dict(row)


def list_checkins(participant_id: str) -> list[dict[str, Any]]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM checkins WHERE participant_id = ? ORDER BY occurred_at",
            (participant_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Outcomes ──────────────────────────────────────────────────────────────────

def save_outcome(
    outcome_id: str,
    participant_id: str,
    outcome_text: str,
    checkin_id: str | None = None,
    occurred_at: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    with _conn() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO outcomes
                (id, participant_id, checkin_id, occurred_at, description,
                 outcome_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                outcome_id,
                participant_id,
                checkin_id,
                occurred_at or _now(),
                description,
                outcome_text,
                _now(),
            ),
        )
    return get_outcome(outcome_id)


def get_outcome(outcome_id: str) -> dict[str, Any] | None:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM outcomes WHERE id = ?", (outcome_id,)
        ).fetchone()
    return _row_to_dict(row)


def list_outcomes(participant_id: str) -> list[dict[str, Any]]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM outcomes WHERE participant_id = ? ORDER BY occurred_at",
            (participant_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Agent runs ────────────────────────────────────────────────────────────────

def save_agent_run(
    run_id: str,
    checkin_id: str,
    mode: str,
    final_output: dict[str, Any] | str,
    hindsight_query: str | None = None,
    retrieved_memories: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Persist an agent run record.

    ``final_output`` and ``retrieved_memories`` are serialised to JSON strings
    for storage and deserialised when read back.
    """
    final_str    = json.dumps(final_output) if not isinstance(final_output, str) else final_output
    memories_str = json.dumps(retrieved_memories or [])
    with _conn() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO agent_runs
                (id, checkin_id, mode, hindsight_query, retrieved_memories,
                 final_output, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, checkin_id, mode, hindsight_query,
             memories_str, final_str, _now()),
        )
    return get_agent_run(run_id)


def get_agent_run(run_id: str) -> dict[str, Any] | None:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM agent_runs WHERE id = ?", (run_id,)
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    # Deserialise JSON fields
    try:
        d["final_output"]       = json.loads(d["final_output"] or "{}")
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        d["retrieved_memories"] = json.loads(d["retrieved_memories"] or "[]")
    except (json.JSONDecodeError, TypeError):
        d["retrieved_memories"] = []
    return d


def list_agent_runs(checkin_id: str) -> list[dict[str, Any]]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM agent_runs WHERE checkin_id = ? ORDER BY created_at",
            (checkin_id,),
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        try:
            d["final_output"]       = json.loads(d["final_output"] or "{}")
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            d["retrieved_memories"] = json.loads(d["retrieved_memories"] or "[]")
        except (json.JSONDecodeError, TypeError):
            d["retrieved_memories"] = []
        result.append(d)
    return result


def recent_agent_runs(limit: int = 10) -> list[dict[str, Any]]:
    """Return the most recent agent runs across all check-ins."""
    with _conn() as con:
        rows = con.execute(
            """
            SELECT ar.*, c.participant_id
            FROM agent_runs ar
            LEFT JOIN checkins c ON ar.checkin_id = c.id
            ORDER BY ar.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        try:
            d["final_output"]       = json.loads(d["final_output"] or "{}")
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            d["retrieved_memories"] = json.loads(d["retrieved_memories"] or "[]")
        except (json.JSONDecodeError, TypeError):
            d["retrieved_memories"] = []
        result.append(d)
    return result


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_stats() -> dict[str, int]:
    """Return high-level counts for the dashboard."""
    with _conn() as con:
        p  = con.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
        ci = con.execute("SELECT COUNT(*) FROM checkins").fetchone()[0]
        o  = con.execute("SELECT COUNT(*) FROM outcomes").fetchone()[0]
        ar = con.execute("SELECT COUNT(*) FROM agent_runs").fetchone()[0]
    return {
        "participants": p,
        "checkins":     ci,
        "outcomes":     o,
        "agent_runs":   ar,
    }


__all__ = [
    "init_db",
    "upsert_participant", "get_participant", "list_participants",
    "save_checkin",       "get_checkin",     "list_checkins",
    "save_outcome",       "get_outcome",     "list_outcomes",
    "save_agent_run",     "get_agent_run",   "list_agent_runs",
    "recent_agent_runs",  "get_stats",
]
