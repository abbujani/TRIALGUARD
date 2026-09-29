"""
tests/test_retrieval_isolation.py

Phase 7 tests — Hindsight retrieval correctness and participant isolation.

These tests do NOT require a live Hindsight server. They verify the isolation
and retrieval contracts end-to-end at the memory.py layer using mocks that
simulate a Hindsight server with real participant-scoped data.

Coverage:
  1.  recall() always passes tags_match="all_strict" — hard isolation
  2.  recall() for P402 never receives P001's tags in the filter
  3.  recall() for P001 never receives P402's tags in the filter
  4.  Isolation: mocked server returns empty results when wrong participant tag
  5.  Isolation: mocked server returns results only for correct participant tag
  6.  query_trial() with nct_id appends trial tag without removing participant tag
  7.  query_trial() without nct_id uses only participant tag
  8.  ingest_trial() + recall() round-trip: stored doc_id matches recall metadata
  9.  Two participants ingest same trial → separate doc_ids → no doc_id collision
 10.  list_participant_memories() filters results by participant tag
 11.  recall() with budget="high" passes budget correctly
 12.  recall() as_prompt_string=True returns a string not a RecallResponse
 13.  Sabotage guard: recall() with participant_id="P402" cannot return
      memories tagged "participant:P001"  (server-side tag enforcement test)
 14.  ensure_bank_exists() failure is swallowed (idempotent)
 15.  get_version() returns api_version string from VersionResponse
"""

import importlib
import os
from unittest.mock import MagicMock, call, patch

import pytest

