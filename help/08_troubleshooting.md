# TrialGuard — Troubleshooting Guide

---

## Quick Diagnostic Checklist

Run through this before investigating further:

- [ ] Is `python app.py` running?
- [ ] Is `.env` present with all 4 variables set?
- [ ] Has `python seed_db.py` been run?
- [ ] Has `python seed_demo.py --participant P402` been run?
- [ ] Does the dashboard show "Hindsight memory connected"?
- [ ] Is there an internet connection? (Hindsight Cloud + Groq both need it)

---

## Issue: Dashboard Shows Only 1 Participant (or No Participants)

**Cause:** SQLite database doesn't have participants loaded.

**Fix:**
```powershell
python seed_db.py
```

Then refresh the dashboard. You should see 10 participants.

---

## Issue: Hindsight Shows as "Unavailable" on Dashboard

**Cause:** Can't reach Hindsight Cloud, or API key/URL is wrong.

**Fix — Step 1:** Check `.env`:
```
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=hsk_xxxx...
HINDSIGHT_BANK_ID=trialguard_id
```

**Fix — Step 2:** Test the connection manually:
```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); import memory; print(memory.get_version())"
```

Expected output: `0.10.1` (or similar version string)

If you see an error, check your Hindsight API key at https://hindsight.vectorize.io

---

## Issue: Analysis Shows "Agent Analysis Unavailable"

**Cause:** Groq API key is wrong, expired, or the model isn't available.

**Fix — Step 1:** Check `.env`:
```
GROQ_API_KEY=gsk_xxxx...
```

**Fix — Step 2:** Test Groq:
```powershell
python -c "
from dotenv import load_dotenv; load_dotenv()
from groq import Groq
import os
r = Groq().chat.completions.create(
    model='openai/gpt-oss-120b',
    messages=[{'role':'user','content':'Say hello'}]
)
print(r.choices[0].message.content)
"
```

If you see a 401 error: the key is invalid. Get a new key at https://console.groq.com  
If you see a 404 error: the model name is wrong. Check available models:
```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); from groq import Groq; [print(m.id) for m in Groq().models.list().data]"
```

---

## Issue: Analysis Runs But No Memories Returned

**Cause:** P402 history not seeded into Hindsight.

**Fix:**
```powershell
python seed_demo.py --participant P402
```

Wait for all 8 check-ins to be confirmed (`✓ checkin:P402:001` through `008`), then retry.

**Verify seeding worked:**
```powershell
python -c "
from dotenv import load_dotenv; load_dotenv()
import memory
resp = memory.recall('nausea dosage', 'P402')
print(f'{len(resp.results)} memories found for P402')
"
```

Should print something like `32 memories found for P402`.

---

## Issue: "Historical Pattern" Field Shows [Redacted]

**Cause:** The safety validator blocked content it detected as a prohibited pattern (diagnosis, dosage change, causal claim).

**This is expected behaviour** — the system is working correctly. The agent's raw output contained a pattern that crossed the defined role boundary.

The redaction message tells you which pattern was blocked. The rest of the brief is unaffected.

If this is happening unexpectedly for benign content, the safety regex may be too broad for your specific wording. Rephrase the check-in to be more neutral.

---

## Issue: App Won't Start — "Address Already in Use"

**Cause:** Port 5000 is already occupied.

**Fix — Option 1:** Kill the existing process:
```powershell
Get-Process -Name python | Stop-Process -Force
```

**Fix — Option 2:** Use a different port — edit the last line of `app.py`:
```python
app.run(debug=True, port=5001)
```

---

## Issue: Database Error on Startup

**Cause:** The `data/` directory doesn't exist, or the DB file is corrupted.

**Fix:**
```powershell
New-Item -ItemType Directory -Force -Path data
python seed_db.py
```

---

## Issue: Unicode / Encoding Error in Terminal

**Cause:** Windows console (cmd.exe / PowerShell) defaults to cp1252 which can't display certain characters.

**Fix:** Run with UTF-8 encoding:
```powershell
$env:PYTHONUTF8=1
python app.py
```

Or set it permanently in your PowerShell profile.

---

## Issue: "Unclosed client session" Warnings in Logs

**Cause:** The Hindsight Python client uses aiohttp internally and doesn't always close the session cleanly on process exit.

**This is not an error** — it's a warning from the aiohttp library. All data was stored/retrieved correctly. It appears in the terminal logs but does not affect functionality.

---

## Issue: The Demo Script Shows All "Not Available" Fields

**Cause:** Usually means the Groq API failed silently. Check `demo_err.txt` (created alongside `demo_out.txt` when running `demo_p402.py`).

Common causes:
- Invalid Groq API key → 401 error
- Wrong model name → 404 error  
- JSON schema error → 400 error

All three have been fixed in the current codebase. If you see them again, check that your `.env` has the latest Groq key.

---

## Issue: Tests Failing

Run the test suite:
```powershell
python -m pytest tests/ -v --tb=short
```

All 144 tests should pass. If any fail:

- Tests do NOT require live Hindsight or Groq — all external calls are mocked
- Check that all source files (`db.py`, `agent.py`, `memory.py`, `models.py`, `safety.py`, `app.py`) haven't been accidentally modified
- If you see import errors, check that all packages are installed: `pip install -r requirements.txt`

---

## Issue: Seeding Takes Very Long

**Cause:** Hindsight Cloud API calls have a network round-trip each. With 45 check-ins, this takes about 2–3 minutes.

**Speed up:** Seed only P402 (8 check-ins, ~40 seconds):
```powershell
python seed_demo.py --participant P402
```

---

## Issue: New Check-ins Don't Show in Hindsight Recall

**Cause:** There is sometimes a short propagation delay in Hindsight Cloud (typically a few seconds).

**Fix:** Wait 5–10 seconds after submission, then run a new check-in. The previously submitted check-in should now be retrievable.

---

## Useful Debug Commands

```powershell
# Check Hindsight version
python -c "from dotenv import load_dotenv; load_dotenv(); import memory; print(memory.get_version())"

# List all memories for P402
python -c "from dotenv import load_dotenv; load_dotenv(); import memory; mems=memory.list_participant_memories('P402'); print(f'{len(mems)} memories'); [print(' -', m['document_id']) for m in mems[:10]]"

# Check SQLite stats
python -c "from dotenv import load_dotenv; load_dotenv(); import db; db.init_db(); print(db.get_stats())"

# Check available Groq models
python -c "from dotenv import load_dotenv; load_dotenv(); from groq import Groq; [print(m.id) for m in Groq().models.list().data]"

# Run a quick agent test (no real data needed)
python -c "
from dotenv import load_dotenv; load_dotenv()
import agent
result = agent.run_agent('Participant reports feeling well.', 'P117', mode='baseline')
print('Mode:', result['mode'])
print('Issue:', result['brief']['current_issue'][:80])
"
```

---

## Log Levels

The app logs to the console. To see more detail:

```python
# In app.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

To reduce noise:
```python
logging.basicConfig(level=logging.WARNING)
```
