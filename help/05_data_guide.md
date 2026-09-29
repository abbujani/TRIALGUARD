# TrialGuard — Data Entry Guide

> What to type into check-in notes, and how to get the best results from the agent.

---

## What Makes a Good Check-in Note?

The agent works best when check-in notes are **specific, narrative, and clinical in tone** — similar to how a coordinator would document a real interaction.

### Good example:
```
Participant reports moderate nausea beginning three days after the most 
recent dosage increase. Described symptoms as persistent but manageable. 
No vomiting. Participant is concerned the symptoms are linked to the 
medication. Coordinator documented the report and will follow up next week.
```

### Poor example:
```
Not feeling well
```

The more context you provide, the better the semantic match with historical memories.

---

## Event Types and What to Write

### Routine Check-in
Use for: scheduled monthly visits with no adverse events.

```
Participant reports feeling well overall. No new symptoms since last visit. 
Tolerating current dosage without issue. Energy levels normal. 
Coordinator confirmed continued enrollment, no protocol deviations.
```

---

### Symptom Report
Use for: a new or recurring complaint from the participant.

```
Participant reports [symptom] beginning [timeframe]. Described as [severity]. 
[Any additional detail: location, duration, triggers]. 
Coordinator documented the symptom and [action taken / none required].
```

**Examples:**
```
Participant reports mild to moderate headache beginning two days after 
last dosage change. Described as frontal pressure, lasting several hours.
Coordinator advised adequate hydration and logged the report.
```

```
Participant reports persistent fatigue over the past two weeks. 
Described as general tiredness affecting daily activities. No pain.
Coordinator logged the report for clinical review.
```

---

### Dosage Change
Use for: recording a protocol-scheduled dosage escalation or reduction.

```
Dosage [increase/decrease] administered today per protocol schedule. 
Participant was briefed on potential side effects. 
Participant [acknowledged / expressed mild concern / felt well].
Coordinator noted the change in the medical log.
```

---

### Outcome / Follow-up
Use for: documenting the result of a previous intervention or episode.

```
Follow-up check-in after earlier [symptom] episode. 
Participant reports that symptoms have [improved significantly / partially resolved / 
persisted / worsened] since [intervention or last visit].
Coordinator documented the [positive/partial/negative] outcome.
```

---

### Concern / Withdrawal Risk
Use for: when a participant expresses frustration or intent to leave the trial.

```
Participant expressed significant frustration about [reason]. 
Participant stated they are considering withdrawing from the study. 
Coordinator documented the concern and will escalate for clinical team review.
```

---

## The P402 Demo — Exact Text to Use

For the Month 6 hero check-in, copy this exactly:

```
Participant P402 reports severe nausea returning over the past week. 
Participant expressed significant frustration and stated they are 
considering withdrawing from the study. They asked whether there is 
any point in continuing given the recurring symptoms.
```

This will match against the Month 1 nausea memories stored in Hindsight and produce the full historical pattern + previous outcome response.

---

## Sample Check-ins for Each Participant

### P117 — No recurring issue
```
Routine monthly check-in. No symptoms reported. 
Participant tolerating current dosage well. 
No concerns raised. Confirmed continued enrollment.
```
Expected result: no historical pattern, no memories of concern — baseline-style brief.

---

### P209 — Recurring headache
```
Participant reports moderate headache returning after today's dosage increase. 
This is the third time headaches have followed a dosage change. 
Coordinator documented the recurrence and reinforced hydration guidance.
```
Expected result: Hindsight should retrieve the Month 1 and Month 3 headache episodes.

---

### P314 — Persistent fatigue
```
Participant reports fatigue continuing at a moderate level. 
Has been ongoing since Month 1 with only partial improvement. 
Coordinator flagged for clinical review.
```
Expected result: Hindsight should retrieve previous fatigue reports.

---

### P501 — Issue resolved previously
```
Six-month check-in. No new symptoms. 
The earlier skin rash has not recurred since Month 2 resolution.
Participant remains well and engaged in the study.
```
Expected result: Hindsight retrieves the rash episode and its resolution.

---

### P607 — Conflicting history
```
Participant reports joint pain continuing. 
States that the earlier physical therapy did not fully resolve symptoms 
despite a previous record indicating improvement. 
Coordinator notes the conflicting accounts for clinical review.
```
Expected result: Hindsight should surface both the improvement record and the contradiction.

---

### P722 — First-time issue
```
Participant reports shortness of breath during mild physical activity 
for the first time. No prior history of this symptom.
Coordinator documented the first occurrence and referred for clinical evaluation.
```
Expected result: no relevant historical pattern — agent should state no memory found.

---

### P811 — Similar symptom, different cause
```
Participant reports nausea again today.
After questioning, participant confirms they skipped breakfast this morning.
No recent dosage change. Coordinator documents as meal-related, not medication-related.
```
Expected result: Hindsight retrieves the previous meal-related nausea episode, showing it is not dosage-linked.

---

### P905 — Benign
```
Month 6 final check-in. Participant has completed the full observation period.
No adverse events reported across all six months. 
Participant is one of the most compliant in the cohort.
```
Expected result: clean history, positive pattern, routine brief.

---

### P990 — Withdrawal, no medical reason
```
Participant contacted the team to discuss withdrawing from the trial.
Cites personal scheduling difficulties, not any medical concern.
No adverse symptoms have been reported at any previous visit.
Coordinator documented the withdrawal request.
```
Expected result: no relevant medical history — agent should note absence of medical basis.

---

## Tips for Better Agent Responses

1. **Include the participant ID** in the note — e.g. "Participant P402 reports..." This helps Hindsight extract the entity correctly.
2. **Include a timeframe** — "beginning three days ago", "over the past week" — Hindsight uses temporal context.
3. **Mention the symptom by name** — "nausea", "headache", "fatigue" — Hindsight's semantic search matches on these.
4. **Note the coordinator's action** — "Coordinator documented...", "Coordinator referred..." — this becomes part of future outcome retrieval.
5. **For dosage events**, explicitly say "dosage increase" or "dosage escalation" — this is what the agent looks for when building the historical pattern.

---

## What NOT to Write

Avoid:
- **Diagnoses**: "Participant has CINV" — the safety validator will redact this
- **Dosage recommendations**: "Coordinator suggested reducing dosage" — will be blocked
- **Medical advice**: any prescription or treatment recommendation
- **Invented history**: don't write "as happened before" unless it actually did — the agent may use this as a false historical reference

These will either be blocked by the safety validator or produce misleading results.
