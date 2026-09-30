You are the primary senior software engineer and coding agent responsible for building a complete, working hackathon project called:

# TRIALGUARD

### Hindsight-Powered Clinical Trial Participant Retention & Longitudinal Context Agent

Your task is to design, implement, test, document, and polish the project end-to-end.

Do not merely create a mockup or a superficial demo. Build a functional application in which Hindsight is genuinely used as the persistent memory layer and where the agent produces meaningfully better historical context than a memoryless baseline.

==================================================

1. HACKATHON CONTEXT
   ==================================================

The hackathon is:

"AI Agents That Learn Using Hindsight"

The official rules emphasize:

* Hindsight is mandatory.
* Persistent memory and learning from past interactions are central.
* The project should solve a real professional/business problem.
* Hindsight should be the star, not an invisible implementation detail.
* The demo should communicate the value very quickly.
* The scope should remain tight: one workflow, one persona, one clear value proposition.
* Synthetic data is acceptable.
* The submission requires a clean GitHub repository, demo video, live project demo, content deliverables, and an explanation of Hindsight usage.

Treat those requirements as hard product constraints.

==================================================
2. PRODUCT DEFINITION
=====================

TrialGuard is an AI decision-support agent for CLINICAL TRIAL COORDINATORS.

The exact problem being solved is:

Clinical-trial participants may have repeated check-ins over many weeks or months. Important longitudinal context can become fragmented across those interactions. A current issue may only become meaningful when connected with similar historical events, previous interventions, and documented outcomes.

TrialGuard uses Hindsight to remember participant interactions over time and retrieve relevant historical context when a new check-in occurs.

Core value proposition:

"Today's check-in becomes more useful when the agent remembers what happened before."

One-sentence product definition:

TrialGuard is a Hindsight-powered AI agent that helps clinical-trial coordinators identify recurring participant issues by connecting current check-ins with relevant historical interactions, interventions, and outcomes.

==================================================
3. PRIMARY PERSONA
==================

The primary user is:

Clinical Trial Coordinator

Do not turn the project into:

* a patient-facing doctor chatbot
* an autonomous medical assistant
* a diagnosis system
* a medication-prescription system
* a dropout prediction platform
* a generic clinical-trial management suite

Keep the project focused on one workflow:

CHECK-IN -> HISTORICAL MEMORY -> PATTERN/CONTEXT -> COORDINATOR ACTION BRIEF

==================================================
4. CORE DEMONSTRATION STORY
===========================

The hero participant is:

Participant P402
Trial TRIAL-001

Build a synthetic longitudinal history approximately like this:

MONTH 1:
A dosage increase is documented.
Participant reports nausea afterward.
A documented intervention is recorded.

MONTH 2:
Follow-up says symptoms improved.

MONTH 3:
Another dosage increase is documented.

MONTH 4:
Routine check-in with no major issue.

MONTH 6:
Participant reports that nausea is severe again and expresses frustration and that they are considering leaving the study.

This should create the central memory story:

WITHOUT HINDSIGHT:
The agent sees only the Month 6 check-in and produces a reasonable but generic coordinator response.

WITH HINDSIGHT:
The agent retrieves relevant Month 1, Month 2, and Month 3 historical context, identifies the similarity/temporal relationship, surfaces the documented previous outcome, and gives the coordinator a concise historical action brief.

The core contrast must be visible in the UI:

Memoryless:
Current issue -> generic contextual response

Hindsight:
Current issue -> historical memory -> temporal context -> previous outcome -> action brief

Do not intentionally make the baseline stupid. The baseline should be a reasonably competent stateless LLM that simply lacks the participant's longitudinal memory.

==================================================
5. SAFETY AND ROLE BOUNDARIES
=============================

This is a synthetic hackathon prototype for decision support.

The system must NEVER:

* diagnose a participant
* prescribe medication
* recommend a dosage increase/decrease
* tell someone to stop or continue medication
* independently change treatment
* make a clinical decision
* decide that a participant should remain in the trial
* claim that the AI prevented a dropout
* claim causation merely because two events occurred close together
* invent historical events
* invent outcomes
* present unsupported medical facts as documented facts

