# TrialGuard — User Guide

> **Prototype for hackathon demonstration using synthetic data. Not for clinical use or medical decision-making.**

---

## What is TrialGuard?

TrialGuard is an AI-powered support tool for clinical trial coordinators. It helps you understand a participant's **current complaint in the context of their full history** — by retrieving relevant past interactions, interventions, and outcomes from long-term memory (Hindsight), then generating a structured Coordinator Action Brief.

The core value: instead of seeing only today's complaint, you see the history behind it.

---

## Starting the App

```powershell
# In the project folder:
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## The Dashboard

The first page you see. It shows:

| Section | What it tells you |
|---------|-------------------|
| **Active Participants** | Total participants loaded in the system |
| **Check-ins Recorded** | Total check-ins submitted through the web form |
| **Outcomes Documented** | Retained outcome records |
| **Agent Analyses Run** | How many coordinator briefs have been generated |
| **Hindsight Status** | Whether long-term memory is connected (green = OK) |
| **Participants Table** | All participants with quick links |
| **Recent Analyses** | Last 5 agent runs with mode and memory count |

If Hindsight shows as unavailable, analyses will still run but without historical context.

---

## Navigating to a Participant

Click **View** next to any participant on the dashboard to open their **timeline page**.

The timeline shows:
- Every check-in in chronological order
- The event type (routine, symptom report, dosage change, outcome, concern)
- Links to any analysis runs attached to that check-in

---

## Submitting a New Check-in

1. Click **New Check-in** from the dashboard or participant page
2. Fill in the **date** (defaults to today)
3. Write the **check-in notes** — describe what the participant reported
4. Choose the **analysis mode**:
   - **With Hindsight Memory** — retrieves historical context (recommended)
   - **Baseline (No Memory)** — analyses current check-in only
5. Click **Analyze Check-in**

The system will:
- Save the check-in to the database
- Store it in Hindsight memory for future retrieval
- Run the AI agent
- Redirect you to the result page

---

## Reading the Coordinator Action Brief

The result page has these sections:

| Section | Meaning |
|---------|---------|
| **Current Issue** | What the participant is reporting today |
| **Participant Concern** | Any emotional or withdrawal concerns expressed |
| **Hindsight Memory** | Historical events retrieved and why they are relevant |
| **Historical Pattern** | Any recurring pattern identified across past events |
| **Previous Outcome** | What happened last time a similar issue occurred |
| **Coordinator Action** | Suggested next step (always review/escalate — never a clinical decision) |
| **Memory Status** | How many Hindsight memories were retrieved and used |
| **Safety Note** | Mandatory disclaimer — always present |

---

## The Memory Trace Page

After viewing a result, click **View Memory Trace** to see the audit record:

- The exact query sent to Hindsight
- Every memory retrieved — with document ID, tags, and content
- The raw JSON output from the agent
- The original check-in text

This is useful for understanding **why** the agent said what it said.

---

## The Two Modes Explained

### With Hindsight Memory (recommended)
The agent first decides whether historical context is needed, then calls Hindsight to retrieve relevant memories, then generates the brief grounded in that history.

### Baseline (No Memory)
The agent sees only the current check-in. No historical context is retrieved. Use this to demonstrate the contrast — the same complaint gets a much more generic response without memory.

---

## What the System Will NOT Do

TrialGuard is decision **support**, not clinical decision-making. It will never:

- Diagnose a participant
- Prescribe or recommend medication changes
- Tell you to increase or decrease a dosage
- State that one event definitively caused another
- Decide whether a participant should leave the trial

If it attempts any of the above, the safety validator automatically replaces that output with a safe fallback.

---

## Urgent Safety Language

If the check-in text contains urgent language (e.g. "can't breathe", "chest pain", "emergency help"), the system bypasses the AI entirely and displays an emergency escalation notice immediately.

---

## Keyboard Tips

- The date field auto-fills to today's date
- Pressing the Analyze button disables it after click to prevent double-submission
- Use the browser back button to return to the participant timeline after viewing a result

---

## Next Steps

- See **02_demo_guide.md** for the P402 demo walkthrough
- See **05_data_guide.md** for what to type into check-in notes
- See **07_participant_reference.md** for all 10 participant profiles
