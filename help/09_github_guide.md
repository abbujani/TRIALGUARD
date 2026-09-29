# TrialGuard — GitHub Guide

> What files to include, what to exclude, and the complete workflow for publishing the repository.

---

## Files to INCLUDE in GitHub

```
TrialGuard/
├── app.py                    ✅ include
├── agent.py                  ✅ include
├── memory.py                 ✅ include
├── db.py                     ✅ include
├── models.py                 ✅ include
├── safety.py                 ✅ include
├── seed_demo.py              ✅ include
├── seed_db.py                ✅ include
├── demo_p402.py              ✅ include
├── requirements.txt          ✅ include
├── .env.example              ✅ include  ← template only, no real keys
├── .gitignore                ✅ include
├── README.md                 ✅ include
│
├── data/
│   └── demo_data.json        ✅ include  ← synthetic data, safe to publish
│
├── templates/                ✅ include all HTML files
├── static/                   ✅ include all CSS and JS files
├── tests/                    ✅ include all test files
│
├── help/                     ✅ include all documentation
└── docs/                     ✅ include API notes
```

---

## Files to EXCLUDE from GitHub

```
.env                          ❌ NEVER commit — contains real API keys
data/trialguard.db            ❌ exclude — local SQLite database
__pycache__/                  ❌ exclude — Python bytecode
*.pyc                         ❌ exclude — compiled Python
.pytest_cache/                ❌ exclude — test artefacts
.venv/ or venv/               ❌ exclude — virtual environment
stderr.txt / stdout.txt       ❌ exclude — any temp output files
bp_raw.txt                    ❌ exclude — temp file
```

Your `.gitignore` already handles all of these. Verify it contains:

```gitignore
.env
data/*.db
data/*.sqlite3
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.venv/
venv/
*.egg-info/
stderr.txt
stdout.txt
bp_raw.txt
```

---

## Step-by-Step: First Push to GitHub

### Step 1 — Create the repository on GitHub

1. Go to https://github.com/new
2. Repository name: `TrialGuard`
3. Description: `AI-powered clinical trial coordinator support, grounded in Hindsight long-term memory`
4. Set to **Public** (required for hackathon submission)
5. Do NOT initialise with README (you already have one)
6. Click **Create repository**

---

### Step 2 — Initialise Git locally

Open PowerShell in the project folder:

```powershell
cd "c:\Users\Abdullah Hamdan\Desktop\hackathons\TrialGuard"

git init
git add .
git status   # verify .env is NOT listed
```

If `.env` appears in `git status`, stop and check your `.gitignore`.

---

### Step 3 — Make the first commit

```powershell
git commit -m "Initial commit — TrialGuard hackathon submission

- Flask + Hindsight + Groq stack
- Two-stage agent pipeline with tool calling
- 10 synthetic participants, P402 hero demo
- 144 passing tests
- Full help documentation"
```

---

### Step 4 — Connect to GitHub and push

```powershell
git remote add origin https://github.com/YOUR_USERNAME/TrialGuard.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

### Step 5 — Verify on GitHub

Open `https://github.com/YOUR_USERNAME/TrialGuard` and confirm:

- [ ] `README.md` renders correctly on the front page
- [ ] `.env` is NOT present (only `.env.example`)
- [ ] `data/trialguard.db` is NOT present
- [ ] `help/` folder with all documentation is present
- [ ] All source files are present

---

## Adding a Repository Description and Topics

On your GitHub repo page:
1. Click the gear icon next to "About"
2. Description: `AI-powered clinical trial coordinator support using Hindsight long-term memory`
3. Website: your live URL (if deployed on Vercel — see `10_vercel_guide.md`)
4. Topics: `python`, `flask`, `ai`, `hindsight`, `groq`, `llm`, `clinical-trials`, `memory`, `hackathon`

---

## Keeping the Repository Updated

After any code change:

```powershell
git add app.py agent.py        # add specific changed files
git commit -m "Fix: improve safety validator patterns"
git push
```

Never use `git add .` without first checking `git status` to confirm `.env` is not included.

---

## Branch Strategy (optional but recommended)

```powershell
# Create a development branch
git checkout -b dev

# Work on dev, then merge to main when ready
git checkout main
git merge dev
git push
```

For a hackathon, working directly on `main` is fine.

---

## Adding a License

The project includes MIT license (stated in README). To add the actual file:

```powershell
# Create LICENSE file
@"
MIT License

Copyright (c) 2026 Abdullah Hamdan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"@ | Out-File -FilePath "LICENSE" -Encoding utf8
```

---

## Hackathon Submission Checklist

Before submitting the GitHub link:

- [ ] Repository is Public
- [ ] README.md is complete and renders correctly
- [ ] `.env` is NOT committed (only `.env.example`)
- [ ] All source code files are present
- [ ] `help/` documentation folder is present
- [ ] `data/demo_data.json` is present (synthetic data)
- [ ] `tests/` folder with 144 tests is present
- [ ] Repository has a description and topics set
- [ ] At least one commit message clearly describes the project