The system MAY:

* summarize the current check-in
* retrieve relevant historical interactions
* identify documented recurrence/similarity
* surface previously documented interventions
* surface documented outcomes
* flag information for coordinator/clinical-team review
* indicate uncertainty
* say when no relevant historical memory was found

Preferred phrasing:

"Historical context identified. Review this information with the appropriate clinical team and follow the applicable trial/site procedures."

Avoid:

"Change the dosage."

Also avoid:

"This dosage caused the nausea."

Prefer:

"Nausea was documented shortly after a dosage increase."

Add a visible application disclaimer:

"Prototype for hackathon demonstration using synthetic data. Not for clinical use or medical decision-making."

==================================================
6. TECHNOLOGY STACK
===================

Use a deliberately simple stack.

Frontend:

* HTML
* CSS
* vanilla JavaScript

Backend:

* Python
* Flask

Application database:

* SQLite

LLM:

* Groq API

Memory:

* Hindsight Cloud using the official Python client

Validation:

* Pydantic

Configuration:

* python-dotenv

Testing:

* pytest

Do NOT add:

* React
* Node.js
* Spring Boot
* Maven
* MySQL server
* Docker
* Kubernetes
* complex agent frameworks
* a second vector database
* FAISS
* Chroma
* Pinecone
* PostgreSQL/pgvector

unless there is a compelling technical reason and you first document why.

The purpose is to keep the architecture easy to explain in a hackathon demo and viva.

==================================================
7. CRITICAL HINDSIGHT REQUIREMENT
=================================

Hindsight is not a decorative integration.

Hindsight must be the actual persistent agent memory.

The minimum required lifecycle is:

RETAIN -> RECALL -> AGENT SYNTHESIS -> RETAIN OUTCOME

Every important participant interaction should be retained.

Relevant historical interactions should be recalled when analyzing a new check-in.

When a new interaction produces a meaningful documented outcome, retain that outcome so that later interactions can benefit from it.

Use timestamps because this is a longitudinal/temporal problem.

Use participant/trial scoping so one participant's history cannot leak into another participant's retrieval.

Before implementing any Hindsight method or parameter:

1. Inspect the version of hindsight-client actually installed.
2. Consult the current official Hindsight documentation if network/docs access is available.
3. Use the exact API signature supported by that version.
4. Never invent parameters or method names.
5. If an API shown in older examples differs from the current API, follow the current official API.

The MVP must rely on verified Retain and Recall functionality.

Reflect may be added later ONLY if it clearly improves the demonstration and does not replace the explicit Recall-based memory story.

==================================================
8. HINDSIGHT MEMORY DESIGN
==========================

Hindsight should receive meaningful natural-language event representations rather than opaque database dumps.

Example retained memory:

Participant: P402
Trial: TRIAL-001
Date: 2026-03-10

A dosage increase was documented.
Participant reported moderate nausea shortly afterward.
A meal-timing intervention was documented.
At follow-up, the participant reported improved symptoms.

Preserve:

* participant ID
* trial ID
* event date/time
* event type
* symptom/issue
* relevant context
* documented intervention
* documented outcome
* source/check-in identifier

Every memory should be timestamped when the source event has a timestamp.

Use stable document identifiers such as:

checkin:P402:001
checkin:P402:002

Do not generate a random new document ID every time the same logical record is written.

Use participant/trial tags where supported by the currently installed Hindsight SDK.

Preferred conceptual tags:

participant:P402
trial:TRIAL-001

For participant retrieval, use strict filtering when supported so the recall operation is scoped to the correct participant and trial.

Do not expose another participant's memories merely because the text is semantically similar.

==================================================
9. SQLITE VS HINDSIGHT RESPONSIBILITIES
=======================================

SQLite is the application's operational database.

Hindsight is the agent's long-term memory.

SQLite should store exact records such as:

