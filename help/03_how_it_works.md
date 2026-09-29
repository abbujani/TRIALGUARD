# TrialGuard — How It Works (Technical Deep-Dive)

---

## The Problem Being Solved

Clinical trial coordinators interact with participants many times over months. A participant's Month 6 complaint (e.g. recurring nausea and withdrawal concern) only makes full sense when viewed against their Month 1 history (nausea after dosage increase, meal-timing intervention, improvement).

Without memory, an LLM sees only today's complaint.
With Hindsight, it sees the full longitudinal context.

---

## Architecture Overview

```
Coordinator submits check-in
         │
         ▼
    Flask Route (/analyze)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 SQLite    Hindsight
 (store)   (retain)
    │         │
    └────┬────┘
         │
         ▼
    Agent LLM Call 1
    (Tool-calling — Groq)
         │
         ▼ (tool call: recall_patient_history)
    Hindsight Recall
    (semantic + keyword + graph + temporal)
         │
         ▼
    Historical Memories
         │
         ▼
    Agent LLM Call 2
    (Structured JSON output — Groq)
         │
         ▼
    Safety Validator
    (deterministic rule-based)
         │
         ▼
    CoordinatorBrief (Pydantic)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 SQLite    Hindsight
 (save     (retain
  run)      outcome)
         │
         ▼
    Result Page (Flask)
```

---

## Component by Component

### Flask App (`app.py`)

The web layer. Eight routes handle the full lifecycle:

- `GET /` — dashboard with stats
- `GET /participants/<id>` — participant timeline
- `GET /participants/<id>/checkin` — check-in form
- `POST /participants/<id>/analyze` — **the core route** (full pipeline)
- `GET /runs/<run_id>` — result page
- `GET /runs/<run_id>/trace` — audit/memory trace
- `GET /api/stats` — JSON stats
- `GET /api/participants` — JSON participant list

**Security note:** The participant ID is taken from the URL path — never from form data. Even if a form field tries to inject a different participant ID, the backend ignores it.

---

### SQLite Layer (`db.py`)

Stores exact application records. Four tables:

| Table | Purpose |
|-------|---------|
| `participants` | id, display_name, trial_id, status |
| `checkins` | raw check-in text, timestamp, participant link |
| `outcomes` | documented outcomes per participant |
| `agent_runs` | full audit record — query, memories (JSON), brief (JSON) |

The SQLite DB is your **exact record**. Hindsight is your **agent memory**. They serve different purposes.

---

### Hindsight Memory Layer (`memory.py`)

Two layers:

**Layer 1 — Connection**
- `_get_client()` — lazy singleton Hindsight client
- `retain()` — store content with participant isolation tag
- `recall()` — semantic retrieval with `tags_match="all_strict"`
- `ensure_bank_exists()` — idempotent bank setup
- `get_version()` — health check

**Layer 2 — Domain**
- `ingest_trial()` / `ingest_trials()` — batch ingestion
- `query_trial()` — semantic Q&A
- `list_participant_memories()` — enumerate stored memories

**Participant isolation** is enforced at the tag level:
- Every retain: `tags=["participant:P402", "trial:TRIAL-001"]`
- Every recall: `tags=["participant:P402"], tags_match="all_strict"`

This means P402's memories are physically unreachable by a P117 query — the Hindsight server enforces it server-side.

---

### Agent (`agent.py`)

**Two-stage pipeline:**

