# TrialGuard — LinkedIn Post

> Copy and paste one of these posts. Edit [brackets] with your actual links and details.

---

## Post Option 1 — Story-driven (Recommended)

---

A clinical trial coordinator walks into Month 6 with a participant reporting severe nausea and considering withdrawal.

Without AI memory: "Participant reports discomfort. Follow applicable procedures."

With Hindsight memory: "This is the third time nausea has followed a dosage increase for this participant. A meal-timing intervention documented in Month 1 was associated with improvement. Here is the exact historical context for your clinical team review."

Same current information. Completely different response.

That's the core idea behind TrialGuard — a project I built for the Hindsight Memory Hackathon.

**The problem:** LLMs are stateless. A six-month clinical trial generates months of documented interactions, dosage changes, interventions, and outcomes — but a conventional AI assistant sees only today's message.

**The solution:** Hindsight as the long-term memory layer. Every participant check-in is retained with participant isolation tags and timestamps. When a new check-in arrives, the agent retrieves the full longitudinal history using semantic + keyword + graph + temporal retrieval — then generates a structured Coordinator Action Brief grounded in documented memory.

**What I built:**
→ Flask backend with a two-stage agentic loop (tool-calling + structured JSON output via Groq)
→ Participant isolation enforced server-side with `tags_match="all_strict"` — no cross-participant leakage possible
→ Deterministic safety validator blocking diagnosis, dosage changes, and causal overclaims before any output reaches the screen
→ 10 synthetic participants covering deliberate edge cases (conflicting records, first-time symptoms, unrelated similar symptoms)
→ 144 automated tests

The punchline of the demo is simple:

"Without memory, the agent sees today's complaint. With Hindsight, it understands the history behind it."

GitHub: [YOUR_GITHUB_LINK]
Live demo: [YOUR_DEMO_LINK]

#AI #MachineLearning #Hackathon #Python #Flask #ClinicalTrials #Hindsight #Groq #LLM #AgentAI #HealthTech

---

## Post Option 2 — Technical (for engineering audience)

---

Just shipped TrialGuard for the Hindsight Memory Hackathon — a clinical trial coordinator AI assistant built on persistent semantic memory.

**Architecture highlights:**

Two-stage agent pipeline (Groq):
- Stage 1: Tool-calling LLM decides whether to query Hindsight
- Stage 2: Structured JSON output generates a validated CoordinatorBrief

Participant isolation:
- Every memory tagged `participant:P402` + `trial:TRIAL-001`
- All recalls use `tags_match="all_strict"` — server-enforced, not a client filter
- Participant ID always comes from the URL path, never from LLM output or form data

Safety layer (deterministic, not prompt-based):
- Regex validator blocks dosage changes, diagnosis claims, causal overclaims
- Urgent language (chest pain, breathing difficulty) bypasses LLM entirely
- Violations replace fields with safe fallbacks before they reach the UI

Learning loop:
- After each analysis, the agent brief is retained back into Hindsight
- Future queries retrieve previous analyses as part of historical context

The key architectural decision: Hindsight IS the memory layer. No separate vector database. Adding FAISS or Chroma would obscure the point of the project — that Hindsight's combination of semantic + keyword + graph + temporal retrieval makes it genuinely different from a similarity search.

144 tests. 10 synthetic participants. Fully documented.

GitHub: [YOUR_GITHUB_LINK]

#Python #Flask #AI #Hindsight #Groq #LLM #AgentArchitecture #Hackathon #HealthTech

---

## Post Option 3 — Short & punchy (for engagement)

---

Built an AI that helps clinical trial coordinators remember what happened to a patient six months ago.

Most LLMs are stateless. The history is in the notes. The insight is in connecting them.

TrialGuard uses Hindsight memory to retrieve longitudinal participant history and generate a structured action brief — grounded in documented events, not guesswork.

The demo: same complaint, two modes.

Without memory → generic response.
With Hindsight → "This happened in Month 1. Here's what worked."

That difference is the product.

[YOUR_GITHUB_LINK] | Built for the Hindsight Hackathon

#AI #Hackathon #Python #HealthTech #LLM

---

## Best Time to Post

- Tuesday–Thursday, 8–10am or 12–2pm in your timezone tend to get the best LinkedIn engagement
- Post the story-driven version (Option 1) for maximum reach
- Tag Hindsight / Vectorize in the post if you can find their LinkedIn page
- Add 1–2 screenshots of the result page showing the memory status indicator and historical matches

## What to Attach

1. A screenshot of the P402 result page (hindsight mode) showing "✓ Hindsight queried — X memories retrieved"
2. A screenshot of the memory trace page showing the retrieved document IDs
3. Optional: a short screen recording of the baseline vs hindsight comparison
