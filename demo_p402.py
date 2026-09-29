"""
demo_p402.py — TrialGuard P402 live demo script.

Blueprint Section 60 — the 60-second demo sequence:
  1. Show P402's seeded history (Month 1–5)
  2. Submit the Month 6 check-in (nausea + withdrawal concern)
  3. Run baseline mode → show generic response
  4. Run hindsight mode → show historical pattern + action brief
  5. Highlight the difference

Usage:
    python demo_p402.py              # full demo
    python demo_p402.py --seed       # seed Hindsight first, then run demo
    python demo_p402.py --seed-only  # just seed, don't run demo
    python demo_p402.py --baseline   # show baseline result only
    python demo_p402.py --hindsight  # show hindsight result only

Requirements:
    .env file with valid HINDSIGHT_BASE_URL, HINDSIGHT_API_KEY,
    HINDSIGHT_BANK_ID, GROQ_API_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

import memory as mem
import agent as ag
import db
from seed_demo import seed

# ── ANSI colours (gracefully disabled on non-TTY) ────────────────────────────

USE_COLOUR = sys.stdout.isatty()

def _c(code: str, text: str) -> str:
    if not USE_COLOUR:
        return text
    return f"\033[{code}m{text}\033[0m"

BOLD   = lambda t: _c("1",     t)
BLUE   = lambda t: _c("1;34",  t)
GREEN  = lambda t: _c("1;32",  t)
AMBER  = lambda t: _c("1;33",  t)
RED    = lambda t: _c("1;31",  t)
CYAN   = lambda t: _c("1;36",  t)
GREY   = lambda t: _c("90",    t)
DIM    = lambda t: _c("2",     t)

# ── P402 Month 6 check-in text ────────────────────────────────────────────────

P402_CHECKIN = (
    "Participant P402 reports severe nausea returning over the past week. "
    "Participant expressed significant frustration and stated they are "
    "considering withdrawing from the study. They asked whether there is "
    "any point in continuing given the recurring symptoms."
)

OCCURRED_AT = "2026-09-02T09:45:00Z"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _divider(char: str = "─", width: int = 62) -> str:
    return GREY(char * width)

def _wrap(text: str, indent: int = 4, width: int = 72) -> str:
    prefix = " " * indent
    return textwrap.fill(text, width=width,
                         initial_indent=prefix, subsequent_indent=prefix)

def _print_section(title: str, body: str, colour=BLUE) -> None:
    print()
    print(_divider())
    print(colour(f"  {title.upper()}"))
    print(_divider())
    print(_wrap(body))


def _print_brief(brief: dict, mode: str) -> None:
    """Pretty-print a CoordinatorBrief dict."""
    mode_label = GREEN("WITH HINDSIGHT MEMORY") if mode == "hindsight" else AMBER("BASELINE — NO MEMORY")
    print()
    print("=" * 64)
    print(BOLD(f"  COORDINATOR ACTION BRIEF  ·  {mode_label}"))
    print("=" * 64)

    _print_section("Current Issue",      brief.get("current_issue", ""),      BLUE)
    _print_section("Participant Concern", brief.get("participant_concern", ""), AMBER)

    matches = brief.get("historical_matches", [])
    if matches:
        print()
        print(_divider())
        print(GREEN("  HINDSIGHT MEMORY"))
        print(_divider())
        for i, m in enumerate(matches, 1):
            date      = m.get("date", "")    if isinstance(m, dict) else getattr(m, "date", "")
            event     = m.get("event", "")   if isinstance(m, dict) else getattr(m, "event", "")
            relevance = m.get("relevance", "")if isinstance(m, dict) else getattr(m, "relevance", "")
            print(f"    {GREEN('✓')} [{i}] {BOLD(date)} — {event}")
            print(f"         {DIM(relevance)}")
    else:
        _print_section("Historical Memory", "No relevant historical memory retrieved.", GREY)

    _print_section("Historical Pattern",      brief.get("historical_pattern", ""),             CYAN)
    _print_section("Previous Outcome",        brief.get("previous_outcome", ""),               CYAN)
    _print_section("Coordinator Action",      brief.get("recommended_coordinator_action", ""), GREEN)

    mem_used  = brief.get("memory_used", False)
    mem_count = brief.get("memories_count", 0)

    print()
    print(_divider())
    print("  MEMORY STATUS")
    print(_divider())
    if mem_used:
        print(f"    {GREEN('✓')} Hindsight queried")
        print(f"    {GREEN('✓')} {mem_count} relevant memories retrieved")
        print(f"    {GREEN('✓')} Historical context used in analysis")
    else:
        print(f"    {AMBER('—')} {'Baseline mode — no memory retrieval' if mode == 'baseline' else 'No relevant history found'}")

    print()
    print(AMBER(f"  ⚠  {brief.get('safety_note', '')}"))
    print()


# ── Demo steps ────────────────────────────────────────────────────────────────

def _step_show_history() -> None:
    print()
    print(BOLD("=" * 64))
    print(BOLD("  STEP 1 — P402 HISTORICAL TIMELINE"))
    print(BOLD("=" * 64))

    history = [
        ("Month 1  2026-03-10", "dosage_change",  "Dosage increase administered per protocol."),
        ("Month 1  2026-03-14", "symptom_report", "Participant reported moderate nausea after dosage increase."),
        ("Month 1  2026-03-28", "outcome",        "Follow-up: symptoms significantly improved after meal-timing intervention."),
        ("Month 2  2026-04-08", "routine",        "Routine check-in — no issues reported."),
        ("Month 3  2026-05-06", "dosage_change",  "Second protocol-scheduled dosage increase administered."),
        ("Month 4  2026-06-03", "routine",        "Routine check-in — good tolerance, following meal-timing guidance."),
        ("Month 5  2026-07-08", "routine",        "Routine check-in — participant continues to do well."),
    ]

    type_colours = {
        "dosage_change":  AMBER,
        "symptom_report": RED,
        "outcome":        GREEN,
        "routine":        DIM,
    }

    for date, etype, text in history:
        colour = type_colours.get(etype, DIM)
        print(f"  {GREY(date)}  {colour(f'[{etype}]')}")
        print(f"    {text}")


def _step_show_checkin() -> None:
    print()
    print(BOLD("=" * 64))
    print(BOLD("  STEP 2 — MONTH 6 CHECK-IN  (2026-09-02)"))
    print(BOLD("=" * 64))
    print()
    print(_wrap(P402_CHECKIN))
    print()
    print(AMBER("  ↓  Submitting to TrialGuard agent…"))


def _step_baseline() -> dict:
    print()
    print(BOLD("=" * 64))
    print(BOLD("  STEP 3 — BASELINE ANALYSIS  (no memory)"))
    print(BOLD("=" * 64))
    print(DIM("  Running without Hindsight — LLM sees today's complaint only…"))

    result = ag.run_agent(
        checkin_text=P402_CHECKIN,
        participant_id="P402",
        trial_id="TRIAL-001",
        occurred_at=OCCURRED_AT,
        mode="baseline",
    )
    _print_brief(result["brief"], "baseline")
    return result


def _step_hindsight() -> dict:
    print()
    print(BOLD("=" * 64))
    print(BOLD("  STEP 4 — HINDSIGHT ANALYSIS  (with memory)"))
    print(BOLD("=" * 64))
    print(DIM("  Running with Hindsight — retrieving historical context…"))

    result = ag.run_agent(
        checkin_text=P402_CHECKIN,
        participant_id="P402",
        trial_id="TRIAL-001",
        occurred_at=OCCURRED_AT,
        mode="hindsight",
    )

    if result.get("hindsight_query"):
        print()
        print(GREY("  Hindsight query sent:"))
        print(GREY(f"  \"{result['hindsight_query'][:120]}…\""))

    memories = result.get("retrieved_memories", [])
    if memories:
        print()
        print(GREEN(f"  ✓ {len(memories)} memories retrieved from Hindsight"))
        for m in memories:
            doc_id = m.get("document_id", "?")
            snippet = (m.get("text", "")[:80] + "…") if len(m.get("text", "")) > 80 else m.get("text", "")
            print(f"    {GREEN('•')} {GREY(doc_id)}")
            print(f"       {snippet}")

    _print_brief(result["brief"], "hindsight")
    return result


def _step_compare(baseline: dict, hindsight: dict) -> None:
    print()
    print(BOLD("=" * 64))
    print(BOLD("  STEP 5 — THE DIFFERENCE HINDSIGHT MAKES"))
    print(BOLD("=" * 64))
    print()

    b_pattern = baseline["brief"].get("historical_pattern", "")
    h_pattern = hindsight["brief"].get("historical_pattern", "")
    b_outcome = baseline["brief"].get("previous_outcome", "")
    h_outcome = hindsight["brief"].get("previous_outcome", "")

    print(f"  {AMBER('WITHOUT MEMORY')}  historical_pattern:")
    print(f"    {_wrap(b_pattern, indent=0).strip()}")
    print()
    print(f"  {GREEN('WITH HINDSIGHT')}  historical_pattern:")
    print(f"    {_wrap(h_pattern, indent=0).strip()}")
    print()
    print(f"  {AMBER('WITHOUT MEMORY')}  previous_outcome:")
    print(f"    {_wrap(b_outcome, indent=0).strip()}")
    print()
    print(f"  {GREEN('WITH HINDSIGHT')}  previous_outcome:")
    print(f"    {_wrap(h_outcome, indent=0).strip()}")
    print()
    print(_divider("═"))
    print(BOLD(
        "  \"Without memory, the agent sees today's complaint.\n"
        "   With Hindsight, it understands the history behind it.\""
    ))
    print(_divider("═"))
    print()


# ── Retain the Month 6 outcome back into Hindsight ───────────────────────────

def _retain_outcome(hindsight_result: dict) -> None:
    brief = hindsight_result["brief"]
    outcome_text = (
        f"Participant P402. Trial: TRIAL-001. Date: {OCCURRED_AT[:10]}.\n\n"
        f"Month 6 check-in analysis:\n"
        f"Current issue: {brief.get('current_issue', '')}\n"
        f"Historical pattern identified: {brief.get('historical_pattern', '')}\n"
        f"Previous outcome on record: {brief.get('previous_outcome', '')}\n"
        f"Coordinator action recommended: {brief.get('recommended_coordinator_action', '')}"
    )
    try:
        mem.retain(
            content=outcome_text,
            participant_id="P402",
            document_id="outcome:demo_p402:month6",
            metadata={
                "participant_id": "P402",
                "trial_id":       "TRIAL-001",
                "event_type":     "agent_outcome",
                "source":         "demo_p402",
            },
            extra_tags=["trial:TRIAL-001"],
        )
        print(GREEN("  ✓ Month 6 outcome retained in Hindsight for future retrieval."))
    except Exception as exc:
        print(AMBER(f"  ⚠ Could not retain outcome: {exc}"))


# ── Health check ──────────────────────────────────────────────────────────────

def _health_check() -> bool:
    print(DIM("  Checking Hindsight connection…"), end=" ", flush=True)
    try:
        ver = mem.get_version()
        print(GREEN(f"OK  (API version: {ver})"))
        return True
    except Exception as exc:
        print(RED(f"FAILED  ({exc})"))
        return False


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TrialGuard P402 live demo script."
    )
    parser.add_argument("--seed",       action="store_true", help="Seed Hindsight before running demo.")
    parser.add_argument("--seed-only",  action="store_true", help="Seed only, skip demo.")
    parser.add_argument("--baseline",   action="store_true", help="Show baseline result only.")
    parser.add_argument("--hindsight",  action="store_true", help="Show Hindsight result only.")
    args = parser.parse_args()

    print()
    print(BOLD("=" * 62))
    print(BOLD("       T R I A L G U A R D  D E M O"))
    print(BOLD("       Participant P402  .  TRIAL-001"))
    print(BOLD("=" * 62))
    print()

    # Health check
    ok = _health_check()
    if not ok and not args.baseline:
        print(RED("  Hindsight is unavailable. Re-run with --baseline for an offline demo."))
        sys.exit(1)

    # Seed if requested
    if args.seed or args.seed_only:
        print()
        print(BOLD("  Seeding Hindsight memory bank with P402 history…"))
        seed(participant_id="P402")
        print(GREEN("  ✓ Seeding complete."))
        if args.seed_only:
            return

    # Ensure DB is ready
    db.init_db()
    db.upsert_participant("P402", "Participant 402", "TRIAL-001", "Active")

    # Run demo
    _step_show_history()
    _step_show_checkin()

    baseline_result  = None
    hindsight_result = None

    if args.hindsight:
        hindsight_result = _step_hindsight()
    elif args.baseline:
        baseline_result = _step_baseline()
    else:
        # Full demo: both modes + comparison
        baseline_result  = _step_baseline()
        hindsight_result = _step_hindsight()
        _step_compare(baseline_result, hindsight_result)

    # Retain the new outcome back into Hindsight (learning loop)
    if hindsight_result and ok:
        _retain_outcome(hindsight_result)

    # Save run to SQLite for audit
    if hindsight_result or baseline_result:
        result = hindsight_result or baseline_result
        run_id = "demo:P402:month6"
        ci_id  = "demo_checkin:P402:month6"
        db.save_checkin(ci_id, "P402", OCCURRED_AT, P402_CHECKIN)
        db.save_agent_run(
            run_id, ci_id,
            mode=result["mode"],
            final_output=result["brief"],
            hindsight_query=result.get("hindsight_query"),
            retrieved_memories=result.get("retrieved_memories", []),
        )
        print(DIM(f"\n  Run saved: {run_id}  (view at /runs/{run_id} when app is running)"))


if __name__ == "__main__":
    main()
