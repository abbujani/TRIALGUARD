"""
tests/test_memory_domain.py

Phase 5 tests — Domain operations in memory.py.

Covers:
  1. _trial_to_text()  renders all fields correctly
  2. _trial_to_text()  handles missing / list fields gracefully
  3. _trial_metadata() extracts scalar fields only
  4. _trial_tags()     produces isolation + trial + phase tags
  5. ingest_trial()    passes correct content / metadata / tags to Hindsight
  6. ingest_trial()    uses nct_id as document_id for deduplication
  7. ingest_trial()    raises ValueError for empty trial or participant
  8. ingest_trials()   calls ingest_trial once per entry
  9. ingest_trials()   re-raises on individual failure
 10. query_trial()     delegates to recall() with correct args
 11. query_trial()     adds trial tag filter when nct_id supplied
 12. query_trial()     raises ValueError for empty question / participant
 13. list_participant_memories() maps response units to plain dicts
"""

import importlib
import os
from unittest.mock import MagicMock, call, patch

import pytest


# ── Fixture helpers ───────────────────────────────────────────────────────────

SAMPLE_TRIAL: dict = {
    "nct_id": "NCT04567890",
    "title": "A Study of Drug X in Adults With Condition Y",
    "phase": "Phase II",
    "status": "Recruiting",
    "sponsor": "Acme Pharma",
    "summary": "This study evaluates the safety and efficacy of Drug X.",
    "eligibility": "Adults aged 18–65; diagnosis of Condition Y.",
    "interventions": ["Drug X 100 mg oral once daily", "Placebo"],
    "conditions": ["Condition Y"],
    "locations": ["Boston, MA, USA", "London, UK"],
    "contacts": ["Dr. Jane Smith (jane@acme.com)"],
}

MINIMAL_TRIAL: dict = {"nct_id": "NCT00000001", "title": "Minimal Trial"}


def _fresh(env: dict):
    """Reload memory with a patched env and cleared singleton."""
    with patch.dict(os.environ, env, clear=False):
        import memory
        importlib.reload(memory)
        memory._client = None
        return memory


def _mock_client_for(memory_mod):
    """Attach a mock client and return it."""
    mock = MagicMock()
    memory_mod._client = mock
    return mock


# ── 1. _trial_to_text — full fields ──────────────────────────────────────────

def test_trial_to_text_contains_all_fields():
    import memory
    text = memory._trial_to_text(SAMPLE_TRIAL)
    assert "NCT04567890" in text
    assert "A Study of Drug X" in text
    assert "Phase II" in text
    assert "Recruiting" in text
    assert "Acme Pharma" in text
    assert "safety and efficacy" in text
    assert "Adults aged 18" in text
    assert "Drug X 100 mg" in text
    assert "Condition Y" in text
    assert "Boston" in text
    assert "Dr. Jane Smith" in text


# ── 2. _trial_to_text — missing / list fields ─────────────────────────────────

def test_trial_to_text_missing_fields_show_na():
    import memory
    text = memory._trial_to_text({})
    assert text.count("N/A") >= 5  # all fields absent → all N/A


def test_trial_to_text_empty_list_shows_na():
    import memory
    trial = {"interventions": [], "conditions": []}
    text = memory._trial_to_text(trial)
    # both list fields should render as N/A
    assert text.count("N/A") >= 2


def test_trial_to_text_list_fields_use_bullets():
    import memory
    text = memory._trial_to_text(SAMPLE_TRIAL)
    assert "• Drug X 100 mg" in text
    assert "• Placebo" in text
    assert "• Condition Y" in text


# ── 3. _trial_metadata ────────────────────────────────────────────────────────

def test_trial_metadata_extracts_scalar_fields():
    import memory
    meta = memory._trial_metadata(SAMPLE_TRIAL)
    assert meta["nct_id"] == "NCT04567890"
    assert meta["title"] == "A Study of Drug X in Adults With Condition Y"
    assert meta["phase"] == "Phase II"
    assert meta["status"] == "Recruiting"
    assert meta["sponsor"] == "Acme Pharma"
    # list fields must not appear
    assert "interventions" not in meta
    assert "conditions" not in meta


def test_trial_metadata_missing_fields_omitted():
    import memory
    meta = memory._trial_metadata({})
    assert meta == {}


# ── 4. _trial_tags ────────────────────────────────────────────────────────────

def test_trial_tags_always_has_participant_tag():
    import memory
    tags = memory._trial_tags(SAMPLE_TRIAL, "P402")
    assert "participant:P402" in tags


def test_trial_tags_includes_trial_tag():
    import memory
    tags = memory._trial_tags(SAMPLE_TRIAL, "P402")
    assert "trial:NCT04567890" in tags


def test_trial_tags_includes_phase_tag():
    import memory
    tags = memory._trial_tags(SAMPLE_TRIAL, "P402")
    assert "phase:phase_ii" in tags


def test_trial_tags_no_trial_tag_when_no_nct():
    import memory
    tags = memory._trial_tags({"title": "Some trial"}, "P001")
    assert "participant:P001" in tags
    assert not any(t.startswith("trial:") for t in tags)


# ── 5. ingest_trial — content / metadata / tags ───────────────────────────────

