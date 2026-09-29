# TrialGuard — Technical Writeup

**Hackathon Submission | Hindsight Memory Hackathon**
**Project:** TrialGuard — AI-Powered Clinical Trial Coordinator Support
**Stack:** Python · Flask · Hindsight Cloud · Groq · SQLite · Pydantic

---

## The Problem

Clinical trial coordinators manage participants across months of interactions. Each visit, symptom report, dosage change, or intervention is documented — but rarely connected longitudinally at the point of need. When a participant arrives at their Month 6 check-in with severe nausea and withdrawal concerns, the coordinator faces a critical question: is this new, or have we seen this before?

The stateless nature of conventional LLM assistants makes them inadequate here. Without persistent memory, an AI sees only today's complaint. It cannot surface the Month 1 dosage increase, the subsequent nausea episode, the meal-timing intervention that resolved it, or the second dosage escalation in Month 3. That context is precisely what makes the difference between a generic response and an actionable brief grounded in documented history.

TrialGuard solves this by placing Hindsight at the centre of the agent architecture.

---

## How Hindsight Is Used

Every participant interaction is retained in Hindsight with a stable document ID (`checkin:P402:001`), an ISO 8601 timestamp for temporal retrieval, and two critical tags: `participant:P402` and `trial:TRIAL-001`. All recalls use `tags_match="all_strict"` — a hard server-side constraint that makes cross-participant data leakage physically impossible at the retrieval layer.

When a new check-in arrives, the agent executes a two-stage pipeline. In Stage 1, a tool-calling LLM call decides whether historical context is relevant. If so, it invokes `recall_patient_history()` with a longitudinal query such as: *"Find previous nausea, dosage changes, interventions and outcomes for this participant."* Hindsight combines semantic, keyword, graph, and temporal retrieval — returning ranked memories that span months of history in a single call.

In Stage 2, the retrieved memories are injected into a second structured-output LLM call. The model generates a validated JSON object (a `CoordinatorBrief`) containing: the current issue, any withdrawal concern, historical matches with dates and relevance, an identified pattern, the previous documented outcome, and a recommended coordinator action. This structured output makes the UI deterministic and testable.

After each analysis, the agent's brief is retained back into Hindsight as an outcome memory (`outcome:<run_id>`). This closes the learning loop: future queries for the same participant will also retrieve previous analyses, making the system progressively more useful with each interaction.

---

## Architecture

The stack is deliberately minimal. Flask handles routing and serves Jinja2 templates. SQLite stores exact application records — the audit trail of participants, check-ins, and agent runs. Hindsight handles semantic long-term memory. Groq provides the LLM. There is no separate vector database: Hindsight is the memory layer, and adding another retrieval system would obscure its role.

The Flask route `/participants/<id>/analyze` enforces a critical security constraint: the participant ID is taken from the URL path and passed directly to the agent — it is never read from form data or from any LLM-generated output. This prevents a compromised or misdirected model from redirecting a recall query to a different participant's memories.

A deterministic safety validator sits between the LLM and the UI. Using regex pattern matching, it scans every field of the generated brief for prohibited content: dosage modification instructions, prescription directives, diagnosis claims, causal overclaims, and outcome guarantees. Any violation replaces the field with a safe fallback before it reaches the coordinator's screen. This layer cannot be hallucinated out of existence — it is code, not a prompt instruction.

An additional fast-path handles urgent language. If the check-in text contains patterns such as "chest pain", "can't breathe", or "emergency help", the LLM pipeline is bypassed entirely and an emergency escalation notice is returned immediately.

---

## The Demo

The demo centres on Participant P402, a synthetic participant with a deliberate six-month story: two dosage escalations, nausea episodes, a meal-timing intervention that worked, and a Month 6 return of nausea with withdrawal concerns. The baseline mode shows the agent responding competently to today's complaint with no historical context. The Hindsight mode surfaces the Month 1 nausea, the successful intervention, and the recurring pattern — and connects them explicitly to the current complaint. The contrast is the product story.

Ten synthetic participants cover distinct scenarios: clean history (P117), recurring headache pattern (P209), persistent fatigue (P314), fully resolved issue (P501), conflicting records (P607), first-time symptom with no history (P722), similar symptom from a different cause (P811), six clean check-ins (P905), and withdrawal concern with no medical basis (P990). This variety demonstrates that the system handles edge cases — not just the hero path.

---

## Technical Decisions

The two-stage agent architecture — tool-calling separated from structured output — reflects a current constraint in Groq's API: tool use and structured JSON output cannot be combined in a single request. Rather than working around this with prompt engineering, the separation is made explicit and architectural: Stage 1 is responsible for deciding what to retrieve; Stage 2 is responsible for generating the structured response. This separation makes each stage independently testable.

The test suite covers 144 tests across 8 files, including explicit participant isolation tests, safety validator pattern tests, agent pipeline mocking, SQLite roundtrip tests, and end-to-end Flask route tests. All tests run without a live Hindsight server or Groq key — every external call is mocked. This allows the test suite to run reliably in CI without credentials.

---

## What This Demonstrates About Hindsight

TrialGuard demonstrates three properties of Hindsight that distinguish it from a vector database. First, temporal retrieval: memories carry timestamps and Hindsight can reason about before/after relationships, enabling queries like "what happened to P402 before Month 6 regarding nausea." Second, entity-aware memory: Hindsight extracts structured facts from retained text rather than storing raw embeddings, which is why a query about "nausea and dosage changes" retrieves the correct Month 1 episode even though the text is phrased differently. Third, tag-based isolation: the `all_strict` tag matching provides participant-level memory scoping with server-side enforcement — not just a client-side filter.

The result is an agent that genuinely becomes more useful with each interaction, without requiring any custom training, fine-tuning, or retrieval infrastructure beyond Hindsight itself.

---

## Conclusion

TrialGuard addresses a real gap in longitudinal context management for clinical trial coordinators. By placing Hindsight at the centre of the agent architecture, it demonstrates that persistent semantic memory can be the primary differentiator between a stateless LLM assistant and a system that understands the history behind the complaint. The architecture is minimal, the safety constraints are deterministic, and the demo is reproducible. The full implementation — 144 tests, 10 participants, complete documentation — is available at the GitHub repository.

---

*Word count: approximately 980 words*

**Links:**
- GitHub Repository: `https://github.com/YOUR_USERNAME/TrialGuard`
- Live Demo: `https://YOUR_DEPLOYMENT_URL`
- Hindsight Cloud: `https://hindsight.vectorize.io`
