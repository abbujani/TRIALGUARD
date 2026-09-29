# TrialGuard — Demo Guide (P402 Hero Demo)

> This guide walks you through the complete 60-second hackathon demo using Participant P402.
> Follow it in order for the most impactful presentation.

---

## Before the Demo — One-Time Setup

Run these commands **once** before your demo session:

```powershell
# 1. Start with a clean environment
cd c:\Users\Abdullah Hamdan\Desktop\hackathons\TrialGuard

# 2. Seed all 10 participants into Hindsight memory
python seed_demo.py

# 3. Seed all participants into SQLite (web UI)
python seed_db.py

# 4. Start the Flask app
python app.py
```

Open **http://127.0.0.1:5000** — you should see 10 participants on the dashboard.

---

## The Demo Story (memorise this)

> **"Clinical trial coordinators lose context over time. A participant's Month 6 complaint only makes sense when you know what happened in Month 1. TrialGuard uses Hindsight memory to retrieve that history automatically."**

---

## Demo Script — Step by Step

### Step 1 (0–10 sec) — Show the Dashboard

Open **http://127.0.0.1:5000**

Say:
> *"This is TrialGuard. We have 10 active participants in Trial 001. Each has a history stored in Hindsight memory."*

Point to the memory status bar:
> *"Hindsight is connected — long-term memory is live."*

---

### Step 2 (10–20 sec) — Show P402's History

Click **View** next to **P402**.

Point to the timeline:
> *"This is Participant 402. In Month 1 they had a dosage increase, then reported nausea, then improved after a meal-timing intervention. In Month 3 they had another dosage increase. Months 4 and 5 were fine."*

Pause.
> *"Now it's Month 6."*

---

### Step 3 (20–25 sec) — Open the Check-in Form

Click **New Check-in** on P402's page.

Set the date to **2026-09-02**.

Paste this into the check-in notes:

```
Participant P402 reports severe nausea returning over the past week.
Participant expressed significant frustration and stated they are
considering withdrawing from the study. They asked whether there is
any point in continuing given the recurring symptoms.
```

**Do NOT click Analyze yet.**

Say:
> *"This is today's complaint. Severe nausea, frustration, considering withdrawal. Let's see what happens without memory first."*

---

### Step 4 (25–35 sec) — Run Baseline First

Select **Baseline (No Memory)** and click **Analyze Check-in**.

When the result loads, point to:
- Historical Pattern: *"No historical pattern identified"*
- Previous Outcome: *"No prior outcome documented"*

Say:
> *"Without memory, the agent sees only today's complaint. It gives a reasonable response — but it has no context. It doesn't know this happened before."*

---

### Step 5 (35–50 sec) — Run Hindsight Mode

Go back. Submit the **same check-in again** but this time select **With Hindsight Memory**.

While it loads (5–10 seconds):
> *"Now Hindsight is querying long-term memory — retrieving everything relevant to nausea, dosage changes, and interventions for P402."*

When the result loads, point to:
- **Memory Status**: "✓ Hindsight queried — X memories retrieved"
- **Historical Memory section**: Month 1 nausea, the meal-timing intervention, improvement
- **Historical Pattern**: recurring nausea following dosage escalation
- **Previous Outcome**: symptoms improved after meal-timing intervention

Say:
> *"With Hindsight, the agent knows this happened in Month 1. It knows the intervention worked. It connects today's complaint to that history."*

---

### Step 6 (50–60 sec) — The Punchline

Point to the Coordinator Action — then close with:

> **"Without memory, the agent sees today's complaint. With Hindsight, it understands the history behind it."**

Optional: click **View Memory Trace** to show the exact memories retrieved.

---

## Optional: Run from the Terminal Instead

If you prefer a terminal demo (no browser needed):

```powershell
# Full demo — shows both modes and the comparison
python demo_p402.py

# Just the Hindsight result
python demo_p402.py --hindsight

# Just the baseline result
python demo_p402.py --baseline
```

---

## Talking Points for Judges

**On Hindsight:**
> *"We're not using a simple vector database. Hindsight combines semantic, keyword, graph, and temporal retrieval — that's why it can find the Month 1 episode even though the query is about Month 6."*

**On participant isolation:**
> *"Every memory is tagged with the participant ID and retrieved with strict tag matching — so P402's history can never leak into P117's analysis."*

**On safety:**
> *"There's a deterministic safety layer between the LLM and the UI. If the agent tries to recommend a dosage change or make a diagnosis, it's automatically replaced with a safe fallback before it reaches the coordinator."*

**On the learning loop:**
> *"After each analysis, the agent's output is retained back into Hindsight. So next time P402 comes in, the system will also remember this Month 6 analysis."*

---

## If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| Dashboard shows 1 participant | Run `python seed_db.py` |
| Hindsight shows unavailable | Check `.env` has correct `HINDSIGHT_BASE_URL` and `HINDSIGHT_API_KEY` |
| Analysis shows "agent error" | Check `.env` has correct `GROQ_API_KEY` |
| No memories retrieved | Run `python seed_demo.py` to seed P402 history into Hindsight |
| App won't start | Run `python seed_db.py` first, then `python app.py` |

See **08_troubleshooting.md** for more detail.
