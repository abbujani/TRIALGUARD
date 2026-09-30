# TrialGuard

> AI-powered clinical trial coordinator support, grounded in long-term memory via [Hindsight](https://hindsight.vectorize.io/).

**🚀 Live Demo → [https://trialguard-dun.vercel.app](https://trialguard-dun.vercel.app)**

> Prototype for demonstration using synthetic data. Not for clinical use or medical decision-making.

---

## The Problem

Clinical trial coordinators interact with participants many times over months. A Month 6 complaint — severe headache, frustration, considering withdrawal — only makes sense when viewed against the full longitudinal record: a dosage increase in Month 1, the same headache, hydration guidance that worked, and two more recurrences since.

Without memory, an LLM sees only today's complaint. It gives a reasonable, professional response — and misses everything that matters.

---

## The Solution

TrialGuard puts [Hindsight](https://hindsight.vectorize.io/) at the centre of the agent architecture. Every check-in is retained in long-term memory. When a new check-in arrives, the agent retrieves the participant's full longitudinal history — semantic, keyword, graph, and temporal retrieval combined — and generates a structured **Coordinator Action Brief** grounded in documented history, not inference.

**Before Hindsight:** `"No historical pattern identified."`
**With Hindsight:** `"Recurring headache consistently following each dosage escalation — now the fourth occurrence. Hydration guidance associated with partial improvement previously."`

Same AI. Same complaint. The only variable is memory.

---

## How Hindsight Is Used

Hindsight is not a feature — it is the architecture. Every part of the agent pipeline runs through it:

**1. Retain on every check-in**
```python
mem.retain(
    content=checkin_text,
    document_id=f"checkin:{participant_id}:{uid}",
    tags=["participant:P209", "trial:TRIAL-001"],
    metadata={"participant_id": "P209", "occurred_at": "2026-10-07T00:00:00Z"}
)
```

**2. Hard participant isolation on every recall**
```python
mem.recall(
    query="Find previous headache events, dosage changes, interventions and outcomes for participant P209.",
    tags=["participant:P209"],
    tags_match="all_strict"   # server-side enforcement — not a client filter
)
```
`tags_match="all_strict"` means cross-participant data leakage is physically impossible at the retrieval layer. P209's memories cannot appear in a P402 query — enforced by the Hindsight server, not application code. This is tested explicitly in `tests/test_retrieval_isolation.py`.

**3. Two-stage agent pipeline**

- **Stage 1 (tool-calling):** The LLM decides whether historical context is needed and invokes `recall_patient_history()` with a longitudinal query. The participant ID is always taken from the URL path — the LLM cannot redirect a recall to a different participant.
- **Stage 2 (structured output):** Retrieved memories are injected into a second LLM call that generates a validated `CoordinatorBrief` JSON object — never free text.

**4. Outcome retention — the learning loop**
```python
mem.retain(
    content=brief_summary,
    document_id=f"outcome:{run_id}",
    tags=["participant:P209", "trial:TRIAL-001"]
)
```
After every analysis, the agent's own output is retained back into Hindsight. Future queries for the same participant also retrieve previous analyses. The system becomes more useful with every interaction without any retraining.

**5. What Hindsight retrieves that a vector DB cannot**

Hindsight combines four retrieval strategies in a single call:
- **Semantic** — finds the March 15 headache episode even when the query says "head pain"
- **Keyword** — catches exact terms like "hydration" or "dosage escalation"
- **Graph** — links related events (dosage change → headache → intervention → outcome)
- **Temporal** — reasons about before/after relationships across months of history

In the P209 demo, a single recall call returns 27 memories spanning seven months — seeded history, live check-ins, and previous analysis outcomes — all ranked by relevance.

---

## Architecture

```
Coordinator submits check-in
         │
    Flask Route /participants/<id>/analyze
    (participant_id enforced from URL path — never from form data)
         │
    ┌────┴────┐
    │         │
 SQLite    Hindsight
 (record)  (retain check-in)
         │
    is_urgent() — fast-path bypass for emergency language
         │
    Agent Stage 1 — Tool-calling LLM (Groq)
    decides whether to call recall_patient_history()
         │
    Hindsight Recall
    tags_match="all_strict" — server-side participant isolation
    semantic + keyword + graph + temporal retrieval
         │
    Historical Memories (ranked, timestamped)
         │
    Agent Stage 2 — Structured output LLM (Groq)
    generates CoordinatorBrief JSON
         │
    Safety Validator — deterministic regex rules
    blocks: diagnosis, dosage changes, prescriptions, causal overclaims
         │
    CoordinatorBrief (Pydantic v2 validated)
         │
    ┌────┴────┐
    │         │
 SQLite    Hindsight
 (audit)   (retain outcome — closes the learning loop)
         │
    Result Page + Memory Trace
```

Two memory stores serve different purposes:

| | SQLite | Hindsight |
|---|---|---|
| **What** | Exact application records | Semantic long-term memory |
| **How retrieved** | SQL (exact) | Semantic search (fuzzy + temporal) |
| **Purpose** | Audit trail, UI timeline | Agent historical context |
| **When used** | Always | During agent reasoning |

SQLite tells you *what happened exactly*. Hindsight tells the *agent what is relevant right now*.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + CSS + JavaScript (Jinja2 templates) |
| Backend | Python · Flask 3.1 |
| Application DB | SQLite (WAL mode) |
| Agent LLM | Groq — `openai/gpt-oss-120b` |
| Long-term memory | **Hindsight Cloud** (`hindsight-client==0.10.1`) |
| Output validation | Pydantic v2 |
| Safety layer | Deterministic regex (`safety.py`) |
| Deployment | Vercel (`Procfile`: `web: python app.py`) |

---

## Key Safety Constraints

TrialGuard is decision **support** only. A deterministic safety validator (`safety.py`) sits between the LLM and the UI. It cannot be hallucinated out of existence — it is code, not a prompt instruction.

**Urgent bypass** — if the check-in text contains emergency language (`"chest pain"`, `"can't breathe"`, `"emergency help"`), the LLM pipeline is skipped entirely and an immediate escalation notice is returned.

**Output validator** — every field of the `CoordinatorBrief` is scanned before reaching the screen. Any of the following triggers a safe fallback replacement:
- Dosage modification instructions
- Prescription or diagnosis claims
- Medication start / stop directives
- Causal overclaims (`"X caused Y"`)
- Outcome guarantees

---

## Demo Participants

Ten synthetic participants, each with a deliberate story designed to test a different aspect of Hindsight memory retrieval:

| ID | Pattern | Key Teaching Point |
|----|---------|-------------------|
| **P209** ⭐ | Recurring headache after every dosage escalation | Hero demo — pattern detection across 7 months |
| P402 | Recurring nausea after dosage escalation | Full before/after Hindsight value |
| P117 | No recurring issues | Clean baseline — memory returns nothing alarming |
| P314 | Persistent fatigue, partial improvement only | Incomplete resolution pattern |
| P501 | Skin rash fully resolved | Positive outcome in history |
| P607 | Conflicting historical outcome records | Ambiguous history — agent flags, not decides |
| P722 | First-time symptom, no prior history | "No memory found" case handled correctly |
| P811 | Nausea from skipped meals — not dosage | Similar symptom, different cause — no misattribution |
| P905 | Six clean check-ins, zero adverse events | Fully benign history handled correctly |
| P990 | Withdrawal concern, no medical basis | Non-medical withdrawal documented appropriately |

---

## Quick Start

### Prerequisites
- Python 3.10+
- [Hindsight Cloud account](https://ui.hindsight.vectorize.io) — use promo code `MEMHACK99` for $50 free credits
- [Groq account](https://console.groq.com) — free tier is sufficient

### 1. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/TrialGuard.git
cd TrialGuard
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env — fill in your four credentials
```

```env
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_key_here
HINDSIGHT_BANK_ID=trialguard_id
GROQ_API_KEY=your_key_here
```

### 3. Seed data
```bash
# Populate SQLite with all 10 participants
python seed_db.py

# Seed P209's 7-month history into Hindsight (required for hero demo)
python seed_demo.py --participant P209

# Seed P209's timeline into SQLite (for the web UI timeline view)
python seed_p209_db.py

# Optional: seed all 10 participants into Hindsight
python seed_demo.py
```

> **Important:** `seed_p209_db.py` fills the browser timeline. `seed_demo.py --participant P209` fills Hindsight memory. Both are required for the full demo.

### 4. Start the app
```bash
python app.py
```

Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

Confirm:
- Dashboard shows **10 participants**
- Green banner: `✓ Hindsight memory connected`
- P209 timeline shows **5 historical check-ins**

---

## Running the P209 Demo

The hero demo shows the Hindsight before/after contrast using Participant P209 — seven months of recurring headaches, each following a dosage escalation.

**Step 1** — Navigate to P209 → New Check-in. Set date `2026-10-07`. Paste:
```
Participant P209 reports a severe headache returning over the past three days,
described as the worst episode since the trial began. Participant states the
headache started within 24 hours of the most recent dosage increase administered
last week. Participant is frustrated and says the headaches keep coming back
every time the dose goes up. Participant is questioning whether to continue in
the trial given the repeated disruption to their daily life.
```

**Step 2** — Select **Baseline (No Memory)** → Analyze. Observe:
- Historical Pattern: `"No historical pattern identified"`
- Previous Outcome: `"No prior outcome available"`

**Step 3** — Submit the same check-in with **With Hindsight Memory** → Analyze. Observe:
- **27 memories retrieved** spanning March–September 2026
- Historical Pattern: `"Recurring headache consistently following each dosage escalation — now the fourth occurrence"`
- Memory Trace shows every document ID traceable to a stored record

**Step 4** — Click **View Memory Trace** to see the full audit trail: Hindsight query sent, all retrieved document IDs, raw JSON output.

---

## Running the P402 Terminal Demo

```bash
# Full demo — baseline + Hindsight + side-by-side comparison
python demo_p402.py

# Hindsight result only
python demo_p402.py --hindsight

# Baseline result only
python demo_p402.py --baseline

# Seed P402 history then run
python demo_p402.py --seed
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

**144 tests** across 8 files. No live Hindsight server or Groq key required — all external calls are mocked.

| Test file | What it covers |
|-----------|---------------|
| `test_agent.py` | Two-stage pipeline, baseline mode, tool-call handling |
| `test_db.py` | SQLite roundtrip — all four tables |
| `test_integration.py` | End-to-end Flask route tests |
| `test_memory_connection.py` | Hindsight client connection and version ping |
| `test_memory_domain.py` | retain / recall / ingest / query operations |
| `test_models_safety.py` | Pydantic schema validation + safety validator patterns |
| `test_retrieval_isolation.py` | Participant isolation — P402 cannot read P209's memories |
| `test_routes.py` | All Flask routes, error handling, redirects |
| `test_seed_demo.py` | Seed script data integrity |

---

## Project Structure

```
TrialGuard/
├── app.py              # Flask app — 7 routes
├── agent.py            # Two-stage Groq agent (Stage 1: tool-calling, Stage 2: structured output)
├── memory.py           # Hindsight client wrapper — retain, recall, ingest, query
├── db.py               # SQLite layer — participants, checkins, outcomes, agent_runs
├── models.py           # Pydantic v2 — CoordinatorBrief, HistoricalMatch
├── safety.py           # Deterministic safety validator — urgent bypass + output scrubber
├── seed_demo.py        # Seed Hindsight with participant histories
├── seed_db.py          # Seed SQLite with all 10 participants
├── seed_p209_db.py     # Seed P209 timeline into SQLite for demo
├── demo_p402.py        # Terminal P402 demo — baseline vs Hindsight
├── requirements.txt    # Pinned dependencies
├── Procfile            # Vercel / production: web: python app.py
├── .env.example        # Environment variable template
├── data/
│   └── demo_data.json  # 10 participants, 45 check-ins (synthetic)
├── templates/          # Jinja2 — dashboard, participant, checkin, result, trace
├── static/
│   ├── css/main.css
│   └── js/main.js
├── tests/              # 144 pytest tests (all mocked — no live credentials needed)
└── help/               # Full documentation (14 files)
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `HINDSIGHT_BASE_URL` | Hindsight Cloud endpoint (`https://api.hindsight.vectorize.io`) |
| `HINDSIGHT_API_KEY` | Hindsight authentication key |
| `HINDSIGHT_BANK_ID` | Memory bank name (e.g. `trialguard_id`) |
| `GROQ_API_KEY` | Groq LLM API key |

---

## Deployment

Live at **[https://trialguard-dun.vercel.app](https://trialguard-dun.vercel.app)**

Deployed on Vercel via `Procfile`. Set all four environment variables in your Vercel project settings before deploying. The SQLite database resets on each cold start in serverless — Hindsight memory persists independently in the cloud regardless.

---

## Documentation

All help documents are in the `help/` folder:

| File | Contents |
|------|---------|
| `01_user_guide.md` | How to use the web app |
| `02_demo_guide.md` | Step-by-step P402 demo script |
| `03_how_it_works.md` | Technical deep-dive |
| `04_faq.md` | Common questions including data persistence |
| `05_data_guide.md` | What to enter in check-in notes |
| `06_setup_guide.md` | Full installation guide |
| `07_participant_reference.md` | All 10 participants and their stories |
| `08_troubleshooting.md` | Common issues and fixes |
| `09_github_guide.md` | GitHub setup and what to include |
| `10_vercel_guide.md` | Deploying on Vercel |
| `11_technical_writeup.md` | Full technical writeup |
| `14_p209_recorded_demo.md` | P209 recorded demo script |

---

## What This Demonstrates About Hindsight

TrialGuard demonstrates three properties of Hindsight that no vector database alone provides:

**Temporal retrieval** — memories carry ISO 8601 timestamps. Hindsight reasons about before/after relationships, surfacing the March 15 episode as prior context for an October 7 query without any date filtering in the application code.

**Entity-aware memory** — Hindsight extracts structured facts from retained text rather than storing raw embeddings. A query about `"headache and dosage changes"` retrieves the correct March episode even though the stored text is phrased entirely differently.

**Server-side tag isolation** — `tags_match="all_strict"` is enforced by the Hindsight server. P209's memories are physically unreachable by a P402 query. This is not a client-side filter — it cannot be bypassed by application-layer bugs.

---

## Safety Notice

This system is a prototype built for demonstration. It uses entirely synthetic data. It must not be used for real clinical decision-making. Every result page carries the mandatory disclaimer:

> *"This system does not diagnose or prescribe treatment. Prototype for demonstration using synthetic data. Not for clinical use or medical decision-making."*

---

## Links

- 🚀 **Live Demo:** [https://trialguard-dun.vercel.app](https://trialguard-dun.vercel.app)
- 🧠 **Hindsight Cloud:** [https://ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io)
- 📖 **Hindsight Docs:** [https://hindsight.vectorize.io](https://hindsight.vectorize.io)
- 💻 **Hindsight GitHub:** [https://github.com/vectorize-io/hindsight](https://github.com/vectorize-io/hindsight)
- 🤖 **What is agent memory:** [https://vectorize.io/what-is-agent-memory](https://vectorize.io/what-is-agent-memory)

---

## License

MIT
