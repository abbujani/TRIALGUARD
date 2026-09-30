"""
memory.py — Hindsight client wrapper for TrialGuard.

Provides two layers:

Layer 1 — Connection (Phase 4)
    Low-level helpers: _get_client(), retain(), recall(), ensure_bank_exists(),
    get_version().  These talk directly to the Hindsight API with minimal
    transformation.

Layer 2 — Domain operations (Phase 5)
    Higher-level helpers that understand TrialGuard's data model:
    - ingest_trial()      store a structured clinical trial document
    - ingest_trials()     batch-ingest a list of trial dicts
    - query_trial()       semantic Q&A over a participant's trial memory
    - list_participant_memories()  enumerate stored memories for a participant

Participant isolation contract
──────────────────────────────
• Every retain call attaches the tag  "participant:<participant_id>"
• Every recall call filters with
      tags=["participant:<participant_id>"], tags_match="all_strict"
  so a participant can NEVER read memories stored for a different participant.

Environment variables consumed (via python-dotenv / os.environ):
  HINDSIGHT_BASE_URL   – e.g. http://localhost:8888
  HINDSIGHT_API_KEY    – Hindsight API key
  HINDSIGHT_BANK_ID    – memory bank scoping all trial data
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from hindsight_client import Hindsight
from hindsight_client import RecallResponse, RetainResponse, VersionResponse

load_dotenv()

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# LAYER 1 — CONNECTION  (Phase 4)
# ─────────────────────────────────────────────────────────────────────────────

_client: Hindsight | None = None


def _get_client() -> Hindsight:
    """Return (and lazily create) the shared Hindsight client instance."""
    global _client
    base_url = os.environ.get("HINDSIGHT_BASE_URL", "").strip()
    api_key  = os.environ.get("HINDSIGHT_API_KEY",  "").strip() or None
    if not base_url:
        raise EnvironmentError(
            "HINDSIGHT_BASE_URL is not set. "
            "Add it to your .env file or environment."
        )
    if _client is None:
        _client = Hindsight(base_url=base_url, api_key=api_key)
        logger.debug("Hindsight client initialised at %s", base_url)
    return _client


def _reset_client() -> None:
    """Force the Hindsight client singleton to be recreated on next call."""
    global _client
    _client = None


def _bank_id() -> str:
    """Return the configured bank ID, raising if missing."""
    bid = os.environ.get("HINDSIGHT_BANK_ID", "").strip()
    if not bid:
        raise EnvironmentError(
            "HINDSIGHT_BANK_ID is not set. "
            "Add it to your .env file or environment."
        )
    return bid


def _participant_tag(participant_id: str) -> str:
    """Return the canonical participant isolation tag."""
    return f"participant:{participant_id}"


def get_version() -> str:
    """
    Ping the Hindsight server and return its API version string.

    Returns
    -------
    str  — the ``api_version`` field from the server's VersionResponse.
    """
    try:
        resp: VersionResponse = _get_client().get_version()
        return resp.api_version
    except Exception:
        # Session may have expired — reset and retry once
        _reset_client()
        resp: VersionResponse = _get_client().get_version()
        return resp.api_version


def retain(
    content: str,
    participant_id: str,
    *,
    document_id: str | None = None,
    metadata: dict[str, str] | None = None,
    extra_tags: list[str] | None = None,
) -> RetainResponse:
    """
    Store *content* in the Hindsight memory bank, scoped to *participant_id*.

    Parameters
    ----------
    content       : Plain-text to store.
    participant_id: Isolation key — becomes tag ``"participant:<id>"``.
    document_id   : Deduplication key; re-retaining the same ID updates the memory.
    metadata      : Arbitrary ``str → str`` key/value pairs (e.g. trial_id, phase).
    extra_tags    : Additional tags beyond the participant isolation tag.

    Returns
    -------
    RetainResponse  (fields: success, bank_id, items_count, operation_id)
    """
    if not content or not content.strip():
        raise ValueError("content must be a non-empty string.")
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must be a non-empty string.")

    tags: list[str] = [_participant_tag(participant_id)]
    if extra_tags:
        tags.extend(extra_tags)

    try:
        resp: RetainResponse = _get_client().retain(
            bank_id=_bank_id(),
            content=content,
            document_id=document_id,
            metadata=metadata or {},
            tags=tags,
        )
    except Exception:
        _reset_client()
        resp: RetainResponse = _get_client().retain(
            bank_id=_bank_id(),
            content=content,
            document_id=document_id,
            metadata=metadata or {},
            tags=tags,
        )
    logger.debug(
        "retain ok | participant=%s | doc_id=%s | items=%d",
        participant_id,
        document_id,
        resp.items_count,
    )
    return resp


def recall(
    query: str,
    participant_id: str,
    *,
    max_tokens: int = 4096,
    budget: str = "mid",
    extra_tags: list[str] | None = None,
    as_prompt_string: bool = False,
) -> RecallResponse | str:
    """
    Semantically retrieve memories relevant to *query*, restricted to
    *participant_id* via hard tag isolation (``tags_match="all_strict"``).

    Parameters
    ----------
    query         : Natural-language question or search string.
    participant_id: Must match the ID used in :func:`retain`.
    max_tokens    : Upper bound on tokens returned.
    budget        : ``"low"`` | ``"mid"`` | ``"high"`` — controls Hindsight spend.
    extra_tags    : Additional tag filters to narrow results.
    as_prompt_string: If True, return ``RecallResponse.to_prompt_string()``
                      (ready-to-inject context string) instead of the raw object.

    Returns
    -------
    RecallResponse | str
    """
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string.")
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must be a non-empty string.")

    tags: list[str] = [_participant_tag(participant_id)]
    if extra_tags:
        tags.extend(extra_tags)

    try:
        resp: RecallResponse = _get_client().recall(
            bank_id=_bank_id(),
            query=query,
            tags=tags,
            tags_match="all_strict",  # hard isolation — no cross-participant leakage
            max_tokens=max_tokens,
            budget=budget,
        )
    except Exception:
        _reset_client()
        resp: RecallResponse = _get_client().recall(
            bank_id=_bank_id(),
            query=query,
            tags=tags,
            tags_match="all_strict",
            max_tokens=max_tokens,
            budget=budget,
        )
    logger.debug(
        "recall ok | participant=%s | results=%d",
        participant_id,
        len(resp.results),
    )
    if as_prompt_string:
        return resp.to_prompt_string()
    return resp


def ensure_bank_exists(
    name: str = "TrialGuard",
    mission: str = (
        "Store and retrieve longitudinal clinical trial participant check-in events, "
        "symptoms, interventions, dosage changes, and outcomes. "
        "Enable coordinators to retrieve relevant historical context for a participant "
        "to support decision-making during new check-ins."
    ),
) -> None:
    """
    Create the Hindsight memory bank if it does not already exist.

    Safe to call at startup — idempotent.
    """
    try:
        _get_client().create_bank(
            bank_id=_bank_id(),
            name=name,
            mission=mission,
        )
        logger.info("Memory bank '%s' ready.", _bank_id())
    except Exception as exc:  # noqa: BLE001
        logger.debug("ensure_bank_exists: %s (may be pre-existing)", exc)


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 2 — DOMAIN OPERATIONS  (Phase 5)
# ─────────────────────────────────────────────────────────────────────────────

# ── Trial document schema ─────────────────────────────────────────────────────
#
# A "trial dict" understood by TrialGuard has these optional keys:
#
#   nct_id         str   — ClinicalTrials.gov identifier  (e.g. "NCT04567890")
#   title          str   — official trial title
#   phase          str   — "Phase I" … "Phase IV" / "N/A"
#   status         str   — "Recruiting" | "Active, not recruiting" | …
#   sponsor        str   — lead sponsor name
#   summary        str   — brief summary / purpose
#   eligibility    str   — eligibility criteria (free text or structured)
#   interventions  list  — list of intervention description strings
#   conditions     list  — list of condition/disease strings
#   locations      list  — list of facility/city/country strings
#   contacts       list  — list of contact name/email strings
#
# Any key absent is simply omitted from the stored text; unknown keys are
# preserved verbatim so the function is forward-compatible.

_TRIAL_TEXT_TEMPLATE = """\
CLINICAL TRIAL RECORD
=====================
NCT ID        : {nct_id}
Title         : {title}
Phase         : {phase}
Status        : {status}
Sponsor       : {sponsor}

