"""tests/test_models_safety.py — Phases 10, 11: Pydantic models + safety validator."""
import pytest
from models import CoordinatorBrief, HistoricalMatch
from safety import is_urgent, validate_output, make_urgent_brief

# ── Models ────────────────────────────────────────────────────────────────────

def _make_brief(**kwargs):
    defaults = dict(
        current_issue="Participant reports nausea.",
        participant_concern="Participant is frustrated.",
        historical_matches=[],
        historical_pattern="No pattern.",
        previous_outcome="No outcome.",
        recommended_coordinator_action="Review with clinical team.",
    )
    defaults.update(kwargs)
    return CoordinatorBrief(**defaults)

def test_coordinator_brief_valid():
    b = _make_brief()
    assert b.current_issue == "Participant reports nausea."
    assert b.memory_used is False
    assert "Not for clinical use" in b.safety_note

def test_coordinator_brief_has_safety_note():
    b = _make_brief()
    assert b.safety_note != ""

def test_historical_match_fields():
    m = HistoricalMatch(date="Month 1", event="Nausea after dosage", relevance="Same symptom")
    assert m.date == "Month 1"

def test_brief_model_dump():
    b = _make_brief(memory_used=True, memories_count=3)
    d = b.model_dump()
    assert d["memory_used"] is True
    assert d["memories_count"] == 3

# ── is_urgent ─────────────────────────────────────────────────────────────────

def test_urgent_chest_pain():
    assert is_urgent("I have severe chest pain right now")

def test_urgent_cant_breathe():
    assert is_urgent("I can't breathe")

def test_urgent_collapse():
    assert is_urgent("I feel like I may collapse")

def test_urgent_suicidal():
    assert is_urgent("I am having suicidal thoughts")

def test_not_urgent_nausea():
    assert not is_urgent("Participant reports moderate nausea.")

def test_not_urgent_headache():
    assert not is_urgent("Mild headache after dosage increase.")

# ── validate_output ───────────────────────────────────────────────────────────

def test_validate_output_clean_passes():
    b = _make_brief()
    result = validate_output(b)
    assert result.recommended_coordinator_action == "Review with clinical team."

def test_validate_output_blocks_dosage_change():
    b = _make_brief(recommended_coordinator_action="You should increase the dosage now.")
    result = validate_output(b)
    assert "increase" not in result.recommended_coordinator_action.lower() or \
           "dosage" not in result.recommended_coordinator_action.lower()

def test_validate_output_blocks_diagnosis():
    b = _make_brief(current_issue="Diagnose the participant with condition X.")
    result = validate_output(b)
    assert "[Redacted" in result.current_issue

def test_validate_output_blocks_stop_medication():
    b = _make_brief(recommended_coordinator_action="Tell participant to stop medication immediately.")
    result = validate_output(b)
    assert result.recommended_coordinator_action != "Tell participant to stop medication immediately."

def test_validate_output_always_sets_safety_note():
    b = _make_brief()
    b2 = validate_output(b)
    assert "Not for clinical use" in b2.safety_note

def test_validate_output_blocks_causal_claim():
    b = _make_brief(historical_pattern="The dosage caused the nausea.")
    result = validate_output(b)
    assert "[Redacted" in result.historical_pattern

def test_validate_cleans_historical_matches():
    b = _make_brief(historical_matches=[
        {"date": "Month 1", "event": "prescribe drug X", "relevance": "relevant"},
        {"date": "Month 2", "event": "Normal check-in",  "relevance": "stable"},
    ])
    result = validate_output(b)
    # The prescribe match should be removed; historical_matches are HistoricalMatch objects
    texts = [m.event if hasattr(m, "event") else m["event"] for m in result.historical_matches]
    assert not any("prescribe" in t.lower() for t in texts)
    assert any("Normal" in t for t in texts)

# ── make_urgent_brief ─────────────────────────────────────────────────────────

def test_make_urgent_brief_contains_urgent_notice():
    b = make_urgent_brief("I can't breathe and I need emergency help.")
    assert "URGENT" in b.recommended_coordinator_action
    assert b.memory_used is False
    assert b.memories_count == 0

def test_make_urgent_brief_bypasses_history():
    b = make_urgent_brief("Chest pain.")
    assert b.historical_matches == []
