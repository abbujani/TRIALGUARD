"""
agent.py — Core agent logic for TrialGuard.

Blueprint Sections 22–28:
  Two-stage agentic loop:
    Stage 1 — Tool-calling LLM call: agent decides whether to recall history.
    Stage 2 — Structured output LLM call: generates CoordinatorBrief JSON.

  Baseline mode (Section 29):
    mode="baseline"  → Stage 1 only, no Hindsight recall, no memory context.
    mode="hindsight" → Full two-stage loop with memory retrieval.

  Safety layer (Section 45):
    is_urgent()     → fast-path bypass before any LLM call.
    validate_output() → scrub prohibited patterns from Stage 2 output.

Blueprint Section 23 — participant ID enforcement:
    The tool call participant_id is ALWAYS overridden by the server-side
    participant_id from the Flask route. The LLM cannot redirect a query
    to a different participant.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

from dotenv import load_dotenv
from groq import Groq

import memory as mem
from models import CoordinatorBrief, HistoricalMatch
from safety import is_urgent, make_urgent_brief, validate_output

load_dotenv()
logger = logging.getLogger(__name__)

# ── Groq client ───────────────────────────────────────────────────────────────

_groq_client: Groq | None = None

def _groq() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is not set.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client

MODEL = "openai/gpt-oss-120b"

# ── System prompt (blueprint Section 24) ─────────────────────────────────────

SYSTEM_PROMPT = """\
You are TrialGuard, an AI support agent for clinical-trial coordinators.

Your task is to analyse participant check-ins and retrieve relevant historical \
context using the Hindsight memory tool.

You MUST:
1. Ground every historical claim in retrieved memory.
2. Prefer documented facts over assumptions.
3. Distinguish current information from historical information.
4. State when no relevant historical memory was found.
5. Identify recurring patterns only when the evidence supports them.
6. Never invent a historical event or outcome.
7. Never diagnose a participant.
8. Never independently prescribe treatment or change dosage.
9. Never state that one event caused another unless causality is explicitly documented \
   in the retrieved memory. Do NOT convert correlation into causation. (Section 25)
10. Surface relevant information for coordinator/clinical-team review.
11. Escalate urgent safety concerns according to the applicable trial/site protocol.
12. Use synthetic-demo framing where appropriate.

Your role is decision support, not clinical decision-making.