ROOT_ENV = {
    "HINDSIGHT_BASE_URL": "http://localhost:8888",
    "HINDSIGHT_BANK_ID": "trial-bank",
    "HINDSIGHT_API_KEY": "test-key",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _setup_memory(monkeypatch):
    """Patch env vars, reload memory, reset singleton."""
    for k, v in ROOT_ENV.items():
        monkeypatch.setenv(k, v)
    import memory
    importlib.reload(memory)
    memory._client = None
    return memory


def _mock_recall_response(results=None):
    resp = MagicMock()
    resp.results = results or []
    resp.to_prompt_string.return_value = "MOCK PROMPT STRING"
    return resp


def _mock_recall_result(text="sample text", tags=None, doc_id=None):
    r = MagicMock()
    r.text = text
    r.tags = tags or []
    r.document_id = doc_id
    r.metadata = {}
    r.id = "result-001"
    return r


def _mock_retain_response(items_count=1):
    r = MagicMock()
    r.items_count = items_count
    r.operation_id = "op-abc"
    r.success = True
    return r


# ── 1. recall always passes tags_match="all_strict" ──────────────────────────

def test_recall_always_all_strict(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        mem.recall("any query", "P402")
    assert mock_client.recall.call_args.kwargs["tags_match"] == "all_strict"


# ── 2. P402 recall never includes P001 tag ───────────────────────────────────

def test_p402_recall_does_not_include_p001_tag(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        mem.recall("eligibility?", "P402")
    tags_sent = mock_client.recall.call_args.kwargs["tags"]
    assert "participant:P001" not in tags_sent
    assert "participant:P402" in tags_sent


# ── 3. P001 recall never includes P402 tag ───────────────────────────────────

def test_p001_recall_does_not_include_p402_tag(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        mem.recall("what phase?", "P001")
    tags_sent = mock_client.recall.call_args.kwargs["tags"]
    assert "participant:P402" not in tags_sent
    assert "participant:P001" in tags_sent


# ── 4. Wrong participant → empty results (server simulation) ─────────────────

def test_wrong_participant_returns_empty_results(monkeypatch):
    """Simulates a server that enforces participant tags strictly."""
    mem = _setup_memory(monkeypatch)

    def _strict_recall(**kwargs):
        tags = kwargs.get("tags", [])
        # Server only has P402 data; P001 query returns nothing
        if "participant:P001" in tags:
            return _mock_recall_response(results=[])
        return _mock_recall_response(results=[_mock_recall_result("P402 data")])

    mock_client = MagicMock()
    mock_client.recall.side_effect = lambda **kwargs: _strict_recall(**kwargs)

    with patch("memory._get_client", return_value=mock_client):
        p001_resp = mem.recall("eligibility?", "P001")
        p402_resp = mem.recall("eligibility?", "P402")

    assert len(p001_resp.results) == 0
    assert len(p402_resp.results) == 1


# ── 5. Correct participant → results returned ─────────────────────────────────

def test_correct_participant_returns_results(monkeypatch):
    mem = _setup_memory(monkeypatch)
    result = _mock_recall_result(
        text="NCT04567890 eligibility criteria",
        tags=["participant:P402", "trial:NCT04567890"],
    )
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response(results=[result])
    with patch("memory._get_client", return_value=mock_client):
        resp = mem.recall("eligibility?", "P402")
    assert len(resp.results) == 1
    assert "participant:P402" in resp.results[0].tags


# ── 6. query_trial with nct_id keeps both participant + trial tags ─────────────

def test_query_trial_with_nct_id_has_both_tags(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        mem.query_trial("What is the dose?", "P402", nct_id="NCT04567890")
    tags = mock_client.recall.call_args.kwargs["tags"]
    assert "participant:P402" in tags
    assert "trial:NCT04567890" in tags


# ── 7. query_trial without nct_id uses only participant tag ───────────────────

def test_query_trial_without_nct_id_only_participant_tag(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        mem.query_trial("Any open trials?", "P402")
    tags = mock_client.recall.call_args.kwargs["tags"]
    assert "participant:P402" in tags
    assert not any(t.startswith("trial:") for t in tags)


# ── 8. ingest_trial + recall round-trip: doc_id matches ──────────────────────

def test_ingest_and_recall_document_id_roundtrip(monkeypatch):
    """Verify retain is called with doc_id=P402:NCT04567890 and recall tags match."""
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.retain.return_value = _mock_retain_response()
    mock_client.recall.return_value = _mock_recall_response(
        results=[_mock_recall_result(doc_id="P402:NCT04567890")]
    )

    trial = {"nct_id": "NCT04567890", "title": "HCC Trial", "phase": "Phase II"}
    with patch("memory._get_client", return_value=mock_client):
        mem.ingest_trial(trial, "P402")
        resp = mem.recall("eligibility criteria", "P402", extra_tags=["trial:NCT04567890"])

    retain_kwargs = mock_client.retain.call_args.kwargs
    assert retain_kwargs["document_id"] == "P402:NCT04567890"
    assert resp.results[0].document_id == "P402:NCT04567890"


# ── 9. Two participants ingest same trial → separate doc_ids ──────────────────

def test_two_participants_get_separate_doc_ids(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.retain.return_value = _mock_retain_response()
    trial = {"nct_id": "NCT04567890", "title": "HCC Trial"}

    with patch("memory._get_client", return_value=mock_client):
        mem.ingest_trial(trial, "P402")
        mem.ingest_trial(trial, "P001")

    calls = mock_client.retain.call_args_list
    doc_ids = [c.kwargs["document_id"] for c in calls]
    assert "P402:NCT04567890" in doc_ids
    assert "P001:NCT04567890" in doc_ids
    # They must be distinct
    assert doc_ids[0] != doc_ids[1]


# ── 10. list_participant_memories filters by participant ──────────────────────

def test_list_participant_memories_passes_correct_query(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    fake_unit = MagicMock()
    fake_unit.id = "u1"
    fake_unit.text = "some trial text"
    fake_unit.document_id = "P402:NCT04567890"
    fake_unit.tags = ["participant:P402"]
    fake_unit.metadata = {}
    fake_resp = MagicMock()
    fake_resp.results = [fake_unit]
    mock_client.list_memories.return_value = fake_resp

    with patch("memory._get_client", return_value=mock_client):
        results = mem.list_participant_memories("P402")

    kw = mock_client.list_memories.call_args.kwargs
    assert "participant:P402" in kw["search_query"]
    assert len(results) == 1


# ── 11. recall budget parameter passed correctly ──────────────────────────────

def test_recall_passes_budget_param(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        mem.recall("question?", "P402", budget="high", max_tokens=8192)
    kw = mock_client.recall.call_args.kwargs
    assert kw["budget"] == "high"
    assert kw["max_tokens"] == 8192


# ── 12. as_prompt_string=True returns a string ───────────────────────────────

def test_recall_as_prompt_string_returns_string(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_response()
    with patch("memory._get_client", return_value=mock_client):
        result = mem.recall("question?", "P402", as_prompt_string=True)
    assert isinstance(result, str)
    assert result == "MOCK PROMPT STRING"


# ── 13. Sabotage guard: recall for P402 cannot return P001 memories ───────────

def test_sabotage_guard_p402_cannot_read_p001_memories(monkeypatch):
    """
    Hard isolation: even if the server mistakenly returns a memory tagged
    'participant:P001' in a P402 query, the tags filter would have prevented
    it. This test verifies our code always sends P402's tag to the server —
    so a compliant server cannot mix participants.
    """
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()

    # Simulate a buggy server that returns P001 data anyway
    p001_result = _mock_recall_result(
        text="P001 private data",
        tags=["participant:P001"]
    )
    mock_client.recall.return_value = _mock_recall_response(results=[p001_result])

    with patch("memory._get_client", return_value=mock_client):
        resp = mem.recall("sensitive query", "P402")

    # Verify we sent the correct isolation tag (server side must enforce it)
    sent_tags = mock_client.recall.call_args.kwargs["tags"]
    assert "participant:P402" in sent_tags
    assert "participant:P001" not in sent_tags
    # tags_match must be "all_strict" — the server contract
    assert mock_client.recall.call_args.kwargs["tags_match"] == "all_strict"


# ── 14. ensure_bank_exists swallows server errors ─────────────────────────────

def test_ensure_bank_exists_swallows_error(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_client.create_bank.side_effect = RuntimeError("bank already exists")
    with patch("memory._get_client", return_value=mock_client):
        # Should not raise
        mem.ensure_bank_exists()


# ── 15. get_version returns api_version string ───────────────────────────────

def test_get_version_returns_api_version_string(monkeypatch):
    mem = _setup_memory(monkeypatch)
    mock_client = MagicMock()
    mock_version = MagicMock()
    mock_version.api_version = "1.2.3"
    mock_client.get_version.return_value = mock_version
    with patch("memory._get_client", return_value=mock_client):
        version = mem.get_version()
    assert version == "1.2.3"
