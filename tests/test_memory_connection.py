"""
tests/test_memory_connection.py

Phase 4 tests — Hindsight connection layer (memory.py).

These tests do NOT require a live Hindsight server.  They verify:
  1. The module imports without errors.
  2. Missing env vars raise EnvironmentError with helpful messages.
  3. retain() and recall() reject empty inputs.
  4. The Hindsight client is constructed with the correct parameters
     when valid env vars are present (client call is mocked).
  5. Participant isolation tags are applied correctly.
"""

import importlib
import os
from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fresh_memory(env: dict):
    """Re-import memory.py with a clean singleton inside a patched env."""
    with patch.dict(os.environ, env, clear=False):
        import memory
        importlib.reload(memory)
        # Reset the module-level singleton so the patched env is used
        memory._client = None
        return memory


# ── 1. Module import ──────────────────────────────────────────────────────────

def test_module_imports():
    import memory  # noqa: F401  — should not raise


# ── 2. Missing env vars ───────────────────────────────────────────────────────

def test_missing_base_url_raises(monkeypatch):
    monkeypatch.delenv("HINDSIGHT_BASE_URL", raising=False)
    monkeypatch.delenv("HINDSIGHT_API_KEY", raising=False)
    import memory
    importlib.reload(memory)
    memory._client = None
    with pytest.raises(EnvironmentError, match="HINDSIGHT_BASE_URL"):
        memory.get_version()


def test_missing_bank_id_raises(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.delenv("HINDSIGHT_BANK_ID", raising=False)
    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    with patch("memory._get_client", return_value=mock_client):
        with pytest.raises(EnvironmentError, match="HINDSIGHT_BANK_ID"):
            memory.retain("some content", "P001")


# ── 3. Input validation ───────────────────────────────────────────────────────

def test_retain_rejects_empty_content(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "test-bank")
    import memory
    importlib.reload(memory)
    memory._client = None
    with pytest.raises(ValueError, match="content"):
        memory.retain("", "P001")


def test_retain_rejects_empty_participant(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "test-bank")
    import memory
    importlib.reload(memory)
    memory._client = None
    with pytest.raises(ValueError, match="participant_id"):
        memory.retain("Some content", "")


def test_recall_rejects_empty_query(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "test-bank")
    import memory
    importlib.reload(memory)
    memory._client = None
    with pytest.raises(ValueError, match="query"):
        memory.recall("", "P001")


def test_recall_rejects_empty_participant(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "test-bank")
    import memory
    importlib.reload(memory)
    memory._client = None
    with pytest.raises(ValueError, match="participant_id"):
        memory.recall("Am I eligible?", "")


# ── 4. Client construction ────────────────────────────────────────────────────

def test_client_constructed_with_correct_params(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:9999")
    monkeypatch.setenv("HINDSIGHT_API_KEY", "test-key-abc")

    import memory
    importlib.reload(memory)
    memory._client = None

    with patch("memory.Hindsight") as MockHindsight:
        MockHindsight.return_value = MagicMock()
        memory._get_client()
        MockHindsight.assert_called_once_with(
            base_url="http://localhost:9999",
            api_key="test-key-abc",
        )


def test_client_singleton_reused(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_API_KEY", "key")

    import memory
    importlib.reload(memory)
    memory._client = None

    with patch("memory.Hindsight") as MockHindsight:
        MockHindsight.return_value = MagicMock()
        c1 = memory._get_client()
        c2 = memory._get_client()
        assert c1 is c2
        assert MockHindsight.call_count == 1


# ── 5. Participant isolation tags ─────────────────────────────────────────────

def test_retain_passes_participant_tag(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")

    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_retain_resp = MagicMock()
    mock_retain_resp.items_count = 1
    mock_client.retain.return_value = mock_retain_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.retain("Trial content", "P402", document_id="doc-1")

    call_kwargs = mock_client.retain.call_args.kwargs
    assert "participant:P402" in call_kwargs["tags"]
    assert call_kwargs["bank_id"] == "trial-bank"
    assert call_kwargs["document_id"] == "doc-1"


def test_recall_uses_all_strict_isolation(monkeypatch):
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
        memory.recall("What are the eligibility criteria?", "P402")

    call_kwargs = mock_client.recall.call_args.kwargs
    assert "participant:P402" in call_kwargs["tags"]
    assert call_kwargs["tags_match"] == "all_strict"


def test_retain_extra_tags_merged(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "trial-bank")

    import memory
    importlib.reload(memory)
    memory._client = None

    mock_client = MagicMock()
    mock_retain_resp = MagicMock()
    mock_retain_resp.items_count = 1
    mock_client.retain.return_value = mock_retain_resp

    with patch("memory._get_client", return_value=mock_client):
        memory.retain("Some data", "P402", extra_tags=["trial:NCT001", "phase:II"])

    tags_sent = mock_client.retain.call_args.kwargs["tags"]
    assert "participant:P402" in tags_sent
    assert "trial:NCT001" in tags_sent
    assert "phase:II" in tags_sent