* participants
* check-ins
* outcomes
* agent runs
* audit information

Hindsight should store information intended for contextual memory and retrieval.

Do not use SQLite's text search as a substitute for Hindsight.

Do not create a second vector database.

==================================================
10. DATABASE SCHEMA
===================

Create at minimum:

TABLE participants:

* id
* display_name
* trial_id
* status
* created_at

TABLE checkins:

* id
* participant_id
* occurred_at
* raw_text
* created_at

TABLE outcomes:

* id
* participant_id
* checkin_id
* occurred_at
* description
* outcome_text
* created_at

TABLE agent_runs:

* id
* checkin_id
* mode
* hindsight_query
* retrieved_memories
* final_output
* created_at

Use foreign keys and reasonable indexes.

Use parameterized SQL or a small clean database helper.

==================================================
11. PROJECT STRUCTURE
=====================

Create this structure unless the existing repository requires a small adjustment:

TrialGuard/
|
|-- app.py
|-- agent.py
|-- hindsight_service.py
|-- groq_service.py
|-- db.py
|-- models.py
|-- prompts.py
|-- seed_demo.py
|
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
|
|-- data/
|   |-- .gitkeep
|
|-- templates/
|   |-- base.html
|   |-- dashboard.html
|   |-- participant.html
|   |-- checkin.html
|   |-- result.html
|
|-- static/
|   |-- style.css
|   |-- script.js
|
|-- tests/
|   |-- test_db.py
|   |-- test_hindsight.py
|   |-- test_agent.py
|   |-- test_safety.py
|   |-- test_isolation.py
|   |-- test_temporal.py
|   |-- test_baseline_vs_hindsight.py

Keep responsibilities separated.

==================================================
12. HINDSIGHT SERVICE
=====================

Create hindsight_service.py.

It should encapsulate Hindsight operations.

Required functions conceptually:

retain_checkin(...)
recall_patient_history(...)
retain_outcome(...)

Do not scatter raw Hindsight API calls throughout the Flask routes.

The Hindsight service should:

* construct the client
* load configuration
* retain memories
* recall memories
* normalize Hindsight results into an application-friendly structure
* handle Hindsight errors cleanly

Do not hide Hindsight behind a fake local implementation.

The real API must actually be called when configured.

For development without credentials, provide an explicit configuration error/fallback message rather than pretending that memory was used.

==================================================
13. GROQ / AGENT LAYER
======================

Create agent.py and groq_service.py.

Implement a real agentic loop.

Desired architecture:

Current check-in
->
Agent LLM
->
tool call: recall_patient_history
->
Hindsight Recall
->
retrieved historical context
->
LLM final synthesis
->
structured action brief

The agent may decide whether historical context is needed, but for the core TrialGuard workflow, the system should strongly encourage historical retrieval for recurring issues and participant check-ins.

The LLM tool should conceptually be:

recall_patient_history(
participant_id,
trial_id,
query,
current_timestamp
)

The backend, not the model, must enforce the authoritative participant_id and trial_id from the HTTP request/context.

Never trust an LLM-provided participant ID for access control.

==================================================
14. AGENT SYSTEM PROMPT
=======================

Create a versioned prompt in prompts.py.

The system prompt must establish:

You are TrialGuard, an AI decision-support agent for clinical-trial coordinators.

Your job is to analyze a participant's current check-in and use Hindsight memory to retrieve relevant historical context.

Rules:

1. Ground historical claims in retrieved evidence.
2. Clearly distinguish current information from historical information.
3. Prefer documented facts over assumptions.
4. If no relevant memory is retrieved, say so.
5. Do not invent history.
6. Do not infer causality from sequence alone.
7. Do not diagnose.
8. Do not prescribe or change dosage.
9. Do not determine trial eligibility or continuation.
10. Surface relevant historical information to the coordinator.
11. Escalate urgent safety concerns according to applicable site/trial procedures.
12. Explicitly communicate uncertainty or conflicting records.
13. The output is coordinator decision support, not medical advice.

Do not hardcode P402 behavior in the prompt.

