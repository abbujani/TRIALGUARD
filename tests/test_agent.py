"""tests/test_agent.py — Phases 9, 12: agent pipeline (mocked Groq + Hindsight)."""
import json, os, importlib
from unittest.mock import MagicMock, patch
import pytest

ENV = {
    "GROQ_API_KEY":        "test-groq-key",
    "HINDSIGHT_BASE_URL":  "http://localhost:8888",
    "HINDSIGHT_BANK_ID":   "trial-bank",
    "HINDSIGHT_API_KEY":   "test-hs-key",
}

VALID_BRIEF_JSON = json.dumps({
    "current_issue":                  "Participant reports nausea.",
    "participant_concern":            "Participant considering withdrawal.",
    "historical_matches":             [
        {"date": "Month 1", "event": "Nausea after dosage increase", "relevance": "Same symptom"}
    ],
    "historical_pattern":             "Recurring nausea following dosage escalation.",
    "previous_outcome":               "Symptoms improved after meal-timing intervention.",
    "recommended_coordinator_action": "Review with clinical team.",
})


def _mock_groq_tool_call(query="previous nausea"):
    """Return a mock Groq response that triggers the recall tool."""
    tool_call = MagicMock()
    tool_call.function.name      = "recall_patient_history"
    tool_call.function.arguments = json.dumps({"participant_id": "P402", "query": query})
    msg = MagicMock(); msg.tool_calls = [tool_call]
    choice = MagicMock(); choice.message = msg
    resp   = MagicMock(); resp.choices   = [choice]
    return resp


def _mock_groq_no_tool():
    """Return a mock Groq response with no tool call."""
    msg  = MagicMock(); msg.tool_calls = []
    choice = MagicMock(); choice.message = msg
    resp   = MagicMock(); resp.choices   = [choice]
    return resp


def _mock_groq_structured():
    """Return a mock Groq structured output response."""
    msg  = MagicMock(); msg.content = VALID_BRIEF_JSON
    choice = MagicMock(); choice.message = msg
    resp   = MagicMock(); resp.choices   = [choice]
    return resp


def _mock_recall_resp():
    result = MagicMock()
    result.text        = "Month 1: nausea after dosage increase. Improved after intervention."
    result.document_id = "checkin:P402:001"
    result.tags        = ["participant:P402", "trial:TRIAL-001"]
    result.metadata    = {"event_type": "symptom_report"}
    resp = MagicMock(); resp.results = [result]
    resp.to_prompt_string.return_value = "Month 1: nausea after dosage increase."
    return resp


# ── Hindsight mode ────────────────────────────────────────────────────────────

def test_run_agent_hindsight_mode(monkeypatch):
    for k, v in ENV.items(): monkeypatch.setenv(k, v)
    import memory; importlib.reload(memory); memory._client = None
    import agent;  importlib.reload(agent);  agent._groq_client = None

    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_resp()

    with patch("memory._get_client", return_value=mock_client), \
         patch("agent._groq") as mock_groq_fn:
        mock_groq_inst = MagicMock()
        mock_groq_fn.return_value = mock_groq_inst
        mock_groq_inst.chat.completions.create.side_effect = [
            _mock_groq_tool_call(),
            _mock_groq_structured(),
        ]
        result = agent.run_agent("Severe nausea again.", "P402", mode="hindsight")

    assert result["mode"] == "hindsight"
    assert "brief" in result
    assert result["brief"]["current_issue"] == "Participant reports nausea."
    assert result["brief"]["memory_used"] is True


def test_run_agent_hindsight_no_tool_call(monkeypatch):
    for k, v in ENV.items(): monkeypatch.setenv(k, v)
    import memory; importlib.reload(memory); memory._client = None
    import agent;  importlib.reload(agent);  agent._groq_client = None

    with patch("memory._get_client", return_value=MagicMock()), \
         patch("agent._groq") as mock_groq_fn:
        mock_groq_inst = MagicMock()
        mock_groq_fn.return_value = mock_groq_inst
        mock_groq_inst.chat.completions.create.side_effect = [
            _mock_groq_no_tool(),
            _mock_groq_structured(),
        ]
        result = agent.run_agent("Routine check-in, all well.", "P402", mode="hindsight")

    assert result["hindsight_query"] is None
    assert result["retrieved_memories"] == []