**Stage 1 — Tool-calling LLM call**
The agent receives the current check-in text and has access to one tool: `recall_patient_history()`. It decides whether to call it. If it does, the tool call is executed with the **server-enforced participant ID** (the LLM's suggested participant ID is overridden — it cannot redirect a query to a different participant).

**Stage 2 — Structured output LLM call**
The retrieved memories and check-in are combined into a prompt. The LLM generates a JSON object matching the `CoordinatorBrief` schema — no free-text response, always structured.

**Baseline mode:**
A single LLM call with no memory context. Produces a competent but history-free response. Used for before/after comparison.

**Urgent bypass:**
If the check-in contains language like "chest pain", "can't breathe", or "emergency help", the LLM is bypassed entirely. An emergency notice is returned immediately.

---

### Models (`models.py`)

Pydantic v2 model for validated output:

```
CoordinatorBrief
├── current_issue          (str)
├── participant_concern    (str)
├── historical_matches     (list of HistoricalMatch)
│   ├── date
│   ├── event
│   └── relevance
├── historical_pattern     (str)
├── previous_outcome       (str)
├── recommended_coordinator_action (str)
├── safety_note            (str — always set)
├── memory_used            (bool)
└── memories_count         (int)
```

---

### Safety Validator (`safety.py`)

A deterministic rule-based layer that sits between the LLM and the UI.

**Two functions:**

`is_urgent(text)` — scans check-in text for emergency language patterns before the agent runs. If triggered, returns an emergency brief without any LLM call.

`validate_output(brief)` — scans every field of the CoordinatorBrief for prohibited patterns:
- Dosage modification instructions
- Prescription instructions
- Diagnosis claims
- Medication stop/continue directives
- Causal overclaims ("the dosage caused the nausea")
- Outcome guarantees

Any violation replaces the field with a safe fallback. The safety note is always enforced.

---

### Seed System

| Script | Purpose |
|--------|---------|
| `seed_demo.py` | Seeds participant check-in histories into **Hindsight** memory |
| `seed_db.py` | Seeds all 10 participants into **SQLite** for the web UI |
| `demo_p402.py` | Runs the live P402 demo from the terminal |

---

## The Hindsight Memory Lifecycle

```
1. RETAIN (on check-in submission)
   └─ check-in text → Hindsight bank
   └─ tags: participant:P402, trial:TRIAL-001
   └─ document_id: checkin:P402:<uuid>
   └─ metadata: participant_id, trial_id, event_type, occurred_at

2. RECALL (during agent Stage 1 tool call)
   └─ query: "Find previous nausea, dosage changes, interventions..."
   └─ tags: participant:P402, trial:TRIAL-001
   └─ tags_match: all_strict (hard isolation)
   └─ budget: mid
   └─ Returns: ranked memories with text, document_id, tags

3. RETAIN OUTCOME (after agent completes)
   └─ agent's brief summary → Hindsight bank
   └─ document_id: outcome:<run_id>
   └─ This means future check-ins can also retrieve previous analyses
```

---

## Data Flow for a Single Check-in

```
Input:  "Participant P402 reports severe nausea, considering withdrawal."
        participant_id = P402  (from URL, server-enforced)
        occurred_at = 2026-09-02

Step 1: Validate — text not empty, participant exists in DB
Step 2: Save checkin to SQLite  → checkin:P402:<uuid8>
Step 3: Retain in Hindsight     → tagged participant:P402, trial:TRIAL-001
Step 4: Agent Stage 1           → Groq decides to call recall_patient_history
Step 5: Hindsight Recall        → 32 memories retrieved for P402
Step 6: Agent Stage 2           → Groq generates CoordinatorBrief JSON
Step 7: Safety Validator        → scans all fields, replaces violations
Step 8: Save agent_run to DB    → stores query, memories (JSON), brief (JSON)
Step 9: Retain outcome          → brief summary stored back in Hindsight
Step 10: Redirect               → result page /runs/<run_id>
```

---

## Why Two Memory Stores?

| | SQLite | Hindsight |
|---|---|---|
| **What** | Exact records | Semantic memories |
| **How retrieved** | SQL queries (exact) | Semantic search (fuzzy) |
| **Purpose** | Audit trail, UI data | Agent historical context |
| **When** | Always | During agent reasoning |

SQLite tells you *what happened exactly*.
Hindsight tells the *agent what is relevant right now*.

---

## Groq Model Used

`openai/gpt-oss-120b` — the most capable chat model available on this account. Both tool-calling and structured JSON output are supported.

---

## Key Technical Decisions

1. **No vector database added** — Hindsight IS the memory layer. Adding another retrieval system would obscure Hindsight's role.
2. **Two-stage agent loop** — tool calling and structured output cannot be combined in one Groq call, so they are deliberately separated.
3. **Participant ID enforced server-side** — the LLM never controls which participant's memories are retrieved.
4. **Deterministic safety layer** — the validator uses regex rules, not another LLM call — it cannot be hallucinated out of existence.
5. **Outcome retained after each analysis** — the system learns. Future queries for P402 will also retrieve previous analyses.