The same logic must work for every synthetic participant.

==================================================
15. STRUCTURED FINAL OUTPUT
===========================

The final result should be structured.

Use a Pydantic model and, where compatible with the chosen Groq model/API, use structured output/schema validation.

Desired fields:

current_issue
participant_concern
historical_matches[]
historical_pattern
previous_outcome
coordinator_action
safety_note
memory_used
memory_count
uncertainty

Example:

{
"current_issue": "Recurring nausea",
"participant_concern": "Participant is considering leaving the study",
"historical_matches": [
{
"date": "2026-03-10",
"event": "Nausea documented after dosage increase",
"relevance": "Similar issue in the participant's history"
}
],
"historical_pattern": "A similar issue was previously documented following a dosage increase.",
"previous_outcome": "The subsequent record documented symptom improvement.",
"coordinator_action": "Review the historical context and previous outcome with the appropriate clinical team.",
"safety_note": "This system does not diagnose or prescribe treatment.",
"memory_used": true,
"memory_count": 3,
"uncertainty": "Historical records should be reviewed before drawing clinical conclusions."
}

Do not fabricate confidence percentages.

==================================================
16. BASELINE MODE
=================

Implement two analysis modes:

baseline
hindsight

BASELINE:
Current check-in -> LLM -> output

HINDSIGHT:
Current check-in -> LLM/tool call -> Hindsight -> historical context -> LLM -> output

The baseline must NOT access Hindsight.

The Hindsight mode MUST access Hindsight.

The UI should make this comparison easy to demonstrate.

Do not intentionally sabotage the baseline.

==================================================
17. MEMORY TRACE / EXPLANATION
==============================

The result screen must visibly show that Hindsight was actually used.

Display something like:

MEMORY STATUS
Hindsight queried
3 relevant memories retrieved
Historical context used
Current interaction retained

Also show an expandable:

"Retrieved Historical Memories"

Each memory should show, where available:

* date
* short text/summary
* source/document ID
* relevance/context

If the SDK exposes source chunks or provenance, preserve and display them appropriately.

Do not fabricate source IDs.

==================================================
18. TEMPORAL REASONING
======================

This is fundamentally a temporal memory project.

Use event timestamps.

The current check-in date should be passed to Hindsight in the correct way supported by the installed SDK.

The recall query should explicitly seek information such as:

* previous occurrences
* earlier related symptoms/issues
* earlier dosage events
* documented interventions
* documented outcomes
* prior withdrawal/frustration concerns
* events that occurred before the current check-in

The agent should understand language such as:

* previously
* earlier
* last month
* after the prior dosage change
* recurring
* returned
* improved
* persisted

Do not fake temporal retrieval in application code.

==================================================
19. MEMORY RETENTION DESIGN
===========================

Retain meaningful events, not every UI detail.

Examples:

CHECK-IN MEMORY:
Participant P402 reported nausea after a dosage increase.

OUTCOME MEMORY:
At follow-up, P402 reported improved symptoms after the previously documented intervention.

Important:
Store outcomes because the important memory relationship is:

problem -> intervention -> outcome

not merely:

problem -> problem -> problem

The outcome is what makes later recall useful.

==================================================
20. SYNTHETIC DATASET
=====================

Build a deterministic demo dataset.

Create approximately:

* 10 participants
* 4-6 months of history
* roughly 40-60 check-ins/events

Do not use real patient information.

Create different patterns deliberately.

At minimum:

P402:
Recurring nausea linked temporally to dosage events with a documented prior improvement.

P117:
No useful historical match for the current issue.

P209:
Recurring headache pattern.

P311:
Similar symptom but a different documented context, so the agent must not overgeneralize.

P607:
Conflicting historical outcomes.

P722:
First occurrence of an issue.

P811:
Historically similar words but unrelated event.

The remaining participants can have realistic routine events.

The dataset must be deterministic so the same demo can always be reproduced.

==================================================
21. DO NOT HARDCODE THE HERO RESULT
===================================

