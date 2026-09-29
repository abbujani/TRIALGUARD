# Hindsight Client API — Phase 3 Verification Notes

**Package:** `hindsight-client==0.10.1`  
**Main class:** `hindsight_client.Hindsight`  
**Instantiation:** `Hindsight(base_url=..., api_key=...)`

---

## Key Methods Used by TrialGuard

### `retain(bank_id, content, *, tags, metadata, document_id, ...)`
Stores text (or a list of content blocks) into the memory bank.  
- `content` — `str` or `list[dict]`  
- `tags` — `list[str]` used for participant scoping (e.g. `["participant:P402"]`)  
- `metadata` — `dict[str, str]` for extra structured fields  
- `document_id` — deduplication key  
- Returns: `RetainResponse`

### `recall(bank_id, query, *, tags, tags_match, max_tokens, budget, ...)`
Semantic retrieval against the bank.  
- `query` — natural-language question  
- `tags` / `tags_match` — filter by participant tag; use `tags_match="all_strict"` for hard isolation  
- `budget` — `"low"` | `"mid"` | `"high"` controls token spend  
- Returns: `RecallResponse` (iterable of `RecallResult`)

### `aretain` / `arecall`
Async variants of the above (same signatures, prefixed with `a`).

### `create_bank(bank_id, name, mission, ...)`
One-time bank initialisation; idempotent via `bank_id`.

### `get_version()`
Health-check / version probe — returns `VersionResponse`.

---

## Participant Isolation Strategy

All memories are tagged `["participant:<ID>"]`.  
All recalls filter with `tags=["participant:<ID>"], tags_match="all_strict"`.  
This ensures one participant cannot read another's stored context.

---

## Response Objects of Interest

| Class | Key attributes |
|-------|---------------|
| `RetainResponse` | `.operation_id`, `.status` |
| `RecallResponse` | iterable of `RecallResult`; `.to_prompt_string()` |
| `RecallResult` | `.content`, `.score`, `.tags`, `.metadata` |
| `VersionResponse` | `.version` |

---

## Constructor Signature (inferred from inspection)

```python
from hindsight_client import Hindsight

hs = Hindsight(
    base_url="http://localhost:8888",  # HINDSIGHT_BASE_URL
    api_key="...",                     # HINDSIGHT_API_KEY
)
```

All bank-scoped calls pass `bank_id` (= `HINDSIGHT_BANK_ID`) as the first positional argument.