Summary
-------
{summary}

Eligibility Criteria
--------------------
{eligibility}

Interventions
-------------
{interventions}

Conditions / Diseases
---------------------
{conditions}

Locations
---------
{locations}

Contact Information
-------------------
{contacts}
"""


def _trial_to_text(trial: dict[str, Any]) -> str:
    """
    Render a trial dict into a plain-text document suitable for Hindsight.

    Missing fields are replaced with "N/A".  List fields are joined with
    newline bullets.
    """
    def _str(val: Any) -> str:
        if val is None:
            return "N/A"
        if isinstance(val, list):
            if not val:
                return "N/A"
            return "\n".join(f"• {item}" for item in val)
        return str(val).strip() or "N/A"

    return _TRIAL_TEXT_TEMPLATE.format(
        nct_id=_str(trial.get("nct_id")),
        title=_str(trial.get("title")),
        phase=_str(trial.get("phase")),
        status=_str(trial.get("status")),
        sponsor=_str(trial.get("sponsor")),
        summary=_str(trial.get("summary")),
        eligibility=_str(trial.get("eligibility")),
        interventions=_str(trial.get("interventions")),
        conditions=_str(trial.get("conditions")),
        locations=_str(trial.get("locations")),
        contacts=_str(trial.get("contacts")),
    )


def _trial_metadata(trial: dict[str, Any]) -> dict[str, str]:
    """
    Build a ``str → str`` metadata dict from a trial record.

    Only string-compatible scalar fields are included (Hindsight requires
    all metadata values to be strings).
    """
    meta: dict[str, str] = {}
    for key in ("nct_id", "title", "phase", "status", "sponsor"):
        val = trial.get(key)
        if val is not None:
            meta[key] = str(val)
    return meta


def _trial_tags(trial: dict[str, Any], participant_id: str) -> list[str]:
    """
    Build the full tag list for a trial memory unit.

    Always includes the participant isolation tag.  Adds ``trial:<nct_id>``
    and ``phase:<phase>`` when available so callers can filter by trial or
    phase without a semantic search.
    """
    tags = [_participant_tag(participant_id)]
    nct_id = trial.get("nct_id")
    if nct_id:
        tags.append(f"trial:{nct_id}")
    phase = trial.get("phase")
    if phase:
        # Normalise to lowercase slug, e.g. "Phase II" → "phase:phase_ii"
        tags.append(f"phase:{phase.lower().replace(' ', '_')}")
    return tags


# ── Public domain helpers ─────────────────────────────────────────────────────


def ingest_trial(
    trial: dict[str, Any],
    participant_id: str,
) -> RetainResponse:
    """
    Ingest a single clinical trial document into Hindsight for *participant_id*.

    The trial dict is rendered into a structured plain-text document, tagged
    with the participant isolation tag plus optional ``trial:<nct_id>`` and
    ``phase:<phase>`` tags for fast filtering.

    Parameters
    ----------
    trial:
        Dictionary with trial fields (see module-level schema comment).
        Must contain at least one non-empty field.
    participant_id:
        Server-side participant identifier.  All stored memories are scoped
        to this ID and cannot be retrieved by any other participant.

    Returns
    -------
    RetainResponse

    Raises
    ------
    ValueError
        If *trial* is empty or *participant_id* is empty.
    EnvironmentError
        If required environment variables are missing.
    """
    if not trial:
        raise ValueError("trial dict must not be empty.")
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must be a non-empty string.")

    text = _trial_to_text(trial)
    metadata = _trial_metadata(trial)
    tags = _trial_tags(trial, participant_id)

    # Use nct_id as document_id for deduplication when available
    nct_id = trial.get("nct_id")
    doc_id = f"{participant_id}:{nct_id}" if nct_id else None

    resp = _get_client().retain(
        bank_id=_bank_id(),
        content=text,
        document_id=doc_id,
        metadata=metadata,
        tags=tags,
    )
    logger.info(
        "ingest_trial ok | participant=%s | nct_id=%s | items=%d",
        participant_id,
        nct_id or "unknown",
        resp.items_count,
    )
    return resp


def ingest_trials(
    trials: list[dict[str, Any]],
    participant_id: str,
) -> list[RetainResponse]:
    """
    Batch-ingest a list of trial dicts for *participant_id*.

    Calls :func:`ingest_trial` for each entry, collecting responses.
    Errors on individual trials are logged and re-raised so the caller
    can decide whether to continue or abort.

    Parameters
    ----------
    trials        : Non-empty list of trial dicts.
    participant_id: Participant isolation key.

    Returns
    -------
    list[RetainResponse]  — one per trial, in input order.
    """
    if not trials:
        raise ValueError("trials list must not be empty.")
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must be a non-empty string.")

    responses: list[RetainResponse] = []
    for i, trial in enumerate(trials):
        try:
            resp = ingest_trial(trial, participant_id)
            responses.append(resp)
        except Exception as exc:
            nct = trial.get("nct_id", f"index {i}")
            logger.error("ingest_trials: failed on trial %s — %s", nct, exc)
            raise
    logger.info(
        "ingest_trials done | participant=%s | count=%d",
        participant_id,
        len(responses),
    )
    return responses


def query_trial(
    question: str,
    participant_id: str,
    *,
    nct_id: str | None = None,
    max_tokens: int = 4096,
    budget: str = "mid",
    as_prompt_string: bool = False,
) -> RecallResponse | str:
    """
    Answer a natural-language question about a participant's trial memories.

    Optionally narrows the search to a specific trial via ``nct_id``.

    Parameters
    ----------
    question      : User's question, e.g. "What are the eligibility criteria?".
    participant_id: Must match the ID used when ingesting trials.
    nct_id        : If supplied, adds a ``trial:<nct_id>`` tag filter so only
                    memories for that specific trial are returned.
    max_tokens    : Upper bound on tokens in the recall response.
    budget        : Hindsight retrieval budget — ``"low"`` | ``"mid"`` | ``"high"``.
    as_prompt_string: If True, return the recalled context as a ready-to-inject
                      string rather than the raw RecallResponse object.

    Returns
    -------
    RecallResponse | str

    Raises
    ------
    ValueError
        If *question* or *participant_id* are empty.
    """
    if not question or not question.strip():
        raise ValueError("question must be a non-empty string.")
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must be a non-empty string.")

    extra_tags: list[str] | None = None
    if nct_id:
        extra_tags = [f"trial:{nct_id}"]

    return recall(
        query=question,
        participant_id=participant_id,
        max_tokens=max_tokens,
        budget=budget,
        extra_tags=extra_tags,
        as_prompt_string=as_prompt_string,
    )


def list_participant_memories(
    participant_id: str,
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Return a summary list of all memories stored for *participant_id*.

    Each entry in the returned list is a plain dict with keys:
    ``id``, ``text`` (truncated), ``document_id``, ``tags``, ``metadata``.

    Parameters
    ----------
    participant_id: Participant whose memories to list.
    limit         : Maximum number of records to return (default 100).

    Returns
    -------
    list[dict]
    """
    if not participant_id or not participant_id.strip():
        raise ValueError("participant_id must be a non-empty string.")

    resp = _get_client().list_memories(
        bank_id=_bank_id(),
        search_query=f"participant:{participant_id}",
        limit=limit,
    )
    results = []
    for unit in getattr(resp, "results", []) or []:
        results.append({
            "id": getattr(unit, "id", None),
            "text": (getattr(unit, "text", "") or "")[:200] + "…",
            "document_id": getattr(unit, "document_id", None),
            "tags": getattr(unit, "tags", []),
            "metadata": getattr(unit, "metadata", {}),
        })
    return results


# ── Convenience re-exports ────────────────────────────────────────────────────
__all__ = [
    # Layer 1
    "ensure_bank_exists",
    "get_version",
    "recall",
    "retain",
    # Layer 2
    "ingest_trial",
    "ingest_trials",
    "query_trial",
    "list_participant_memories",
]