# ── Baseline mode ─────────────────────────────────────────────────────────────

def test_run_agent_baseline_mode(monkeypatch):
    for k, v in ENV.items(): monkeypatch.setenv(k, v)
    import agent; importlib.reload(agent); agent._groq_client = None

    with patch("agent._groq") as mock_groq_fn:
        mock_groq_inst = MagicMock()
        mock_groq_fn.return_value = mock_groq_inst
        mock_groq_inst.chat.completions.create.return_value = _mock_groq_structured()
        result = agent.run_agent("Nausea again.", "P402", mode="baseline")

    assert result["mode"] == "baseline"
    assert result["retrieved_memories"] == []
    assert result["hindsight_query"] is None
    assert result["brief"]["memory_used"] is False


# ── Urgent bypass ─────────────────────────────────────────────────────────────

def test_run_agent_urgent_bypass(monkeypatch):
    for k, v in ENV.items(): monkeypatch.setenv(k, v)
    import agent; importlib.reload(agent); agent._groq_client = None

    with patch("agent._groq") as mock_groq_fn:
        mock_groq_fn.return_value = MagicMock()
        result = agent.run_agent("I have severe chest pain and can't breathe.", "P402")

    # Groq should NOT have been called
    assert result["mode"] == "urgent"
    assert "URGENT" in result["brief"]["recommended_coordinator_action"]
    mock_groq_fn.return_value.chat.completions.create.assert_not_called()


# ── Server-side participant_id enforcement ────────────────────────────────────

def test_participant_id_enforced_server_side(monkeypatch):
    """LLM tries to recall for P001 but server must use P402."""
    for k, v in ENV.items(): monkeypatch.setenv(k, v)
    import memory; importlib.reload(memory); memory._client = None
    import agent;  importlib.reload(agent);  agent._groq_client = None

    mock_client = MagicMock()
    mock_client.recall.return_value = _mock_recall_resp()

    # LLM tool call requests P001 — should be overridden to P402
    bad_tool_call = MagicMock()
    bad_tool_call.function.name      = "recall_patient_history"
    bad_tool_call.function.arguments = json.dumps({"participant_id": "P001", "query": "nausea"})
    msg    = MagicMock(); msg.tool_calls = [bad_tool_call]
    choice = MagicMock(); choice.message = msg
    stage1 = MagicMock(); stage1.choices = [choice]

    with patch("memory._get_client", return_value=mock_client), \
         patch("agent._groq") as mock_groq_fn:
        mock_groq_inst = MagicMock()
        mock_groq_fn.return_value = mock_groq_inst
        mock_groq_inst.chat.completions.create.side_effect = [stage1, _mock_groq_structured()]
        agent.run_agent("Nausea.", "P402", mode="hindsight")

    # Recall must have been called with P402, NOT P001
    recall_kwargs = mock_client.recall.call_args.kwargs
    assert "participant:P402" in recall_kwargs["tags"]
    assert "participant:P001" not in recall_kwargs["tags"]


# ── Input validation ──────────────────────────────────────────────────────────

def test_run_agent_empty_checkin_raises():
    import agent
    with pytest.raises(ValueError, match="checkin_text"):
        agent.run_agent("", "P402")

def test_run_agent_empty_participant_raises():
    import agent
    with pytest.raises(ValueError, match="participant_id"):
        agent.run_agent("Some text.", "")


# ── Graceful degradation ──────────────────────────────────────────────────────

def test_run_agent_groq_failure_returns_fallback(monkeypatch):
    for k, v in ENV.items(): monkeypatch.setenv(k, v)
    import agent; importlib.reload(agent); agent._groq_client = None

    with patch("agent._groq") as mock_groq_fn:
        mock_groq_inst = MagicMock()
        mock_groq_fn.return_value = mock_groq_inst
        mock_groq_inst.chat.completions.create.side_effect = RuntimeError("Groq down")
        result = agent.run_agent("Check-in text.", "P402", mode="baseline")

    assert "error" in result
    assert result["brief"]["memory_used"] is False
