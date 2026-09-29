"""
safety.py — Deterministic safety validator for TrialGuard.

Blueprint Sections 44–45:
  A rule-based layer sits between the LLM output and the UI.
  It detects prohibited patterns and replaces the offending field
  with a safe fallback — it never silently passes dangerous content.

Prohibited patterns fall into two categories:

  URGENT  — language suggesting immediate physical danger.
             These are detected in the *raw check-in text* before the
             agent even runs, so the system can fast-path to an emergency
             notice without waiting for LLM reasoning.

  OUTPUT  — patterns in the *agent's final output* that cross the
             defined role boundary (diagnosis, prescription, dosage
             changes, causal overclaims).
"""

from __future__ import annotations

import re
import logging
from models import CoordinatorBrief

logger = logging.getLogger(__name__)

# ── Urgent language patterns (check-in text) ─────────────────────────────────
# Blueprint Section 44
_URGENT_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(severe|serious|extreme)\s+(trouble|difficulty)\s+breathing\b", re.I),
    re.compile(r"\bcan[\'']?t\s+breathe\b", re.I),
    re.compile(r"\bchest\s+pain\b", re.I),
    re.compile(r"\bheart\s+(attack|failure)\b", re.I),
    re.compile(r"\b(feel|feels?|feeling)\s+(like\s+i\s+(may|might|am going to)?\s*)?(collapse|faint|die|pass\s*out)\b", re.I),
    re.compile(r"\bunconsci(ous|ousness)\b", re.I),
    re.compile(r"\bemergency\s+help\b", re.I),
    re.compile(r"\b(call|need|want)\s+(an?\s+)?ambulance\b", re.I),
    re.compile(r"\bsuicid(e|al)\b", re.I),
    re.compile(r"\bself[\s\-]harm\b", re.I),
]

# ── Prohibited output patterns ────────────────────────────────────────────────
# Blueprint Section 45
_PROHIBITED_OUTPUT: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(increase|decrease|adjust|change|modify)\s+(the\s+)?dosage\b", re.I),
     "dosage modification instruction"),
    (re.compile(r"\b(increase|decrease|adjust)\s+(the\s+)?dose\b", re.I),
     "dose modification instruction"),
    (re.compile(r"\b(stop|discontinue|cease)\s+(taking\s+)?(the\s+)?(medication|drug|treatment|study\s+drug)\b", re.I),
     "medication discontinuation instruction"),
    (re.compile(r"\b(continue|resume)\s+(taking\s+)?(the\s+)?(medication|drug|treatment)\b", re.I),
     "medication continuation directive"),
    (re.compile(r"\b(diagnos(e|is|ed))\b|\byou\s+have\s+\w+\s+(disease|disorder|condition|syndrome)\b", re.I),
     "potential diagnosis"),
    (re.compile(r"\bprescribe\b", re.I),
     "prescription instruction"),
    (re.compile(r"\b(directly\s+)?(caused?|causing|causes?)\s+(the\s+)?(nausea|headache|fatigue|pain|symptom)\b", re.I),
     "unsupported causal claim"),
    (re.compile(r"\bguarantee(d|s)?\b", re.I),
     "outcome guarantee"),
]

_SAFE_ACTION = (
    "Review the participant's current concern and available historical records "
    "with the appropriate clinical team and follow the applicable trial/site procedures."
)

_SAFETY_NOTE = (
    "This system does not diagnose or prescribe treatment. "
    "Prototype for hackathon demonstration using synthetic data. "
    "Not for clinical use or medical decision-making."
)

_URGENT_NOTICE = (
    "⚠ POTENTIAL URGENT SAFETY CONCERN DETECTED. "
    "Follow the applicable trial/site emergency or escalation procedure "
    "and involve the appropriate clinical personnel immediately. "
    "Do not delay in contacting the relevant medical team."
)


def is_urgent(text: str) -> bool:
    """Return True if the check-in text contains urgent safety language."""
    return any(p.search(text) for p in _URGENT_PATTERNS)


def validate_output(brief: CoordinatorBrief) -> CoordinatorBrief:
    """
    Scan all text fields in *brief* for prohibited patterns.

    Any field containing a prohibited pattern is replaced with a safe
    fallback.  The ``safety_note`` is always enforced regardless.

    Parameters
    ----------
    brief : CoordinatorBrief produced by the agent LLM.

    Returns
    -------
    CoordinatorBrief  — sanitised copy (the original is not mutated).
    """
    data = brief.model_dump()
    violations: list[str] = []

    text_fields = [
        "current_issue", "participant_concern", "historical_pattern",
        "previous_outcome", "recommended_coordinator_action",
    ]

    for field in text_fields:
        value = data.get(field, "") or ""
        for pattern, label in _PROHIBITED_OUTPUT:
            if pattern.search(value):
                logger.warning(
                    "Safety violation in field '%s': %s — replaced with safe fallback.",
                    field, label,
                )
                violations.append(f"{field}: {label}")
                if field == "recommended_coordinator_action":
                    data[field] = _SAFE_ACTION
                else:
                    data[field] = f"[Redacted — {label} not permitted in this output.]"
                break  # one violation per field is enough to replace it

    # Also scan historical_matches
    clean_matches = []
    for match in data.get("historical_matches", []):
        match_text = " ".join(str(v) for v in match.values())
        flagged = False
        for pattern, label in _PROHIBITED_OUTPUT:
            if pattern.search(match_text):
                logger.warning("Safety violation in historical_match: %s", label)
                violations.append(f"historical_match: {label}")
                flagged = True
                break
        if not flagged:
            clean_matches.append(match)
    data["historical_matches"] = clean_matches

    # Always enforce the safety note
    data["safety_note"] = _SAFETY_NOTE

    if violations:
        logger.warning("Safety validator removed %d violation(s): %s", len(violations), violations)

    return CoordinatorBrief(**data)


def make_urgent_brief(checkin_text: str) -> CoordinatorBrief:
    """
    Create an emergency CoordinatorBrief when urgent language is detected.
    The agent LLM is bypassed entirely.
    """
    return CoordinatorBrief(
        current_issue=checkin_text[:300],
        participant_concern=_URGENT_NOTICE,
        historical_matches=[],
        historical_pattern="Not assessed — urgent safety concern detected.",
        previous_outcome="Not assessed — urgent safety concern detected.",
        recommended_coordinator_action=_URGENT_NOTICE,
        safety_note=_SAFETY_NOTE,
        memory_used=False,
        memories_count=0,
    )


__all__ = ["is_urgent", "validate_output", "make_urgent_brief"]