Absolutely do NOT write logic such as:

if participant_id == "P402":
return hardcoded historical result

or:

if symptom == "nausea":
return a prewritten answer

The actual result must emerge from:

* stored data
* Hindsight retrieval
* agent reasoning

The P402 story is a DATA FIXTURE, not a CODE PATH.

==================================================
22. NO-MEMORY CASE
==================

Support a case in which Hindsight returns no relevant historical memory.

The system must say:

"No relevant historical memory was found for this participant and issue."

Do not claim this proves the issue has never happened unless the application has complete verified records establishing that.

==================================================
23. CONFLICTING MEMORY CASE
===========================

If historical records conflict, do not choose a convenient answer.

Example:

Month 1:
Symptoms improved.

Month 2:
Symptoms persisted.

The output should say that the historical records contain differing reports and should be reviewed.

==================================================
24. URGENT SAFETY CASE
======================

Add a safety test case for urgent language.

For example:

* severe breathing difficulty
* collapse
* immediate emergency concern

The system must prioritize:
"Follow the applicable emergency/escalation procedure and involve appropriate clinical personnel."

It must not search historical memory and then provide a treatment recommendation as though history overrides an urgent situation.

Historical information may still be shown as context if appropriate, but emergency escalation must take precedence.

==================================================
25. DETERMINISTIC SAFETY VALIDATOR
==================================

Implement a lightweight safety validation layer after the LLM result and before displaying the final result.

The validator should detect dangerous or prohibited output patterns such as:

* change dosage
* increase dosage
* decrease dosage
* stop medication
* start medication
* diagnose
* prescribe
* definitely caused by

If an unsafe output is detected:

* do not display it as the final recommendation
* replace the action portion with a safe review/escalation instruction
* log that the validator intervened

This is a guardrail, not a medical safety certification.

==================================================
26. FLASK ROUTES
================

Implement at minimum:

GET /
GET /dashboard
GET /participants/<participant_id>
GET /participants/<participant_id>/checkin
POST /participants/<participant_id>/analyze
GET /runs/<run_id>

Use appropriate validation and error handling.

==================================================
27. UI REQUIREMENTS
===================

Keep the UI professional, clean, and simple.

Do NOT create a giant enterprise dashboard.

PAGE 1:
Dashboard

Show:

* TrialGuard title
* active participants
* recent check-ins
* detected historical-pattern count based on actual application data where possible
* link to start a check-in

PAGE 2:
Participant Timeline

Show:

* participant ID
* trial ID
* current status
* chronological history

Clearly distinguish:
CURRENT
HISTORICAL

PAGE 3:
Check-in

Fields:

* participant
* date/time
* check-in text
* analyze button

Include a clear synthetic-data disclaimer.

PAGE 4:
Analysis Result

Sections:

CURRENT CHECK-IN

HINDSIGHT MEMORY

* memory queried
* number retrieved
* historical memory cards

HISTORICAL PATTERN

PREVIOUS DOCUMENTED OUTCOME

COORDINATOR ACTION BRIEF

SAFETY / UNCERTAINTY

Also include:
[Compare with Memoryless Baseline]

The result page must be optimized for the 60-second hackathon demo.

==================================================
28. UI MEMORY VISUALIZATION
===========================

Make the memory story visually obvious:

CURRENT CHECK-IN
|
v
HINDSIGHT RECALL
|
v
3 HISTORICAL MEMORIES
|
v
TEMPORAL / RELATED PATTERN
|
v
COORDINATOR ACTION BRIEF

Do not use unnecessary animations.

Do not create a fake animation pretending that Hindsight did something it did not do.

Only display actual retrieved memories and actual status.

==================================================
29. AUDITABILITY
================

For every agent run, save enough information to understand:

* current check-in
* Hindsight query
* retrieved memory IDs/source identifiers when available
* retrieved memory text/summary
* final generated output
* safety validator result
* timestamp
* mode: baseline or hindsight

The application should make it possible to answer:

"Why did TrialGuard generate this result?"

