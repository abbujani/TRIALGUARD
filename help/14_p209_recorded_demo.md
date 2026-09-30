# TrialGuard — P209 Recorded Demo Guide

> Complete script for recording the demo video using Participant P209.
> Everything is exact — copy-paste ready. Do not paraphrase the check-in texts.

---

## Before You Start Recording

### One-time setup (run ALL of these before the demo)

```powershell
# 1. Seed P209's 5 historical check-ins into the SQLite timeline (web UI)
python seed_p209_db.py

# 2. Seed P209's history into Hindsight memory (AI recall)
python seed_demo.py --participant P209

# 3. Make sure all 10 participants are in SQLite
python seed_db.py

# 4. Start the app
python app.py
```

> **Important:** Both `seed_p209_db.py` AND `seed_demo.py --participant P209` must be run.
> - `seed_p209_db.py` → fills the **timeline** you see in the browser
> - `seed_demo.py` → fills **Hindsight memory** the AI recalls from
> They are separate. You need both.

Open **http://127.0.0.1:5000** — confirm:
- Dashboard shows 10 participants
- Hindsight shows "connected" in green
- P209 timeline shows exactly **5 check-ins**

### Browser prep
- Use Chrome or Edge in full-screen (F11)
- Zoom browser to 100%
- Close all other tabs
- Hide bookmarks bar for a cleaner look

---

## The Demo Story (say this at the start of the recording)

> *"Clinical trial coordinators manage participants across months. When a participant reports a problem, the question is always: is this new, or have we seen this before? Participant 209 has been in this trial for seven months. They have reported a headache after every single dosage increase — but that history is spread across months of records. Watch what happens when the AI has memory versus when it doesn't."*

---

## PART 1 — Show the Existing History (30 seconds)

### Action: Click **View** next to P209 on the dashboard

You will see the timeline with these **5 entries** already populated:

| Date | What it shows |
|------|--------------|
| 2026-03-15 | Headache after dosage initiation — hydration advised |
| 2026-03-29 | Headache improved following hydration guidance |
| 2026-05-09 | Second dosage escalation — coordinator reminded about hydration |
| 2026-05-15 | Headache returned after second dosage increase — recurring pattern noted |
| 2026-09-03 | Third headache at third dosage increase — escalated for clinical review |

**Say:**
> *"Here is Participant 209's timeline. Three previous headache episodes — Month 1, Month 3, Month 6 — each one following a dosage escalation. Improved with hydration the first time. Came back the second time. Came back again the third time."*

Scroll slowly through the entries as you speak so the viewer can read them.

**Say:**
> *"Now it is Month 7. There has been another dosage increase. The participant calls in."*

---

## PART 2 — Submit the New Check-in (20 seconds)

### Action: Click **+ New Check-in** on P209's page

Set the date field to: **2026-10-07**

### Action: Paste this EXACT text into the check-in notes field:

```
Participant P209 reports a severe headache returning over the past three days, described as the worst episode since the trial began. Participant states the headache started within 24 hours of the most recent dosage increase administered last week. Participant is frustrated and says the headaches keep coming back every time the dose goes up. Participant is questioning whether to continue in the trial given the repeated disruption to their daily life.
```

**Say:**
> *"This is today's complaint. Severe headache — the worst yet. Frustration. Considering withdrawal. Let's see what the AI does without memory first."*

---

## PART 3 — Baseline Mode (25 seconds)

### Action: Select **Baseline (No Memory)** → click **Analyze Check-in**

While it loads (3–5 seconds):
> *"Without memory — the AI sees only today's message."*

When the result loads, **pause and point to**:

- **Historical Pattern** → will say something like *"No historical pattern identified"*
- **Previous Outcome** → will say something like *"No prior outcome documented"*
- **Memory Status** → *"Baseline mode — no memory retrieval"*

**Say:**
> *"Reasonable. Professional. It tells the coordinator to follow the protocols. But it has no idea this happened three times before. It doesn't know hydration helped. It doesn't know the pattern. It sees a headache — not a history."*

---

## PART 4 — Hindsight Mode (35 seconds)

### Action: Click the browser back button → P209's timeline → **+ New Check-in** again

Set date to: **2026-10-07**

Paste the **exact same check-in text** again:

```
Participant P209 reports a severe headache returning over the past three days, described as the worst episode since the trial began. Participant states the headache started within 24 hours of the most recent dosage increase administered last week. Participant is frustrated and says the headaches keep coming back every time the dose goes up. Participant is questioning whether to continue in the trial given the repeated disruption to their daily life.
```

### Action: Select **With Hindsight Memory** → click **Analyze Check-in**

While it loads (8–15 seconds):
> *"Now Hindsight is querying long-term memory — searching across all seven months of history for anything relevant to headaches, dosage changes, interventions, and outcomes."*

When the result loads, **point to each section in order**:

**1. Memory Status** (top of page)
> *"Hindsight queried. Multiple memories retrieved — each one a piece of documented history."*

**2. Hindsight Memory section** — read out the matches slowly
> *"March 15 — headache after the first dosage. March 29 — improved with hydration. May 9 — second dosage escalation, hydration reminder given. May 15 — headache returned. September 3 — third headache at the third dosage increase."*

**3. Historical Pattern**
> *"Recurring headache consistently following each dosage escalation. This is the fourth occurrence."*

**4. Previous Outcome**
> *"Hydration guidance provided improvement — but only partially, and it came back."*

**5. Coordinator Action**
> *"Review this documented pattern with the clinical team."*

**Say:**
> *"Same complaint. Same AI model. The only difference is memory."*

---

## PART 5 — Memory Trace (15 seconds, optional but impressive)

### Action: Click **View Memory Trace** at the bottom of the result page

Point to:
- **Hindsight query sent** — the actual question the AI sent to memory
- **Retrieved document IDs** — `checkin:P209:001`, `checkin:P209:002`, etc. — these match exactly the records seeded into Hindsight
- **Raw JSON** — the agent's complete structured output

**Say:**
> *"This is the full audit trail. Every memory retrieved has a document ID. Every claim the AI made is traceable to a specific stored record. Nothing is invented."*

---

## PART 6 — The Punchline (5 seconds)

**Say — slowly and clearly:**

> **"Without memory, the AI sees a headache. With Hindsight, it sees a pattern that has been building for seven months."**

---

## PART 7 — Submit the Follow-up (Optional — shows the learning loop)

### Action: Back to P209's page → **+ New Check-in**

Set date to: **2026-10-14**

Paste this EXACT text:

```
Participant P209. Trial: TRIAL-001. Date: 2026-10-14.

Follow-up check-in one week after the severe headache episode. Participant reports the headache has reduced to a mild level after reinstating the hydration protocol and resting adequately. Participant remains frustrated about the recurring pattern but has agreed to continue in the trial pending clinical team review. Coordinator documented partial improvement. This is now the fourth documented episode of headache following a dosage escalation event. Escalated to clinical team for formal assessment of the recurring pattern.
```

Select **With Hindsight Memory** → Analyze

**Say:**
> *"Now this outcome is also retained in Hindsight. Next time Participant 209 comes in, the system will retrieve not just the four headache episodes but also this follow-up — including whether the hydration guidance worked again. The memory grows with every interaction."*

---

## Recording Checklist

Before hitting record — verify every item:

- [ ] `python seed_p209_db.py` has been run (populates the SQLite timeline)
- [ ] `python seed_demo.py --participant P209` has been run (populates Hindsight memory)
- [ ] `python seed_db.py` has been run (all 10 participants in SQLite)
- [ ] `python app.py` is running
- [ ] Dashboard at http://127.0.0.1:5000 shows 10 participants
- [ ] Dashboard shows **"Hindsight memory connected"** in green
- [ ] P209 timeline shows exactly **5 check-ins** with dates 2026-03-15 through 2026-09-03
- [ ] Both check-in texts are copied and ready to paste (keep this file open in a second window or on your phone)
- [ ] Browser is full-screen (F11), 100% zoom, no other tabs visible
- [ ] Microphone is working and tested

---

## Timing Guide

| Part | Action | Duration |
|------|--------|----------|
| Intro | Open dashboard, explain the story | 0:00 – 0:20 |
| Part 1 | Navigate to P209, scroll through 5 check-ins | 0:20 – 0:50 |
| Part 2 | Open check-in form, paste text | 0:50 – 1:10 |
| Part 3 | Baseline result — point to missing history | 1:10 – 1:35 |
| Part 4 | Hindsight result — point to all 5 memories | 1:35 – 2:30 |
| Part 5 | Memory trace (optional) | 2:30 – 2:45 |
| Part 6 | Punchline | 2:45 – 2:50 |
| Part 7 | Follow-up / learning loop (optional) | 2:50 – 3:20 |

