# TrialGuard — Project Prompt

TrialGuard is a Flask-based AI assistant that helps patients and caregivers understand clinical trials. It uses the Hindsight semantic memory system to store and recall trial information, and the Groq LLM API for natural language generation.

## Section 11 — Directory Structure

```
TrialGuard/
├── app.py                  # Flask application entry point
├── agent.py                # Core agent logic (LLM + memory integration)
├── memory.py               # Hindsight client wrapper
├── requirements.txt
├── .env
├── .env.example
├── data/                   # Persistent data files (trial JSON exports, etc.)
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
└── tests/                  # Pytest test suite
```

## Section 35 — Environment Variables

All configuration is passed via environment variables. Required keys:

| Variable              | Description                                      |
|-----------------------|--------------------------------------------------|
| `HINDSIGHT_BASE_URL`  | Base URL of the Hindsight server (e.g. http://localhost:8888) |
| `HINDSIGHT_API_KEY`   | API key for authenticating with Hindsight        |
| `HINDSIGHT_BANK_ID`   | Memory bank ID scoping all trial data            |
| `GROQ_API_KEY`        | Groq API key for LLM completions                 |

## Project Goals

- Ingest clinical trial documents into Hindsight memory banks.
- Allow users to query trials via natural language chat.
- Surface eligibility criteria, phase information, and sponsor details.
- Provide structured summaries and Q&A grounded in stored memory.
