# TrialGuard — Participant Reference

> All 10 participants in the demo dataset. Each has a deliberate story designed to test a different aspect of memory retrieval.

**Trial:** TRIAL-001 — Phase II Oncology Safety & Efficacy Study  
**Duration:** Month 1 (March 2026) to Month 6 (September 2026)

---

## P402 — Hero Participant ⭐

**Pattern:** Recurring nausea after dosage escalation events  
**Status:** Active  
**Check-ins:** 8  
**Use for:** The main demo — demonstrates the full before/after value of Hindsight memory

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-10 | Dosage change | First dosage increase per protocol. Participant felt well. |
| 2026-03-14 | Symptom report | Moderate nausea began 2 days after dosage increase. Meal-timing intervention initiated. |
| 2026-03-28 | Outcome | Symptoms significantly improved after meal-timing intervention. |
| 2026-04-08 | Routine | No issues. Tolerating dosage well. |
| 2026-05-06 | Dosage change | Second dosage increase. Coordinator reminded P402 of meal-timing guidance. |
| 2026-06-03 | Routine | Good tolerance. Following meal-timing guidance consistently. |
| 2026-07-08 | Routine | Participant continues to do well. No adverse symptoms. |
| 2026-09-02 | **Concern** | **Severe nausea returns. Participant frustrated, considering withdrawal.** |

### What the Agent Should Surface
- Historical pattern: recurring nausea following dosage escalation
- Previous outcome: symptoms improved after meal-timing intervention
- Action: review historical context with clinical team; note the prior successful intervention

---

## P117 — No Recurring Issue

**Pattern:** Straightforward enrollment, no adverse events  
**Status:** Active  
**Check-ins:** 4  
**Use for:** Demonstrating a clean baseline — memory returns nothing alarming

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-12 | Routine | Enrollment check-in. Feeling well. No concerns. |
| 2026-04-10 | Routine | No symptoms. Tolerating dosage well. |
| 2026-05-08 | Dosage change | First escalation. No adverse reaction. |
| 2026-07-10 | Routine | Continued good tolerance. No issues. |

### What the Agent Should Surface
- No concerning historical pattern
- Clean history — agent should confirm normal progress

---

## P209 — Recurring Headache Pattern

**Pattern:** Headache following each dosage change  
**Status:** Active  
**Check-ins:** 5  
**Use for:** Demonstrating pattern detection across multiple events

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-15 | Symptom report | Mild-moderate headache after dosage initiation. Hydration advised. |
| 2026-03-29 | Outcome | Headache improved following hydration guidance. |
| 2026-05-09 | Dosage change | Escalation. Coordinator reminded P209 to hydrate. |
| 2026-05-15 | Symptom report | Headache returned after dosage increase. Concerning pattern noted. |
| 2026-09-03 | Symptom report | Headache again at Month 6 dosage increase — third occurrence. |

### What the Agent Should Surface
- Pattern: headache recurring after every dosage change (3 times)
- Previous outcome: hydration guidance helped
- Action: review recurrence with clinical team

---

## P314 — Persistent Fatigue

**Pattern:** Fatigue ongoing since Month 1 with only partial improvement  
**Status:** Active  
**Check-ins:** 4  
**Use for:** Demonstrating a symptom that persists despite intervention

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-18 | Symptom report | Persistent fatigue after enrollment dosage. Coordinator logged. |
| 2026-04-15 | Outcome | Fatigue somewhat reduced with sleep schedule adjustment. |
| 2026-05-20 | Symptom report | Fatigue persists moderately. Difficulty concentrating. Flagged for review. |
| 2026-07-14 | Symptom report | Fatigue continues. Ongoing since Month 1, only partial relief documented. |

### What the Agent Should Surface
- Pattern: fatigue present since Month 1 with incomplete resolution
- Previous outcome: partial improvement only
- Action: escalate persistent symptom for clinical review

---

## P501 — Issue Resolved Previously

**Pattern:** Skin rash fully resolved in Month 2, no recurrence  
**Status:** Active  
**Check-ins:** 4  
**Use for:** Demonstrating a fully documented resolution — agent should surface the positive outcome

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-20 | Symptom report | Mild skin rash on forearms. Referred to dermatology. |
| 2026-04-05 | Outcome | Rash fully resolved after topical treatment. Documented complete resolution. |
| 2026-05-12 | Routine | No recurrence. Stable participation. |
| 2026-09-05 | Routine | No adverse events across 6 months. Remains enrolled. |

### What the Agent Should Surface
- Prior issue: skin rash (fully resolved)
- Previous outcome: complete resolution after dermatology referral
- Pattern: no recurrence

---

## P607 — Conflicting Historical Outcome