def test_ingest_trial_passes_correct_args(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.items_count = 3
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.ingest_trial(SAMPLE_TRIAL, "P402")

    kw = mock_client.retain.call_args.kwargs
    assert kw["bank_id"] == "trial-bank"
    assert "NCT04567890" in kw["content"]
    assert "Phase II" in kw["content"]
    assert "participant:P402" in kw["tags"]
    assert "trial:NCT04567890" in kw["tags"]
    assert kw["metadata"]["nct_id"] == "NCT04567890"


# ── 6. ingest_trial — document_id deduplication ───────────────────────────────

def test_ingest_trial_uses_nct_as_doc_id(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.items_count = 1
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.ingest_trial(SAMPLE_TRIAL, "P402")

    kw = mock_client.retain.call_args.kwargs
    assert kw["document_id"] == "P402:NCT04567890"


def test_ingest_trial_no_doc_id_when_no_nct(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.items_count = 1
    mock_client.retain.return_value = mock_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.ingest_trial({"title": "No NCT"}, "P001")

    kw = mock_client.retain.call_args.kwargs
    assert kw["document_id"] is None


# ── 7. ingest_trial — input validation ───────────────────────────────────────

def test_ingest_trial_rejects_empty_trial():
    import memory
    with pytest.raises(ValueError, match="trial dict"):
        memory.ingest_trial({}, "P001")


def test_ingest_trial_rejects_empty_participant():
    import memory
    with pytest.raises(ValueError, match="participant_id"):
        memory.ingest_trial(SAMPLE_TRIAL, "")


# ── 8. ingest_trials — calls ingest_trial per entry ──────────────────────────

def test_ingest_trials_calls_retain_for_each(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.items_count = 1
    mock_client.retain.return_value = mock_resp

    trials = [SAMPLE_TRIAL, MINIMAL_TRIAL]
    with patch("memory._get_client", return_value=mock_client):
        responses = memory.ingest_trials(trials, "P402")

    assert len(responses) == 2
    assert mock_client.retain.call_count == 2


def test_ingest_trials_rejects_empty_list():
    import memory
    with pytest.raises(ValueError, match="trials list"):
        memory.ingest_trials([], "P001")


# ── 9. ingest_trials — re-raises on failure ──────────────────────────────────

def test_ingest_trials_reraises_on_error(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_client.retain.side_effect = RuntimeError("network failure")

    with patch("memory._get_client", return_value=mock_client):
        with pytest.raises(RuntimeError, match="network failure"):
            memory.ingest_trials([SAMPLE_TRIAL], "P402")


# ── 10. query_trial — delegates to recall ────────────────────────────────────

def test_query_trial_calls_recall_correctly(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_recall_resp = MagicMock()
    mock_recall_resp.results = []
    mock_client.recall.return_value = mock_recall_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.query_trial("What are the eligibility criteria?", "P402")

    kw = mock_client.recall.call_args.kwargs
    assert kw["bank_id"] == "trial-bank"
    assert kw["query"] == "What are the eligibility criteria?"
    assert "participant:P402" in kw["tags"]
    assert kw["tags_match"] == "all_strict"


# ── 11. query_trial — adds trial tag when nct_id given ───────────────────────

def test_query_trial_adds_nct_tag(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_recall_resp = MagicMock()
    mock_recall_resp.results = []
    mock_client.recall.return_value = mock_recall_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.query_trial("What is the sponsor?", "P402", nct_id="NCT04567890")

    kw = mock_client.recall.call_args.kwargs
    assert "trial:NCT04567890" in kw["tags"]
    assert "participant:P402" in kw["tags"]


# ── 12. query_trial — input validation ───────────────────────────────────────

def test_query_trial_rejects_empty_question():
    import memory
    with pytest.raises(ValueError, match="question"):
        memory.query_trial("", "P001")


def test_query_trial_rejects_empty_participant():
    import memory
    with pytest.raises(ValueError, match="participant_id"):
        memory.query_trial("What is the phase?", "")


# ── 13. list_participant_memories ─────────────────────────────────────────────

def test_list_participant_memories_maps_to_dicts(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")
    import memory
    importlib.reload(memory)
    memory._client = None

    # Build a fake list_memories response
    fake_unit = MagicMock()
    fake_unit.id = "mem-001"
    fake_unit.text = "Drug X trial information " * 20  # long text
    fake_unit.document_id = "P402:NCT04567890"
    fake_unit.tags = ["participant:P402", "trial:NCT04567890"]
    fake_unit.metadata = {"nct_id": "NCT04567890"}

    fake_resp = MagicMock()
    fake_resp.results = [fake_unit]

    mock_client = MagicMock()
    mock_client.list_memories.return_value = fake_resp

    with patch("memory._get_client", return_value=mock_client):
        results = memory.list_participant_memories("P402")

    assert len(results) == 1
    r = results[0]
    assert r["id"] == "mem-001"
    assert len(r["text"]) <= 201  # truncated to 200 + ellipsis char
    assert r["document_id"] == "P402:NCT04567890"
    assert "participant:P402" in r["tags"]
    assert r["metadata"]["nct_id"] == "NCT04567890"


def test_list_participant_memories_rejects_empty_participant():
    import memory
    with pytest.raises(ValueError, match="participant_id"):
        memory.list_participant_memories("")