==================================================
30. ERROR HANDLING
==================

Handle at least:

* invalid participant
* empty check-in
* invalid timestamp
* Hindsight API unavailable
* Hindsight authentication failure
* Groq API unavailable
* tool-calling failure
* malformed structured response
* empty memory result
* conflicting evidence
* safety-validator intervention

Never silently pretend that an external service worked.

If Hindsight failed, say:
"Historical memory service unavailable. No historical context was used."

==================================================
31. LOGGING
===========

Add clean server-side logging for:

* Hindsight retain errors
* Hindsight recall errors
* Groq errors
* validation errors
* safety validator interventions

Do not log API keys.

Do not log secrets.

Do not claim that a memory operation succeeded unless the API response confirms success.

==================================================
32. TESTING REQUIREMENTS
========================

Create real automated tests.

At minimum:

TEST 1:
Database creation and CRUD.

TEST 2:
Hindsight retain function forms the correct event representation.

TEST 3:
Hindsight recall is called with participant/trial scope.

TEST 4:
Participant isolation:
P402 retrieval cannot return P207 data.

TEST 5:
Temporal query behavior is correctly configured.

TEST 6:
No-memory case.

TEST 7:
Conflicting-memory case.

TEST 8:
Baseline mode never calls Hindsight.

TEST 9:
Hindsight mode calls Hindsight.

TEST 10:
Unsafe generated recommendation is blocked by safety validator.

TEST 11:
Urgent safety language triggers escalation-oriented handling.

TEST 12:
Malformed model output is rejected/falls back safely.

Use mocks for external APIs where appropriate.

Also provide at least one optional integration test that can run when API credentials are available.

==================================================
33. MEMORY QUALITY EVALUATION
=============================

Create a small evaluation fixture.

For each test case specify:

* input check-in
* expected relevant historical records
* whether a pattern is expected
* expected outcome context
* participant scope
* safety expectation

Measure at least conceptually:

* correct historical event retrieval
* correct participant isolation
* correct temporal context
* correct use of previous outcomes
* correct uncertainty handling

Do not invent fake benchmark scores.

==================================================
34. DEVELOPMENT SCRIPTS
=======================

Create:

seed_demo.py

It should:

1. initialize the database
2. create deterministic participants
3. insert synthetic check-ins
4. retain relevant memory in Hindsight when configured
5. print a clear success/failure summary

Create a simple command or script to test Hindsight connectivity.

Create a command or script to exercise the P402 recall scenario.

==================================================
35. ENVIRONMENT
===============

Create .env.example with placeholders such as:

HINDSIGHT_BASE_URL=
HINDSIGHT_API_KEY=
HINDSIGHT_BANK_ID=
GROQ_API_KEY=

Do not commit .env.

Do not expose secrets in source control.

Use environment variables throughout.

==================================================
36. HINDSIGHT BANK
==================

The application should use a dedicated bank for TrialGuard.

On initial setup, document whether the bank needs to be created manually or whether the application can safely create/verify it through the current Hindsight SDK.

Do not silently create duplicate banks every time the application starts.

Use a stable bank identifier.

==================================================
37. README REQUIREMENTS
=======================

Create a professional README containing:

1. Project title
2. Problem
3. Solution
4. Why Hindsight is necessary
5. Architecture
6. Technology stack
7. Hindsight Retain flow
8. Hindsight Recall flow
9. Agent/tool-calling flow
10. SQLite vs Hindsight responsibilities
11. Synthetic data explanation
12. Safety boundaries
13. Baseline vs Hindsight comparison
14. Local setup
15. Environment variables
16. How to seed demo data
17. How to run
18. How to run tests
19. Demo walkthrough
20. Known limitations
21. Hackathon submission notes

Include a simple architecture diagram in Markdown.

==================================================
38. README HINDSIGHT EXPLANATION
================================

The README must make this extremely explicit:

SQLite = exact application records

Hindsight = persistent agent memory

Groq = reasoning/generation

Core lifecycle:

RETAIN
-> RECALL
-> SYNTHESIS
-> RETAIN OUTCOME
-> FUTURE RECALL

Explain that the system is not simply doing keyword search over a database.

Explain that Hindsight is central because the current check-in becomes useful through relevant historical context.

==================================================
39. HACKATHON DEMO MODE
=======================

Implement the application so that the hero scenario can be demonstrated quickly.

Demo sequence:

1. Open P402.
2. Show Month 1 and Month 3 history.
3. Submit Month 6 check-in:
   "I'm having severe nausea again and I'm thinking about leaving the study."
4. Click Analyze.
5. Show "Hindsight queried."
6. Show retrieved historical memories.
7. Show the historical pattern.
8. Show previous documented outcome.
9. Show coordinator action brief.
10. Compare with memoryless baseline.

The demo should fit naturally into approximately 60 seconds.

==================================================
40. HINDSIGHT MUST BE VISIBLE
=============================

A judge should never have to guess whether Hindsight is actually being used.

The UI and README should clearly demonstrate:

* a real Retain
* a real Recall
* retrieved historical memories
* use of timestamps
* participant/trial scoping
* new outcome retained for future interactions

Do not simply put the word "Hindsight" in the UI.

==================================================
41. CONTENT QUALITY
===================

Use professional language.

Avoid marketing exaggerations such as:

* "saves the patient"
* "guarantees retention"
* "prevents dropout"
* "solves a $50M problem"
* "medical-grade AI"
* "100% accurate"

Prefer defensible claims such as:

* "supports participant-retention workflows"
* "surfaces historical context"
* "identifies recurring documented patterns"
* "provides coordinator-facing decision support"

==================================================
42. NO UNSUPPORTED BUSINESS NUMBERS
===================================

Do not invent dollar values, dropout percentages, cost savings, clinical performance statistics, or adoption statistics.

If the repository needs business context, use qualitative wording unless a source is explicitly included.

==================================================
43. NO REAL PATIENT DATA
========================

All patient/participant information must be synthetic.

Make the synthetic nature explicit in:

* README
* UI disclaimer
* demo documentation

==================================================
44. CODE QUALITY
================

Follow clean Python practices.

Use:

* type hints
* small functions
* meaningful names
* clear separation of concerns
* environment configuration
* exception handling
* comments where they explain non-obvious logic

Do not over-engineer.

Do not build unnecessary abstractions.

Do not duplicate code.

==================================================
45. SECURITY BASICS
===================

Implement:

* secret handling through environment variables
* parameterized database access
* basic input validation
* no secret logging
* participant ID enforcement server-side
* safe HTML escaping/Jinja usage
* no arbitrary code execution
* no trust in raw LLM tool arguments for authorization

==================================================
46. IMPLEMENTATION ORDER
========================

Do not build everything at once blindly.

Work in this order:

PHASE 1
Inspect the repository and existing files.

PHASE 2
Set up Python environment/dependencies.

PHASE 3
Verify current Hindsight client API.

PHASE 4
Implement Hindsight connection.

PHASE 5
Implement retain and recall.

PHASE 6
Seed P402 and a small synthetic dataset.

PHASE 7
Test Hindsight retrieval and participant isolation.

PHASE 8
Implement SQLite layer.

PHASE 9
Implement Groq agent and tool calling.

PHASE 10
Implement structured output.

PHASE 11
Implement safety validator.

PHASE 12
Implement baseline mode.

PHASE 13
Implement Flask routes.

PHASE 14
Implement UI.

PHASE 15
Implement audit/memory trace.

PHASE 16
Implement automated tests.

PHASE 17
Run full test suite.

PHASE 18
Run the complete P402 demo.

PHASE 19
Polish README and repository.

PHASE 20
Perform final architecture/rules audit.

Do not skip the core memory testing before building UI polish.

==================================================
47. HOW TO WORK AS CODEX
========================

At the beginning:

1. Inspect all existing repository files.
2. Identify what is already implemented.
3. Reuse working code where appropriate.
4. Do not destroy useful work unnecessarily.
5. Create/update an implementation plan.
6. Identify any existing conflicts with the specification.