**Target total: 2:50 to 3:20**

---

## Exact Check-in Texts (Clean Copy)

### NEW CHECK-IN — Month 7 (paste into web form)

**Date:** `2026-10-07`
**Mode:** Baseline first, then Hindsight (submit twice)

```
Participant P209 reports a severe headache returning over the past three days, described as the worst episode since the trial began. Participant states the headache started within 24 hours of the most recent dosage increase administered last week. Participant is frustrated and says the headaches keep coming back every time the dose goes up. Participant is questioning whether to continue in the trial given the repeated disruption to their daily life.
```

---

### FOLLOW-UP CHECK-IN — Month 7 follow-up (paste into web form)

**Date:** `2026-10-14`
**Mode:** With Hindsight Memory

```
Participant P209. Trial: TRIAL-001. Date: 2026-10-14.

Follow-up check-in one week after the severe headache episode. Participant reports the headache has reduced to a mild level after reinstating the hydration protocol and resting adequately. Participant remains frustrated about the recurring pattern but has agreed to continue in the trial pending clinical team review. Coordinator documented partial improvement. This is now the fourth documented episode of headache following a dosage escalation event. Escalated to clinical team for formal assessment of the recurring pattern.
```

---

## What the P209 Timeline Looks Like Before the Demo

After running `seed_p209_db.py`, the timeline at http://127.0.0.1:5000/participants/P209 shows:

```
2026-03-15  Participant P209. Trial: TRIAL-001. Date: 2026-03-15.
            Participant reported mild to moderate headache beginning three days
            after dosage initiation...

2026-03-29  Participant P209. Trial: TRIAL-001. Date: 2026-03-29.
            Headache symptoms reduced following hydration guidance...

2026-05-09  Participant P209. Trial: TRIAL-001. Date: 2026-05-09.
            Dosage escalation per protocol. Coordinator reminded participant
            to maintain fluid intake...

2026-05-15  Participant P209. Trial: TRIAL-001. Date: 2026-05-15.
            Headache returned following the most recent dosage increase...

2026-09-03  Participant P209. Trial: TRIAL-001. Date: 2026-09-03.
            Headache reported again at Month 6 check-in, coinciding with
            the third dosage increase...
```

---

## What Hindsight Should Return

When you run the Hindsight analysis on the Month 7 check-in, expect these memories:

| Document ID | Date | Why retrieved |
|-------------|------|---------------|
| `checkin:P209:001` | 2026-03-15 | Headache after first dosage — same symptom, same trigger |
| `checkin:P209:002` | 2026-03-29 | Improved with hydration — previous documented outcome |
| `checkin:P209:003` | 2026-05-09 | Second dosage + hydration reminder — same trigger pattern |
| `checkin:P209:004` | 2026-05-15 | Headache recurrence — recurring pattern evidence |
| `checkin:P209:005` | 2026-09-03 | Third headache episode — confirms the established pattern |

> These document IDs match exactly what `seed_p209_db.py` saved to SQLite AND what `seed_demo.py` retained in Hindsight — so the memory trace will show the correct IDs linking back to the correct timeline entries.

Expected agent output:
- **Historical pattern:** Recurring headache consistently following each dosage escalation — now fourth occurrence
- **Previous outcome:** Hydration guidance associated with partial/temporary improvement
- **Coordinator action:** Review documented pattern with clinical team for formal assessment

---

## If Something Goes Wrong During Recording

| Problem | Cause | Fix |
|---------|-------|-----|
| P209 timeline shows "No check-ins recorded yet" | `seed_p209_db.py` not run | Run `python seed_p209_db.py` and refresh |
| "No memories retrieved" from Hindsight | `seed_demo.py` not run | Run `python seed_demo.py --participant P209` and wait 10 sec |
| Hindsight shows unavailable | `.env` not loaded or network issue | Restart `python app.py` from the project folder |
| Agent shows "analysis unavailable" | Invalid Groq API key | Check `GROQ_API_KEY` in `.env` |
| P209 not on dashboard | `seed_db.py` not run | Run `python seed_db.py` and refresh |
| Timeline shows entries but wrong dates | Old data in DB | No action needed — dates are correct from `seed_p209_db.py` |
| App won't start | Port 5000 in use | Run `Get-Process -Name python | Stop-Process -Force` then restart |
