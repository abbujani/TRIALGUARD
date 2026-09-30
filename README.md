# TrialGuard

> AI-powered clinical trial coordinator support, grounded in long-term memory.

**Prototype for hackathon demonstration using synthetic data. Not for clinical use or medical decision-making.**

---

## The Problem

Clinical trial coordinators interact with participants many times over months. A Month 6 complaint — severe nausea, frustration, considering withdrawal — only makes sense when viewed against Month 1: a dosage increase, the same nausea, a meal-timing intervention, and documented improvement.

Without memory, an LLM sees only today's complaint.

---

## The Solution

TrialGuard uses **Hindsight** to retain and retrieve the full longitudinal history of each participant's interactions. When a new check-in is submitted, the agent retrieves relevant historical events, connects them to the current complaint, and generates a structured **Coordinator Action Brief** — grounded in documented memory, not inference.

---

## How Hindsight Is Used

1. **Retain** — every check-in is stored in Hindsight with participant isolation tags and a stable document ID
2. **Tag isolation** — `tags=["participant:P402", "trial:TRIAL-001"]` with `tags_match="all_strict"` ensures no cross-participant leakage
3. **Recall** — the agent calls `recall_patient_history()` with a longitudinal query and receives ranked memories combining semantic, keyword, graph, and temporal retrieval
4. **Temporal context** — each memory carries an ISO 8601 timestamp, enabling Hindsight to reason about before/after relationships
5. **Outcome retention** — after each analysis, the agent's brief is retained back into Hindsight so future queries benefit from previous analyses

---

## Architecture

```
Coordinator submits check-in
         │
    Flask Route (/analyze)
         │
    ┌────┴────┐
    │         │
 SQLite    Hindsight
 (record)  (retain)
         │
    Agent LLM — Stage 1 (tool-calling)
         │
    recall_patient_history()
         │
    Hindsight Recall
    (semantic + keyword + graph + temporal)
         │
    Historical Memories
         │
    Agent LLM — Stage 2 (structured output)
         │
    Safety Validator (deterministic)
         │
    CoordinatorBrief (Pydantic)
         │
    ┌────┴────┐
    │         │
 SQLite    Hindsight
 (audit)   (retain outcome)
         │
    Result Page
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + CSS + JavaScript (Jinja2) |
| Backend | Python Flask |
| Application DB | SQLite |
| Agent LLM | Groq (`openai/gpt-oss-120b`) |
| Long-term memory | Hindsight Cloud |
| Output validation | Pydantic v2 |
| Secrets | `.env` / python-dotenv |

---

## Key Safety Constraints

TrialGuard is decision **support** only. A deterministic safety validator sits between the LLM and the UI and blocks:

- Dosage modification instructions
- Prescription or diagnosis claims
- Medication start/stop directives
- Causal overclaims ("X caused Y")
- Urgent language triggers an emergency bypass — LLM is skipped entirely

---

## Demo Participants

Ten synthetic participants with deliberate patterns:

| ID | Pattern |
|----|---------|
| **P402** ⭐ | Recurring nausea after dosage — hero demo participant |
| P117 | No recurring issues |
| P209 | Recurring headache pattern |
| P314 | Persistent fatigue |
| P501 | Issue resolved previously |
| P607 | Conflicting historical records |
| P722 | First-time symptom, no prior history |
| P811 | Similar symptom, different (non-dosage) cause |
| P905 | Six clean check-ins, no adverse events |
| P990 | Withdrawal concern with no medical basis |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Hindsight Cloud account — https://hindsight.vectorize.io
- Groq account — https://console.groq.com

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your Hindsight and Groq credentials
```

### 3. Seed data
```bash
# Populate SQLite with all 10 participants
python seed_db.py

# Seed P402 history into Hindsight (required for the demo)
python seed_demo.py --participant P402

# Optional: seed all 10 participants
python seed_demo.py
```

### 4. Start the app
```bash
python app.py
```

Open **http://127.0.0.1:5000**

---

## Running the P402 Demo

```bash
# Full terminal demo — baseline + Hindsight + comparison
python demo_p402.py

# Just the Hindsight result
python demo_p402.py --hindsight

# Seed then run
python demo_p402.py --seed
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All **144 tests** pass. No live Hindsight or Groq required (all external calls mocked).

---

## Project Structure

```
TrialGuard/
├── app.py              # Flask app + routes
├── agent.py            # Two-stage Groq agent
├── memory.py           # Hindsight client wrapper
├── db.py               # SQLite layer
├── models.py           # Pydantic output schema
├── safety.py           # Deterministic safety validator
├── seed_demo.py        # Seed Hindsight with participant histories
├── seed_db.py          # Seed SQLite with participant records
├── demo_p402.py        # Terminal P402 demo
├── requirements.txt
├── .env.example
├── data/
│   └── demo_data.json  # 10 participants, 45 check-ins
├── templates/          # Jinja2 HTML templates
├── static/             # CSS + JS
├── tests/              # 144 pytest tests
└── help/               # Documentation
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `HINDSIGHT_BASE_URL` | Hindsight Cloud endpoint |
| `HINDSIGHT_API_KEY` | Hindsight authentication key |
| `HINDSIGHT_BANK_ID` | Memory bank name |
| `GROQ_API_KEY` | Groq LLM API key |

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
| `10_vercel_guide.md` | Deploying live on Vercel |
| `11_technical_writeup.md` | Hackathon technical writeup |

---

## Safety Notice

This system is a prototype built for hackathon demonstration. It uses entirely synthetic data. It must not be used for real clinical decision-making. Every result page displays the mandatory safety disclaimer:

> *"This system does not diagnose or prescribe treatment. Prototype for hackathon demonstration using synthetic data. Not for clinical use or medical decision-making."*

---

## License

MIT