Then implement incrementally.

After every meaningful stage:

* run relevant tests
* run the application or a focused script
* inspect errors
* fix them
* do not assume success because a command returned superficially successful output

Use the current installed library/API signatures.

When an API is uncertain, verify it rather than guessing.

==================================================
48. DO NOT ASK FOR CLARIFICATION UNLESS ABSOLUTELY NECESSARY
============================================================

Make sensible implementation decisions based on this specification.

Do not repeatedly ask me to choose between trivial alternatives.

If a technology/API detail is uncertain:

* inspect the repository
* inspect installed package information
* inspect official documentation if available
* choose the simplest defensible implementation

Only stop for clarification if a required credential or genuinely missing external dependency makes implementation impossible.

==================================================
49. ACCEPTANCE CRITERIA
=======================

The project is NOT complete until all of these are true:

CORE:
[ ] Flask application runs
[ ] SQLite works
[ ] Hindsight connection works when configured
[ ] Groq connection works when configured

HINDSIGHT:
[ ] Retain works
[ ] Recall works
[ ] timestamps are used
[ ] participant/trial scope is enforced
[ ] historical outcomes are retained
[ ] real historical memories appear in the demo

AGENT:
[ ] tool calling works
[ ] agent uses Hindsight
[ ] final answer is structured
[ ] no hardcoded P402 result
[ ] baseline is genuinely memoryless

SAFETY:
[ ] no diagnosis
[ ] no prescription
[ ] no autonomous dosage changes
[ ] no unsupported causal claims
[ ] urgent safety handling exists
[ ] uncertainty/conflicting evidence is handled

UI:
[ ] dashboard
[ ] participant timeline
[ ] check-in form
[ ] result page
[ ] Hindsight memory display
[ ] baseline comparison
[ ] disclaimer

TESTING:
[ ] unit tests pass
[ ] isolation test passes
[ ] no-memory test passes
[ ] conflicting-history test passes
[ ] safety test passes
[ ] baseline/hindsight comparison test passes

DOCUMENTATION:
[ ] README complete
[ ] architecture explained
[ ] Hindsight usage explained
[ ] local setup explained
[ ] environment variables documented
[ ] demo sequence documented

==================================================
50. FINAL SELF-AUDIT
====================

Before declaring completion, perform a final audit against the hackathon criteria:

INNOVATION:
Does this go beyond a generic chatbot?

HINDSIGHT MEMORY:
Is Hindsight central to the value proposition?
Can the demo show that memory changes the result?

TECHNICAL IMPLEMENTATION:
Is the code functional, clean, testable, and resilient?

USER EXPERIENCE:
Can a judge understand the workflow quickly?

REAL-WORLD IMPACT:
Is the workflow clearly relevant to a professional user?

Also verify:

* one persona
* one workflow
* one clear value proposition
* synthetic data
* no fake claims
* no fake memory
* no hardcoded hero result
* real Hindsight integration

==================================================
51. FINAL OUTPUT FROM YOU
=========================

When the implementation is complete, report:

1. What was built
2. Final architecture
3. Important files
4. How Hindsight is used
5. How to configure API keys
6. How to seed demo data
7. How to start the application
8. How to run tests
9. Exact P402 demo steps
10. Any limitations or items that remain manual
11. A final hackathon-alignment audit

Do not merely tell me "done."

Show evidence:

* tests run
* important commands
* important integration checks
* any known failures

The finished project must be a real, reproducible hackathon prototype whose defining behavior is:

CURRENT CHECK-IN
+
HINDSIGHT LONG-TERM MEMORY
↓
RELEVANT HISTORICAL CONTEXT
↓
DOCUMENTED PATTERN / OUTCOME
↓
COORDINATOR ACTION BRIEF
↓
NEW OUTCOME RETAINED FOR FUTURE MEMORY

This memory loop is the heart of TrialGuard.
Do not let secondary features overshadow it.

