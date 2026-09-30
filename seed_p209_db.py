"""
seed_p209_db.py — Seed P209's historical check-ins into SQLite for the demo.

This populates the TIMELINE view in the web UI.
Hindsight memories are separate — run `python seed_demo.py --participant P209`
for those.

Run once before the demo:
    python seed_p209_db.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import db

db.init_db()

# Ensure P209 exists in participants table
db.upsert_participant("P209", "Participant 209", "TRIAL-001", "Active")

CHECKINS = [
    {
        "checkin_id":   "checkin:P209:001",
        "occurred_at":  "2026-03-15T11:00:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-03-15.\n\n"
            "Participant reported mild to moderate headache beginning three days after "
            "dosage initiation. Described as frontal pressure, lasting several hours per day. "
            "Coordinator advised adequate hydration and logged the report."
        ),
    },
    {
        "checkin_id":   "checkin:P209:002",
        "occurred_at":  "2026-03-29T10:00:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-03-29.\n\n"
            "Headache symptoms reduced following hydration guidance. Participant reports "
            "headaches are now occasional and mild. Coordinator documented improvement. "
            "No further intervention required."
        ),
    },
    {
        "checkin_id":   "checkin:P209:003",
        "occurred_at":  "2026-05-09T09:30:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-05-09.\n\n"
            "Dosage escalation per protocol. Coordinator reminded participant to maintain "
            "fluid intake given prior headache history."
        ),
    },
    {
        "checkin_id":   "checkin:P209:004",
        "occurred_at":  "2026-05-15T10:00:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-05-15.\n\n"
            "Headache returned following the most recent dosage increase. Moderate severity. "
            "Participant is concerned this is a recurring pattern linked to dosage changes. "
            "Coordinator reviewed hydration guidance and documented the recurrence."
        ),
    },
    {
        "checkin_id":   "checkin:P209:005",
        "occurred_at":  "2026-09-03T10:30:00Z",
        "raw_text": (
            "Participant P209. Trial: TRIAL-001. Date: 2026-09-03.\n\n"
            "Headache reported again at Month 6 check-in, coinciding with the third dosage "
            "increase. Participant notes this is the third time headaches have followed a "
            "dosage change. Coordinator documented the recurring pattern for clinical team review."
        ),
    },
]

print("\nSeeding P209 check-ins into SQLite...\n")

for ci in CHECKINS:
    db.save_checkin(
        checkin_id=ci["checkin_id"],
        participant_id="P209",
        occurred_at=ci["occurred_at"],
        raw_text=ci["raw_text"],
    )
    print(f"  Saved {ci['checkin_id']}  ({ci['occurred_at'][:10]})")

print(f"\nDone. P209 now has {len(db.list_checkins('P209'))} check-in(s) in SQLite.")
print("Refresh http://127.0.0.1:5000/participants/P209 to see the timeline.")
