"""
seed_demo.py — Seed the Hindsight memory bank with synthetic demo data.

Architecture (blueprint Sections 18, 19, 23, 49)
-------------------------------------------------
1. Reads data/demo_data.json — 10 participants, TRIAL-001, Month 1–6 check-ins.
2. Calls memory.ensure_bank_exists() once.
3. For each participant × check-in:
   - Builds a narrative-style content string (blueprint Section 9).
   - Calls retain_checkin() which stores it with:
       document_id  = "checkin:<participant_id>:<checkin_id>"   (Section 13)
       timestamp    = occurred_at ISO string                    (Section 10)
       tags         = ["participant:<id>", "trial:<trial_id>"]  (Section 11)
       metadata     = participant_id, trial_id, event_type, ...  (Section 12)

Usage
-----
    python seed_demo.py                     # seed all 10 participants
    python seed_demo.py --participant P402  # seed only P402
    python seed_demo.py --dry-run           # render & print, no network calls
    python seed_demo.py --verify P402       # recall P402 after seeding

Output on success
-----------------
    Demo data seeded successfully.
    Participants : 10
    Check-ins    : 57
    Hero         : P402
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import memory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed_demo")

DATA_FILE = Path(__file__).parent / "data" / "demo_data.json"


# ── Data loading ──────────────────────────────────────────────────────────────

def load_demo_data() -> dict:
    """Load and return the full demo dataset from data/demo_data.json."""
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


# ── Core retain function (blueprint Section 18) ───────────────────────────────

def retain_checkin(
    participant_id: str,
    trial_id: str,
    checkin_id: str,
    occurred_at: str,
    event_type: str,
    text: str,
    *,
    dry_run: bool = False,
) -> None:
    """
    Retain a single participant check-in event in Hindsight.

    Parameters
    ----------
    participant_id : e.g. "P402"
    trial_id       : e.g. "TRIAL-001"
    checkin_id     : e.g. "001"
    occurred_at    : ISO 8601 timestamp string e.g. "2026-03-10T10:00:00Z"
    event_type     : "routine" | "symptom_report" | "dosage_change" | "outcome" | "concern"
    text           : Narrative check-in text (already formatted in demo_data.json)
    dry_run        : If True, print the content instead of sending to Hindsight.
    """
    doc_id = f"checkin:{participant_id}:{checkin_id}"          # Section 13
    tags   = [f"participant:{participant_id}", f"trial:{trial_id}"]  # Section 11
    meta   = {                                                  # Section 12
        "participant_id": participant_id,
        "trial_id":       trial_id,
        "event_type":     event_type,
        "checkin_id":     checkin_id,
        "occurred_at":    occurred_at,
        "source":         "synthetic_demo",
    }

    if dry_run:
        print(f"\n{'─'*60}")
        print(f"  document_id : {doc_id}")
        print(f"  occurred_at : {occurred_at}")
        print(f"  event_type  : {event_type}")
        print(f"  tags        : {tags}")
        print(f"  metadata    : {meta}")
        print(f"  content preview:")
        print("  " + text[:300].replace("\n", "\n  ") + ("…" if len(text) > 300 else ""))
        return

    # Parse timestamp for Hindsight temporal retrieval (Section 10)
    try:
        ts = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
    except ValueError:
        ts = None

    _get_client = memory._get_client
    bank        = memory._bank_id()

    resp = _get_client().retain(
        bank_id     = bank,
        content     = text,
        context     = "clinical_trial_checkin",
        timestamp   = ts,
        document_id = doc_id,
        metadata    = meta,
        tags        = tags,
    )
    logger.info(
        "  ✓ %s  [%s]  items=%d  op=%s",
        doc_id, event_type, resp.items_count, resp.operation_id,
    )


# ── Seed logic ────────────────────────────────────────────────────────────────

def seed(
    participant_id: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Seed Hindsight with demo check-in data.

    Returns
    -------
    dict  summary with keys: participants, checkins, hero
    """
    data         = load_demo_data()
    trial_id     = data["trial"]["id"]
    participants = data["participants"]

    # Filter to single participant if requested
    if participant_id:
        participants = [p for p in participants if p["id"] == participant_id]
        if not participants:
            logger.error(
                "Unknown participant '%s'. Available: %s",
                participant_id,
                [p["id"] for p in data["participants"]],
            )
            sys.exit(1)

    if not dry_run:
        logger.info("Ensuring memory bank exists…")
        memory.ensure_bank_exists()

    total_checkins = 0

    for participant in participants:
        pid      = participant["id"]
        checkins = participant["checkins"]
        logger.info(
            "Seeding %s (%s) — %d check-in(s) | pattern: %s",
            pid, participant["display_name"], len(checkins), participant["pattern"],
        )

        for ci in checkins:
            retain_checkin(
                participant_id = pid,
                trial_id       = trial_id,
                checkin_id     = ci["checkin_id"],
                occurred_at    = ci["occurred_at"],
                event_type     = ci["event_type"],
                text           = ci["text"],
                dry_run        = dry_run,
            )
            total_checkins += 1

    summary = {
        "participants": len(participants),
        "checkins":     total_checkins,
        "hero":         "P402",
    }

    if dry_run:
        print(f"\n[dry-run] Would have seeded {total_checkins} check-in(s) "
              f"across {len(participants)} participant(s). No data written.")
    else:
        logger.info(
            "\nDemo data seeded successfully.\n"
            "  Participants : %d\n"
            "  Check-ins    : %d\n"
            "  Hero         : P402",
            summary["participants"], summary["checkins"],
        )

    return summary


# ── Optional post-seed verification (blueprint Section 51) ────────────────────

def verify(participant_id: str = "P402") -> None:
    """
    Recall memories for *participant_id* and print them to confirm seeding worked.
    Requires a live Hindsight server.
    """
    logger.info("Verifying recall for participant %s…", participant_id)
    query = (
        f"Find relevant historical interactions for Participant {participant_id} "
        "related to nausea, dosage changes, interventions, symptom outcomes, "
        "and withdrawal concerns."
    )
    resp = memory.recall(
        query          = query,
        participant_id = participant_id,
        budget         = "mid",
        max_tokens     = 3000,
    )
    if not resp.results:
        print(f"No memories found for {participant_id}. Was seed run first?")
        return

    print(f"\n{'='*60}")
    print(f"  Recall results for {participant_id} ({len(resp.results)} memories)")
    print(f"{'='*60}")
    for i, r in enumerate(resp.results, 1):
        print(f"\n  [{i}] {getattr(r, 'text', '')[:300]}…")
        print(f"       tags: {getattr(r, 'tags', [])}")
        print(f"       doc : {getattr(r, 'document_id', 'n/a')}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed TrialGuard Hindsight memory bank with synthetic demo data."
    )
    parser.add_argument(
        "--participant", "-p",
        metavar="ID",
        help="Seed only this participant (e.g. P402). Default: all 10.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render and print check-in content without writing to Hindsight.",
    )
    parser.add_argument(
        "--verify",
        metavar="ID",
        nargs="?",
        const="P402",
        help="After seeding, run a recall verification for this participant (default P402).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    seed(participant_id=args.participant, dry_run=args.dry_run)
    if args.verify and not args.dry_run:
        verify(args.verify)
