---
name: r2
description: >
  RETIRED. The in-app R2 assistant, R2Lambda, self-heal, and AI code-push
  are gone (2026-09-07). Do not invoke R2Lambda or r2_chat.py. For live ops
  use hospitable, kumo, pricing, aws-account, and r2-memory instead.
---

# R2 assistant — retired

Jerome has Grok (laptop + phone). The Android/web R2 chat, `act=ai_code_*` jobs,
self-heal, and Lambda **`R2Lambda`** were removed.

**Do not** run `r2_chat.py`. **Do not** `aws lambda invoke` `R2Lambda`.

| Need | Use |
|------|-----|
| Occupancy / guests / block nights / guest messages | skill **`hospitable`** |
| Occupancy goals / weekly report | skill **`pricing`** + `https://www.cleaningbutton.com/data/occupancy/latest.json` |
| AC / heat pump | skill **`kumo`** (or dashboard `set_climate` via **`cleaningbutton-api`**) |
| AWS bill | skill **`aws-account`** |
| Standing prefs / past Q&A | skill **`r2-memory`** (Titan on S3 — **kept**) |
| Code changes | Grok CLI in the target repo — no in-app AI Tasks |

Electricity (CMP) and water (PWD) run **in-process** on Lambda `api`. Occupancy, Ring, cleaning, auto-reply are unchanged.