**Pattern:** Joint pain with contradictory outcome records  
**Status:** Active  
**Check-ins:** 4  
**Use for:** Demonstrating the agent handling ambiguous/conflicting history responsibly

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-22 | Symptom report | Moderate joint pain in both knees. Referred to physical therapy. |
| 2026-04-18 | Outcome | Physical therapy completed. Participant reported improvement. **(documented as improved)** |
| 2026-05-25 | Outcome | Participant contradicts earlier record — says pain never fully resolved. **(documented as conflicting)** |
| 2026-09-07 | Symptom report | Joint pain continues. Conflicting records flagged for clinical review. |

### What the Agent Should Surface
- Conflict: earlier record says improved; later record contradicts this
- Agent should not choose one version — it should flag the discrepancy
- Action: review both source records before drawing conclusions

---

## P722 — First-Time Issue, No Prior History

**Pattern:** New symptom (shortness of breath) with no prior history in the record  
**Status:** Active  
**Check-ins:** 3  
**Use for:** Demonstrating the "no memory found" case — agent should state no relevant history

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-25 | Routine | Enrollment. No issues. |
| 2026-05-15 | Routine | Good tolerance. No problems. |
| 2026-09-08 | Symptom report | **Shortness of breath during mild activity — first ever occurrence. Referred for evaluation.** |

### What the Agent Should Surface
- No prior history of respiratory symptoms
- Agent should explicitly state: "No relevant historical memory found for this symptom"
- Action: refer for clinical evaluation as first occurrence

---

## P811 — Similar Symptom, Different Cause

**Pattern:** Nausea from skipped meals — not related to medication  
**Status:** Active  
**Check-ins:** 4  
**Use for:** Demonstrating that the agent should not equate "nausea = dosage problem" automatically

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-28 | Routine | Enrollment. No issues. |
| 2026-04-20 | Symptom report | Nausea reported. After questioning: linked to skipped meals, NOT dosage change. Meal schedule advised. |
| 2026-05-18 | Outcome | Nausea resolved with consistent meal schedule. Meal-related aetiology confirmed. |
| 2026-09-10 | Routine | No further nausea. Stable enrollment. |

### What the Agent Should Surface
- Prior nausea: meal-related, not medication-related
- Important distinction — prevents misattribution to dosage
- Action: check meal patterns before assuming medication link

---

## P905 — Multiple Benign Check-ins

**Pattern:** 6 check-ins across 6 months, no adverse events at any point  
**Status:** Active  
**Check-ins:** 6  
**Use for:** Demonstrating that the agent handles a completely clean history correctly

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-03-30 | Routine | Enrollment. No issues. |
| 2026-04-28 | Routine | No symptoms. Good tolerance. |
| 2026-05-27 | Routine | Dosage escalation — no adverse effects. |
| 2026-06-25 | Routine | Asymptomatic. No concerns. |
| 2026-07-24 | Routine | Continued good tolerance. Most compliant participant. |
| 2026-09-11 | Routine | Final Month 6 check-in. No adverse events across full 6 months. |

### What the Agent Should Surface
- No adverse history
- Pattern: consistently well-tolerated protocol
- Brief should be positive and routine

---

## P990 — Withdrawal Concern, No Medical Reason

**Pattern:** Wants to leave due to personal scheduling burden, not any symptom  
**Status:** Active  
**Check-ins:** 3  
**Use for:** Demonstrating that the agent handles withdrawal requests without a medical basis correctly

### Timeline

| Date | Event | What Happened |
|------|-------|---------------|
| 2026-04-02 | Routine | Enrollment. No adverse effects. Positive attitude. |
| 2026-05-05 | Routine | No symptoms. Mentions scheduling difficulties. |
| 2026-09-12 | Concern | **Contacts team about withdrawing. Cites personal/scheduling reasons — no medical concerns.** |

### What the Agent Should Surface
- No medical history supporting withdrawal
- No adverse events, no symptom pattern
- Agent should note absence of medical basis
- Action: document the request; discuss with appropriate team per trial protocol

---

## Summary Table

| ID | Pattern | Check-ins | Key Teaching Point |
|----|---------|-----------|-------------------|
| **P402** ⭐ | Recurring nausea after dosage | 8 | Hero demo — full historical pattern |
| P117 | No issues | 4 | Clean baseline |
| P209 | Recurring headache | 5 | Pattern across multiple events |
| P314 | Persistent fatigue | 4 | Incomplete resolution |
| P501 | Resolved rash | 4 | Positive outcome in history |
| P607 | Conflicting records | 4 | Ambiguous history handling |
| P722 | First-time symptom | 3 | No memory found case |
| P811 | Meal-related nausea | 4 | Not all nausea = dosage issue |
| P905 | All benign | 6 | Clean 6-month history |
| P990 | Non-medical withdrawal | 3 | Withdrawal without symptoms |
