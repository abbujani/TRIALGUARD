"""
models.py — Pydantic output models for TrialGuard.

Blueprint Section 26: The final LLM call generates a structured JSON object.
All agent output is validated against CoordinatorBrief before being stored
or returned to the UI.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class HistoricalMatch(BaseModel):
    """A single retrieved historical event relevant to the current check-in."""
    date:      str = Field(description="Approximate date or month label of the historical event.")
    event:     str = Field(description="Brief description of what happened.")
    relevance: str = Field(description="Why this event is relevant to the current issue.")


class CoordinatorBrief(BaseModel):
    """
    Structured output produced by the TrialGuard agent.

    Blueprint Section 26 schema — all fields map directly to the result
    page sections (Section 34).
    """
    current_issue: str = Field(
        description="The participant's current complaint or concern, as understood from the check-in."
    )
    participant_concern: str = Field(
        description="Any emotional or withdrawal concern expressed by the participant."
    )
    historical_matches: list[HistoricalMatch] = Field(
        default_factory=list,
        description="List of relevant historical events retrieved from Hindsight memory."
    )
    historical_pattern: str = Field(
        description=(
            "Description of any recurring pattern detected across historical events, "
            "or 'No relevant historical pattern identified.' if none found."
        )
    )
    previous_outcome: str = Field(
        description=(
            "What the historical record says happened last time a similar issue occurred, "
            "or 'No previous outcome documented.' if not found."
        )
    )
    recommended_coordinator_action: str = Field(
        description=(
            "Suggested next step for the coordinator — always framed as review/escalate, "
            "never as a clinical decision or prescription."
        )
    )
    safety_note: str = Field(
        default=(
            "This system does not diagnose or prescribe treatment. "
            "Prototype for hackathon demonstration using synthetic data. "
            "Not for clinical use or medical decision-making."
        ),
        description="Mandatory safety disclaimer appended to every output."
    )
    memory_used: bool = Field(
        default=False,
        description="True if Hindsight memory was successfully retrieved and used."
    )
    memories_count: int = Field(
        default=0,
        description="Number of historical memories retrieved from Hindsight."
    )

    model_config = {"extra": "ignore"}
