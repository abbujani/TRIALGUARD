# TrialGuard — Vercel Deployment Guide

> How to deploy TrialGuard live on Vercel.

---

## Important Note About Vercel and Flask

Vercel is primarily designed for Node.js/Next.js apps. It does support Python via **serverless functions**, but Flask apps require a specific configuration. The approach below uses Vercel's Python runtime with a `vercel.json` configuration file.

**Key limitation:** Vercel's serverless environment does not support a persistent SQLite file on disk (the filesystem is read-only/ephemeral). For a live deployment, you have two options:

| Option | Complexity | Best for |
|--------|-----------|----------|
| **A. Vercel + in-memory SQLite** (demo only) | Low | Hackathon demo — data resets on each cold start |
| **B. Vercel + external DB (PlanetScale/Supabase)** | Medium | Production-quality persistence |
| **C. Railway/Render (recommended alternative)** | Low | Full Flask app with persistent SQLite |

For a hackathon demo, **Option A** (or Option C) is the fastest path.

---

## Option A — Vercel with In-Memory / Temp SQLite

This works for demos where you don't need persistent check-in history across sessions. The app runs fully — Hindsight memories persist (cloud), but SQLite resets on cold start.

### Step 1 — Create `vercel.json`

Create this file in the project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### Step 2 — Create `api/index.py` (Vercel entry point)

Vercel needs the Flask app exported from `api/index.py`:

```powershell
New-Item -ItemType Directory -Force -Path api
```

Create `api/index.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

# Vercel expects 'app' as the WSGI callable
```

### Step 3 — Update `vercel.json` to point at api/index.py

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### Step 4 — Set environment variables on Vercel

1. Go to https://vercel.com/dashboard
2. Open your project → **Settings** → **Environment Variables**
3. Add each of the four variables:

| Name | Value |
|------|-------|
| `HINDSIGHT_BASE_URL` | `https://api.hindsight.vectorize.io` |
| `HINDSIGHT_API_KEY` | your key |
| `HINDSIGHT_BANK_ID` | `trialguard_id` |
| `GROQ_API_KEY` | your key |

### Step 5 — Deploy

```powershell
# Install Vercel CLI if not already installed
npm install -g vercel

# Deploy from project root
vercel

# Follow the prompts:
# - Link to existing project or create new
# - Set up and deploy
```

Or connect your GitHub repository to Vercel for automatic deployments on push.

---

## Option C — Railway (Recommended for Flask + SQLite)

Railway is much simpler for Flask applications with SQLite. It gives you a persistent filesystem.

### Step 1 — Create a Railway account

Go to https://railway.app and sign in with GitHub.

### Step 2 — Create a new project

1. Click **New Project** → **Deploy from GitHub repo**
2. Select your `TrialGuard` repository
3. Railway auto-detects Python

### Step 3 — Add a `Procfile`

Create `Procfile` in the project root:

```
web: python app.py
```

Or for production with gunicorn:

```
web: gunicorn app:app
```

If using gunicorn, add it to `requirements.txt`:
```
gunicorn==21.2.0
```

### Step 4 — Set environment variables on Railway

1. Open your Railway project → **Variables**
2. Add all four environment variables (same as above)
3. Add: `PORT=5000` (Railway uses this)

### Step 5 — Update `app.py` to use `PORT` env var

Change the last line of `app.py`:

```python
if __name__ == "__main__":
    db.init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

Also add `import os` at the top if not already there.

### Step 6 — Seed on first deploy

After deployment, open a Railway shell or run the seed command:

```bash
python seed_db.py
python seed_demo.py --participant P402
```

Railway will give you a public URL like `https://trialguard-production.up.railway.app`.

---

## Option D — Render (Also Recommended)

Similar to Railway. Free tier available.

1. Go to https://render.com → **New** → **Web Service**
2. Connect your GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add environment variables in the Render dashboard
6. Click **Deploy**

---

## Fastest Path for the Hackathon

For maximum speed and reliability:

1. Push code to GitHub (see `09_github_guide.md`)
2. Sign up at https://railway.app
3. Deploy from GitHub in 3 clicks
4. Set 4 environment variables
5. Run `python seed_db.py` and `python seed_demo.py --participant P402` once
6. Share the Railway URL as your live demo link

**Estimated time: 15–20 minutes.**

---

## After Deployment — Verify

Visit your live URL and check:

- [ ] Dashboard loads with 10 participants
- [ ] Hindsight status shows "connected"
- [ ] P402 → New Check-in → submit → result page works
- [ ] Memory trace page loads
- [ ] Safety note is visible on result page

---

## Custom Domain (optional)

Both Railway and Render allow you to attach a custom domain:

1. Buy a domain (e.g. `trialguard.app` on Namecheap/GoDaddy)
2. In Railway/Render: **Settings** → **Domains** → **Add Custom Domain**
3. Point your domain's DNS to the provided CNAME
