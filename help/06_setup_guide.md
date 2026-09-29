# TrialGuard — Setup Guide

> Complete installation and configuration from scratch.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | 3.13 confirmed working |
| pip | any recent | included with Python |
| Hindsight Cloud account | — | https://hindsight.vectorize.io |
| Groq account | — | https://console.groq.com |
| Internet connection | — | for Hindsight Cloud + Groq API |

---

## Step 1 — Clone / Open the Project

The project folder is:
```
c:\Users\Abdullah Hamdan\Desktop\hackathons\TrialGuard\
```

---

## Step 2 — Install Dependencies

All dependencies are already installed in your environment. If you ever need to reinstall:

```powershell
pip install -r requirements.txt
```

Dependencies (pinned):
```
flask==3.1.3
python-dotenv==1.2.3
requests==2.34.2
groq==1.7.0
hindsight-client==0.10.1
pytest==9.1.1
pydantic (installed with groq)
```

---

## Step 3 — Configure Environment Variables

The `.env` file in the project root contains all credentials. It should look like this:

```env
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=hsk_xxxxxxxxxxxxxxxxxxxx
HINDSIGHT_BANK_ID=trialguard_id
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

Your current `.env` is already configured. If you ever need to reset it:

```powershell
Copy-Item .env.example .env
# Then edit .env with your keys
```

### Getting a Hindsight API Key
1. Go to https://hindsight.vectorize.io
2. Create an account or log in
3. Create a new memory bank — name it `trialguard_id` (or anything, then update `.env`)
4. Create an API key in the dashboard
5. Copy the key — it is shown only once

### Getting a Groq API Key
1. Go to https://console.groq.com
2. Create an account or log in
3. Go to API Keys → Create new key
4. Copy the key

---

## Step 4 — Initialise the Database

```powershell
python seed_db.py
```

This creates `data/trialguard.db` and inserts all 10 participants. You will see a confirmation table.

---

## Step 5 — Seed Hindsight Memory

```powershell
python seed_demo.py
```

This stores all participant check-in histories into the Hindsight cloud bank. Takes about 2–3 minutes (one API call per check-in, 45 total).

To seed only P402 (faster, sufficient for the demo):
```powershell
python seed_demo.py --participant P402
```

---

## Step 6 — Start the App

```powershell
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Open **http://127.0.0.1:5000** — you should see the dashboard with 10 participants and Hindsight showing as connected.

---

## Startup Checklist

Before a demo session, verify:

- [ ] `.env` file exists with all 4 variables set
- [ ] `python seed_db.py` has been run (dashboard shows 10 participants)
- [ ] `python seed_demo.py --participant P402` has been run (P402 history in Hindsight)
- [ ] `python app.py` is running
- [ ] Dashboard shows "Hindsight memory connected"
- [ ] P402 timeline shows 0 check-ins (expected — check-ins come from form submissions)

---

## Project File Structure

```
TrialGuard/
├── app.py              # Flask web application
├── agent.py            # Groq LLM agent (two-stage pipeline)
├── memory.py           # Hindsight client wrapper
├── db.py               # SQLite database layer
├── models.py           # Pydantic output schema
├── safety.py           # Safety validator
├── seed_demo.py        # Seed Hindsight with participant histories
├── seed_db.py          # Seed SQLite with participant records
├── demo_p402.py        # Terminal demo script
├── requirements.txt    # Python dependencies
├── .env                # Live credentials (NOT in git)
├── .env.example        # Template (safe to share)
├── .gitignore
│
├── data/
│   ├── demo_data.json      # 10 participants, 45 check-ins
│   └── trialguard.db       # SQLite database (created on first run)
│
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── participant.html
│   ├── checkin.html
│   ├── result.html
│   ├── trace.html
│   └── error.html
│
├── static/
│   ├── css/main.css
│   └── js/main.js
│
├── tests/              # Pytest test suite (144 tests)
│
├── help/               # This folder — documentation
│
└── docs/
    └── hindsight_api_notes.md
```

---

## Running the Tests

```powershell
python -m pytest tests/ -v
```

All 144 tests should pass. Tests do not require a live Hindsight server or Groq key (all external calls are mocked).

---

## Environment Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `HINDSIGHT_BASE_URL` | Yes | Hindsight Cloud endpoint |
| `HINDSIGHT_API_KEY` | Yes | Hindsight authentication key |
| `HINDSIGHT_BANK_ID` | Yes | Memory bank name/ID |
| `GROQ_API_KEY` | Yes | Groq LLM API key |
| `DB_PATH` | No | Override SQLite path (default: `data/trialguard.db`) |

---

## Port Configuration

The app runs on port 5000 by default. To change it, edit the last line of `app.py`:

```python
app.run(debug=True, port=5000)  # change 5000 to any free port
```

---

## Resetting Everything

To start completely fresh:

```powershell
# 1. Delete the database
Remove-Item data\trialguard.db -ErrorAction SilentlyContinue

# 2. Re-initialise
python seed_db.py
python seed_demo.py

# 3. Start the app
python app.py
```

Note: Hindsight memories from the previous session will still exist in the cloud bank. Re-running `seed_demo.py` will update them (idempotent — same document_ids).