Prototype for hackathon demonstration using synthetic data. \
Not for clinical use or medical decision-making."""

# ── Tool definition (blueprint Section 23) ───────────────────────────────────

_RECALL_TOOL = {
    "type": "function",
    "function": {
        "name": "recall_patient_history",
        "description": (
            "Retrieve relevant historical interactions, interventions, symptoms, "
            "and outcomes from long-term memory for a specific participant. "
            "Call this whenever the current check-in may relate to prior events."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "participant_id": {
                    "type": "string",
                    "description": "The participant's ID (e.g. P402).",
                },
                "query": {
                    "type": "string",
                    "description": (
                        "A specific longitudinal question such as: "
                        "'Find previous nausea, dosage changes, interventions "
                        "and outcomes for this participant.'"
                    ),
                },
            },
            "required": ["participant_id", "query"],
        },
    },
}

# ── Recall tool executor ──────────────────────────────────────────────────────

def _execute_recall(
    participant_id: str,
    query: str,
    trial_id: str,
    occurred_at: str | None = None,
) -> tuple[str, list[dict]]:
    """
    Run the Hindsight recall and return (prompt_string, memories_list).

    The participant_id is ALWAYS the server-side enforced value — the LLM
    cannot redirect to a different participant (blueprint Section 23).
    """
    extra_tags = [f"trial:{trial_id}"] if trial_id else None
    try:
        resp = mem.recall(
            query=query,
            participant_id=participant_id,
            max_tokens=3000,
            budget="mid",
            extra_tags=extra_tags,
        )
        prompt_str = resp.to_prompt_string()
        memories = [
            {
                "text":        getattr(r, "text",        ""),
                "document_id": getattr(r, "document_id", ""),
                "tags":        getattr(r, "tags",        []),
                "metadata":    getattr(r, "metadata",    {}),
            }
            for r in resp.results
        ]
        logger.info("Hindsight recalled %d memories for %s", len(memories), participant_id)
        return prompt_str, memories
    except Exception as exc:
        logger.error("Hindsight recall failed: %s", exc)
        return "Historical memory service unavailable. No historical context was used.", []


# ── Stage 1 — Tool-calling LLM call ──────────────────────────────────────────

def _stage1_tool_call(
    checkin_text: str,
    participant_id: str,
    trial_id: str,
    occurred_at: str | None,
) -> tuple[str, list[dict], str | None]:
    """
    First LLM call: decide whether to recall history and execute the tool.

    Returns
    -------
    (memory_context_str, retrieved_memories, hindsight_query_used)
    """
    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": (
            f"Participant: {participant_id}  |  Trial: {trial_id}\n"
            f"Date: {occurred_at or 'unknown'}\n\n"
            f"Check-in:\n{checkin_text}"
        )},
    ]

    response = _groq().chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[_RECALL_TOOL],
        tool_choice="auto",
        temperature=0.1,
    )

    msg = response.choices[0].message

    # If no tool call was made, return empty context
    if not msg.tool_calls:
        logger.info("Agent decided no recall needed.")
        return "", [], None

    tool_call  = msg.tool_calls[0]
    args       = json.loads(tool_call.function.arguments)
    query_used = args.get("query", "")

    # ENFORCE server-side participant_id — ignore any LLM-supplied ID
    memory_str, memories = _execute_recall(
        participant_id=participant_id,   # server-enforced
        query=query_used,
        trial_id=trial_id,
        occurred_at=occurred_at,
    )
    return memory_str, memories, query_used


# ── Stage 2 — Structured output LLM call ─────────────────────────────────────

_BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "current_issue":                  {"type": "string"},
        "participant_concern":            {"type": "string"},
        "historical_matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date":      {"type": "string"},
                    "event":     {"type": "string"},
                    "relevance": {"type": "string"},
                },
                "required": ["date", "event", "relevance"],
                "additionalProperties": False,
            },
        },
        "historical_pattern":             {"type": "string"},
        "previous_outcome":               {"type": "string"},
        "recommended_coordinator_action": {"type": "string"},
    },
    "required": [
        "current_issue", "participant_concern", "historical_matches",
        "historical_pattern", "previous_outcome",
        "recommended_coordinator_action",
    ],
    "additionalProperties": False,
}


def _stage2_structured(
    checkin_text: str,
    participant_id: str,
    trial_id: str,
    occurred_at: str | None,
    memory_context: str,
) -> CoordinatorBrief:
    """Second LLM call: produce structured CoordinatorBrief JSON."""
    memory_section = (
        f"\n\nHINDSIGHT MEMORY CONTEXT\n{'─'*40}\n{memory_context}"
        if memory_context.strip()
        else "\n\nNo relevant historical memory was found for this participant."
    )

    user_msg = (
        f"Participant: {participant_id}  |  Trial: {trial_id}\n"
        f"Date: {occurred_at or 'unknown'}\n\n"
        f"Check-in:\n{checkin_text}"
        f"{memory_section}\n\n"
        "Generate a structured Coordinator Action Brief as a JSON object. "
        "Use only the retrieved memory — do not invent historical events. "
        "Do not diagnose, prescribe, or recommend dosage changes. "
        "Do not state causation unless it is explicitly documented in the memory."
    )

    response = _groq().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name":   "coordinator_brief",
                "strict": True,
                "schema": _BRIEF_SCHEMA,
            },
        },
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Stage 2 JSON decode failed; using fallback brief.")
        data = {
            "current_issue":                  checkin_text[:200],
            "participant_concern":            "Unable to parse agent output.",
            "historical_matches":             [],
            "historical_pattern":             "Agent output could not be parsed.",
            "previous_outcome":               "Not available.",
            "recommended_coordinator_action": (
                "Review the participant's concern with the appropriate clinical team."
            ),
        }

    return CoordinatorBrief(
        **data,
        memory_used=bool(memory_context.strip()),
        memories_count=len(data.get("historical_matches", [])),
    )


# ── Baseline stage (blueprint Section 29–30) ──────────────────────────────────

def _baseline(
    checkin_text: str,
    participant_id: str,
    trial_id: str,
    occurred_at: str | None,
) -> CoordinatorBrief:
    """
    Run the agent without Hindsight memory retrieval.

    The response should be competent but lacking historical context —
    this is the *before* side of the baseline vs Hindsight comparison.
    (Blueprint Section 30: do not manufacture an obviously stupid baseline.)
    """
    user_msg = (
        f"Participant: {participant_id}  |  Trial: {trial_id}\n"
        f"Date: {occurred_at or 'unknown'}\n\n"
        f"Check-in:\n{checkin_text}\n\n"
        "No historical memory is available. "
        "Generate a structured Coordinator Action Brief based only on the current check-in. "
        "Do not invent historical context. "
        "Do not diagnose, prescribe, or recommend dosage changes."
    )

    response = _groq().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name":   "coordinator_brief",
                "strict": True,
                "schema": _BRIEF_SCHEMA,
            },
        },
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "current_issue":                  checkin_text[:200],
            "participant_concern":            "Unable to parse agent output.",
            "historical_matches":             [],
            "historical_pattern":             "Not assessed — no memory available.",
            "previous_outcome":               "Not available.",
            "recommended_coordinator_action": (
                "Review the participant's concern with the appropriate clinical team."
            ),
        }

    return CoordinatorBrief(
        **data,
        memory_used=False,
        memories_count=0,
    )


# ── Public entry point ────────────────────────────────────────────────────────

def run_agent(
    checkin_text: str,
    participant_id: str,
    trial_id: str = "TRIAL-001",
    occurred_at: str | None = None,
    mode: str = "hindsight",
) -> dict[str, Any]:
    """
    Run the full TrialGuard agent pipeline for a single check-in.

    Parameters
    ----------
    checkin_text   : Raw check-in text submitted by the coordinator.
    participant_id : Server-side participant ID (cannot be overridden by LLM).
    trial_id       : Trial identifier, default "TRIAL-001".
    occurred_at    : ISO 8601 timestamp of the check-in event.
    mode           : "hindsight" (full pipeline) | "baseline" (no memory).

    Returns
    -------
    dict with keys:
      brief              — CoordinatorBrief as dict
      retrieved_memories — list of raw memory dicts (empty for baseline)
      hindsight_query    — the query sent to Hindsight (None for baseline)
      mode               — echoed mode string
    """
    if not checkin_text or not checkin_text.strip():
        raise ValueError("checkin_text must not be empty.")
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must not be empty.")

    # Fast-path: urgent language bypass (blueprint Section 44)
    if is_urgent(checkin_text):
        logger.warning("Urgent language detected for participant %s — bypassing LLM.", participant_id)
        brief = make_urgent_brief(checkin_text)
        return {
            "brief":               brief.model_dump(),
            "retrieved_memories":  [],
            "hindsight_query":     None,
            "mode":                "urgent",
        }

    try:
        if mode == "baseline":
            brief = _baseline(checkin_text, participant_id, trial_id, occurred_at)
            brief = validate_output(brief)
            return {
                "brief":               brief.model_dump(),
                "retrieved_memories":  [],
                "hindsight_query":     None,
                "mode":                "baseline",
            }

        # Hindsight mode: two-stage loop
        memory_str, memories, query_used = _stage1_tool_call(
            checkin_text, participant_id, trial_id, occurred_at
        )
        brief = _stage2_structured(
            checkin_text, participant_id, trial_id, occurred_at, memory_str
        )
        brief.memory_used    = bool(memories)
        brief.memories_count = len(memories)
        brief = validate_output(brief)

        return {
            "brief":               brief.model_dump(),
            "retrieved_memories":  memories,
            "hindsight_query":     query_used,
            "mode":                "hindsight",
        }

    except Exception as exc:
        logger.error("Agent pipeline failed: %s", exc)
        # Graceful degradation (blueprint Section 65)
        fallback = CoordinatorBrief(
            current_issue=checkin_text[:200],
            participant_concern="Agent analysis unavailable.",
            historical_matches=[],
            historical_pattern="Not available — agent error.",
            previous_outcome="Not available.",
            recommended_coordinator_action=(
                "Review the participant's concern with the appropriate clinical team."
            ),
            memory_used=False,
            memories_count=0,
        )
        return {
            "brief":               fallback.model_dump(),
            "retrieved_memories":  [],
            "hindsight_query":     None,
            "mode":                mode,
            "error":               str(exc),
        }


__all__ = ["run_agent"]
