"""
reset_p209_db.py — Remove all demo check-ins for P209 and restore clean history.

Run this to:
  1. Delete ALL checkins and agent_runs for P209 from SQLite
  2. Re-seed the 5 original historical check-ins (no demo runs)

Usage:
    python reset_p209_db.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import sqlite3
import db

db.init_db()

# ── Step 1: Delete all existing P209 checkins and runs ───────────────────────

DB_PATH = db.DB_PATH

with sqlite3.connect(str(DB_PATH)) as con:
    # Delete agent_runs linked to P209 checkins
    con.execute("""
        DELETE FROM agent_runs
        WHERE checkin_id IN (
            SELECT id FROM checkins WHERE participant_id = 'P209'
        )
    """)
    deleted_runs = con.execute("SELECT changes()").fetchone()[0]

    # Delete all P209 checkins
    con.execute("DELETE FROM checkins WHERE participant_id = 'P209'")
    deleted_ci = con.execute("SELECT changes()").fetchone()[0]

print(f"  Removed {deleted_ci} check-in(s) and {deleted_runs} agent run(s) for P209.")

# ── Step 2: Re-seed the 5 clean historical check-ins ─────────────────────────

db.upsert_participant("P209", "Participant 209", "TRIAL-001", "Active")

CHECKINS = [
    {
        "checkin_id":  "checkin:P209:001",
        "occurred_at": "2026-03-15T11:00:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-03-15.\n\n"
            "Participant reported mild to moderate headache beginning three days after "
            "dosage initiation. Described as frontal pressure, lasting several hours per day. "
            "Coordinator advised adequate hydration and logged the report."
        ),
    },
    {
        "checkin_id":  "checkin:P209:002",
        "occurred_at": "2026-03-29T10:00:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-03-29.\n\n"
            "Headache symptoms reduced following hydration guidance. Participant reports "
            "headaches are now occasional and mild. Coordinator documented improvement. "
            "No further intervention required."
        ),
    },
    {
        "checkin_id":  "checkin:P209:003",
        "occurred_at": "2026-05-09T09:30:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-05-09.\n\n"
            "Dosage escalation per protocol. Coordinator reminded participant to maintain "
            "fluid intake given prior headache history."
        ),
    },
    {
        "checkin_id":  "checkin:P209:004",
        "occurred_at": "2026-05-15T10:00:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-05-15.\n\n"
            "Headache returned following the most recent dosage increase. Moderate severity. "
            "Participant is concerned this is a recurring pattern linked to dosage changes. "
            "Coordinator reviewed hydration guidance and documented the recurrence."
        ),
    },
    {
        "checkin_id":  "checkin:P209:005",
        "occurred_at": "2026-09-03T10:30:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-09-03.\n\n"
            "Headache reported again at Month 6 check-in, coinciding with the third dosage "
            "increase. Participant notes this is the third time headaches have followed a "
            "dosage change. Coordinator documented the recurring pattern for clinical team review."
        ),
    },
]

print("\nRe-seeding 5 clean historical check-ins for P209...")
for ci in CHECKINS:
    db.save_checkin(
        checkin_id=ci["checkin_id"],
        participant_id="P209",
        occurred_at=ci["occurred_at"],
        raw_text=ci["raw_text"],
    )
    print(f"  Saved {ci['checkin_id']}  ({ci['occurred_at'][:10]})")

final = db.list_checkins("P209")
print(f"\nDone. P209 now has {len(final)} clean check-in(s) in SQLite.")
print("Refresh http://127.0.0.1:5000/participants/P209")
