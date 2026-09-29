# TrialGuard — Frequently Asked Questions

---

## Data & Persistence

### Are new check-ins permanent?

**Yes — in two places.**

1. **SQLite** (`data/trialguard.db`) — The check-in text, timestamp, and participant link are saved permanently to the local database file the moment you click Analyze. This survives app restarts.

2. **Hindsight** — The check-in content is retained in the Hindsight cloud memory bank. It stays there indefinitely until explicitly deleted. It will be retrieved in all future analyses for that participant.

So if you submit a check-in today and restart the app tomorrow, the check-in will still be in the database AND in Hindsight memory.

---

### What happens if I restart the app?

The SQLite database persists — all participants, check-ins, and agent runs are preserved. Hindsight memory also persists (it's cloud-based). You will see everything exactly as you left it.

---

### What happens if I delete the database file?

The SQLite file (`data/trialguard.db`) will be recreated empty on next app start. You will lose all check-in records and agent run history. **Hindsight memory is NOT affected** — it exists independently in the cloud.

To rebuild the participant list after deleting the DB: run `python seed_db.py`.

---

### Can I remove a check-in from Hindsight?

Not through the TrialGuard UI (there is no delete button — this is intentional for demo integrity). To remove a memory from Hindsight manually, you would use the Hindsight Cloud dashboard or their API directly with the `document_id` (format: `checkin:P402:<id>`).

---

### Does the agent remember previous analyses?

**Yes.** After every analysis, the agent's output (the coordinator brief summary) is retained back into Hindsight with `document_id = outcome:<run_id>`. So future queries for P402 will also retrieve previous analysis summaries as part of the historical context.

This is the learning loop: each interaction makes the system more useful for the next one.

---

### Is the data real patient data?

**No.** All data is synthetic, created specifically for this hackathon demonstration. No real patient information is used anywhere in this system. The disclaimer "Prototype for hackathon demonstration using synthetic data. Not for clinical use or medical decision-making." is displayed on every result page.

---

## The Agent & AI

### Why does the agent sometimes not retrieve any memories?

Three possible reasons:

1. **P402's history hasn't been seeded** — run `python seed_demo.py` to seed it
2. **Hindsight is unavailable** — check the memory status indicator on the dashboard
3. **The query didn't match stored memories semantically** — try a check-in that mentions nausea, dosage, or specific symptoms

The agent decides whether to call Hindsight at all (Stage 1). If it decides the check-in doesn't need historical context (e.g. a simple routine check-in), it may skip the recall entirely.

---

### Why does it say "No tool call made" sometimes?

The agent decides in Stage 1 whether historical context is needed. For very routine check-ins ("Participant reports feeling well, no issues"), it may correctly decide no recall is needed. This is intended behaviour.

---

### Can the agent make clinical decisions?

**No — by design.** The safety validator blocks any output that:
- Recommends dosage changes
- Makes a diagnosis
- Prescribes medication
- States causation (e.g. "the dosage caused the nausea")
- Directs medication start/stop

If the model attempts any of these, the field is replaced with a safe fallback before it reaches the screen.

---

### What is the "urgent bypass"?

If the check-in text contains emergency language — e.g. "chest pain", "can't breathe", "I feel like I may collapse", "need emergency help" — the AI pipeline is bypassed entirely. The system immediately returns an urgent escalation notice without waiting for an LLM response. This is intentional safety-first design.

---

### What model is being used?

`openai/gpt-oss-120b` on Groq. This model supports both tool-calling (Stage 1) and structured JSON output (Stage 2).

---

## Memory & Hindsight

### What is Hindsight?

Hindsight is a semantic long-term memory system. Unlike a simple vector database, it combines four retrieval strategies: semantic, keyword, graph, and temporal. It extracts structured facts from retained text, not just embeddings. See `03_how_it_works.md` for details.

### What is the memory bank?

A "bank" in Hindsight is a named container for memories. TrialGuard uses a single bank (`trialguard_id`). All participants share the bank but are isolated by participant tags.

### Can P402's memories leak into P117's analysis?

**No.** Every recall uses `tags_match="all_strict"` with the specific participant's tag. The Hindsight server enforces this — only memories with the matching tag are returned. This is tested explicitly in the test suite (see `tests/test_retrieval_isolation.py`).

### How many memories does Hindsight return?

It depends on how much history is stored and how semantically relevant it is. In the P402 demo, around 30–35 memories are returned (Hindsight extracts multiple discrete facts from each check-in). The budget is set to `"mid"` with `max_tokens=3000`.

---

## The Web App

### Why does the dashboard show only 1 participant?

You need to run `python seed_db.py` to populate all 10 participants into SQLite. The web UI reads from SQLite, not from the JSON data file directly.

### Why is the participant page empty (no check-ins)?

Check-ins only appear in the timeline if they were submitted through the web form (or the demo script). The `seed_demo.py` script seeds Hindsight but not SQLite check-in records — those come from actual form submissions.

### Can I use the app with participants not in the demo data?

Yes. You can add any participant via the SQLite API or by adding them directly to `data/demo_data.json` and re-running `seed_db.py`. The agent will work for any participant as long as you've submitted at least one check-in through the web form.

---

## Setup & Environment

### Do I need to run seed_demo.py every time?

No — once is enough. Hindsight memories persist in the cloud. Only re-run if you want to reset or if the bank was cleared.

### Do I need to run seed_db.py every time?

No — once is enough. SQLite data persists in `data/trialguard.db`. Only re-run if you delete the database.

### What if the .env file is missing?

The app will fail to start (or fail on first Groq/Hindsight call). Copy `.env.example` to `.env` and make sure all four variables are set. See `06_setup_guide.md`.

### Is my API key safe?

The `.env` file is in `.gitignore` — it will not be committed to Git. Never share `.env` publicly or commit it to a repository.
