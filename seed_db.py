"""
seed_db.py — Populate the SQLite database with all 10 demo participants.

Run this ONCE after starting the app for the first time, or any time you
want to reset the participant list in the web UI.

Usage:
    python seed_db.py

What it does:
    1. Initialises the SQLite database (creates tables if missing).
    2. Inserts / updates all 10 participants from data/demo_data.json.
    3. Prints a confirmation table.

This does NOT touch Hindsight. For Hindsight seeding, run:
    python seed_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import db

DATA_FILE = Path(__file__).parent / "data" / "demo_data.json"


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    db.init_db()
    print(f"\nSeeding {len(data['participants'])} participants into SQLite...\n")

    rows = []
    for p in data["participants"]:
        db.upsert_participant(
            participant_id=p["id"],
            display_name=p["display_name"],
            trial_id=p["trial_id"],
            status=p["status"],
        )
        rows.append((p["id"], p["display_name"], p["trial_id"], p["status"], p["pattern"]))

    # Print summary table
    print(f"  {'ID':<8} {'Name':<20} {'Trial':<12} {'Status':<10} Pattern")
    print(f"  {'-'*8} {'-'*20} {'-'*12} {'-'*10} {'-'*40}")
    for pid, name, trial, status, pattern in rows:
        print(f"  {pid:<8} {name:<20} {trial:<12} {status:<10} {pattern[:45]}")

    stats = db.get_stats()
    print(f"\n  Done. Database now has {stats['participants']} participant(s).")
    print(f"  DB path: {db.DB_PATH}\n")


if __name__ == "__main__":
    main()
