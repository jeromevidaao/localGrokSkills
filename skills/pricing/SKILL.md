---
name: pricing
description: >
  CleaningButton dynamic pricing and occupancy goals. Source of truth is
  jeromevidaao/pricing-tool (AWS Lambdas pricing-tool + pricing-tool-report).
  Use when user asks occupancy goals/targets, SEASON_BANDS, BASE_PRICES,
  Pricing Lambda, weekly occupancy report, how we are doing vs goals, Sep/Oct
  fill targets, or pricing-tool.
---

# Pricing tool & occupancy goals

## Source of truth (never invent)

| What | Where |
|------|--------|
| **GitHub repo** | https://github.com/jeromevidaao/pricing-tool |
| **Local clone** | `~/pricing-tool` |
| **Occupancy goal definition** | `report.js` → **hardcoded** `const SEASON_BANDS` (`targetLow` / `targetHigh`) — **not DDB** |
| **Performance vs goals (actuals)** | Weekly JSON from Lambda **pricing-tool-report** → S3 / CDN |
| **S3 path** | `s3://cleansite/data/occupancy/latest.json` (+ dated archive under `data/occupancy/`) |
| **Public URL** | https://www.cleaningbutton.com/data/occupancy/latest.json |
| **Dynamic rates** | `index.js` → Lambda `pricing-tool` |
| **Weekly email + goals scoring** | `report.js` → Lambda `pricing-tool-report` |
| **DynamoDB** | **None** in pricing-tool for goals or weekly actuals |

**Do not** say pricing-tool / SEASON_BANDS / the weekly report is unavailable.

## Question types (do not collapse)

| Host asks | Answer with | Not this |
|-----------|-------------|----------|
| **What are occupancy goals / SEASON_BANDS?** | `report.js` bands (R2 GitHub pull) | Live guests only |
| **How are we doing with the goals?** | S3 weekly `latest.json` first | SEASON_BANDS dump alone; “no data” without S3 |
| **Pricing strategy / reach 85% without leaving money on the table?** | `index.js` levers (R2 strategy direct answer) | SEASON_BANDS table alone |
| Live guests / fresher fill | Hospitable | Goals definition |

### Pricing strategy (HARD)

When the host asks **how we price** to hit fill **without leaving money on the table** (e.g. “pricing strategy to reach 85% occupancy”, “fill vs ADR”, “how does pricing-tool work?”):

1. **Prefer** `jeromevidaao/pricing-tool` → **`index.js`** (Lambda `pricing-tool`).
2. Explain the **levers**, not just the targets:
   - Season-aware **occupancy multipliers** (peak cuts hard; winter protects ADR)
   - Per-month forward occ + mild global nudge
   - **Comp-aware YoY ADR cap** on soft open nights
   - Last-minute / gap-orphan (stronger peak, softer winter)
   - DOW curve, holidays/events, `BASE_PRICES` + `MIN_MAX_PRICES`
   - Push rules: open nights only; **no raise within 21 days**
3. **85% is not year-round** — shoulder high / inside peak; winter target is 35–60%.
4. SEASON_BANDS are the **fill targets** the strategy aims at — include them briefly, never as the whole answer.
5. R2 after deploy: deterministic direct answer (`formatPricingStrategyAnswer`); local:

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "what is your pricing strategy to reach 85% occupancy rate without leaving too much money on the table?"
```

**Banned:** answering a strategy question with only the SEASON_BANDS month table.

## Agent cascade (HARD) — how are we doing with goals?

When the host asks **performance vs goals** (e.g. “how are we doing with the goals?”, “tracking vs Sep target?”, “fill vs goal?”):

### 1. Start with the weekly S3 occupancy report (preferred)

The report already includes **trailing + forward occupancy**, **season targets**, **level** (ok/low/…), **headlines**, and **top actions** — no Hospitable call required for a normal status check.

```bash
# Fast path (this skill)
python3 ~/.grok/skills/pricing/scripts/occupancy_vs_goals.py

# Or curl
curl -sS "https://www.cleaningbutton.com/data/occupancy/latest.json" | python3 -m json.tool | head -80

# Or ask R2 (loads same S3 pack after deploy)
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "How are we doing with the occupancy goals?"
```

**Banned:** claiming “no live occupancy data in this session” or “cannot assess vs goals” **without first fetching** `latest.json`. That file is public and is the weekly source of truth for actuals-vs-targets.

### 2. Pure goal *definition* (bands only) → code

When the host asks **what the targets are** (not how we are tracking):

```bash
python3 ~/.grok/skills/pricing/scripts/season_bands.py
# or
rg -n "SEASON_BANDS|targetLow|targetHigh" ~/pricing-tool/report.js | head -40
# or R2
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "What are occupancy goals for September and October? Quote SEASON_BANDS."
```

### 3. Escalate to Hospitable only if the host wants more / fresher data

Use live Hospitable when the host explicitly asks for:

- live / real-time / refresh / right now
- more granular calendar / night-by-night
- data newer than the weekly S3 snapshot
- revenue + occupancy mixed in one pull

**Do not** open Hospitable for a plain “how are we doing with goals?” — answer from the S3 report first.

#### Hospitable API R2 must use (fill / calendar actuals)

Auth: SSM `/hospitable/bearer-token` (never put the raw token in chat).  
Base: `https://public.api.hospitable.com/v2`  
Scopes: `property:read`, `reservation:read`, `calendar:read` (and `financials:read` if revenue).

**Pine property UUIDs** (required on reservations):

| Unit | UUID |
|------|------|
| #1B Studio | `c899481f-2e5b-402d-80c4-3167fd824d96` |
| #2 | `114663c5-0709-4eff-a868-fa9ebd6ed42d` |
| #3 | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` |

**A. Reservations window (what R2 live occupancy uses today)**

```http
GET /v2/reservations?
  properties[]=<uuid1>&properties[]=<uuid2>&properties[]=<uuid3>
  &start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  &include=properties,guest,financials
  &per_page=100&page=1
```

- Always pass **explicit** `start_date` / `end_date` (default API window is only ~next 2 weeks).
- Skip cancelled / inquiry; prefer `reservation_status.current.category`.
- R2 client: `~/R2Lambda/lib/hospitable.js` → `fetchReservations` + `buildOccupancy`.

**B. Per-property calendar (night-level availability + price)** — best for mid-month fill detail beyond the weekly snapshot:

```http
GET /v2/properties/{uuid}/calendar?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

Call once per Pine UUID for the month or forward-30 window. Occupancy fill ≈ booked / sellable nights from calendar status (align with `pricing-tool` `occupancyFromDays` logic when comparing).

**C. Via R2 chat (preferred for end-user Q&A after S3)**

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "How are we doing with goals — refresh live from Hospitable"
```

R2 routes that phrase to S3 report **plus** `needHospitable` when the message includes live/refresh/Hospitable/more detail.

Full API map: skill **`hospitable`**.

## SEASON_BANDS (authoritative occupancy targets)

Months are **1–12**. Goals are trailing occupancy fill rates.

| Band | Months | targetLow | targetHigh | Notes |
|------|--------|-----------|------------|--------|
| **peak** | 6, 7, 8 (Jun–Aug) | **0.80** | **0.95** | Peak summer |
| **shoulder** | 5, 9, 10 (May, **Sep**, **Oct**) | **0.60** | **0.85** | Late spring / early fall |
| **soft** | 4 (Apr) | **0.45** | **0.70** | Soft shoulder |
| **winter** | 1, 2, 3, 11, 12 | **0.35** | **0.60** | Off-season; do not panic mid-40s |

### Quick answers

- **September / October** → **shoulder**: **60–85%** target (`targetLow: 0.6`, `targetHigh: 0.85`)
- **June–August** → **peak**: **80–95%**
- **Nov–Mar** → **winter**: **35–60%**

If code may have changed, re-read `SEASON_BANDS` from disk or R2 — do not rely on memory alone for shipping decisions.

## What is in `latest.json` (weekly report)

Published by **pricing-tool-report** (same Lambda as the email):

- `meta.season` — current trailing-window band + `targetLow` / `targetHigh`
- `meta.monthlyTargets` — next months’ goal bands
- `summary[]` per unit: `trailing30`, `forward30`, `target`, `level`, `headline`, `topAction`, booked/sellable/open, ADRs
- Optional chart series, Grok analysis, proposed BASE_PRICES PR metadata

**Generated path in code:** `report.js` → `buildOccupancyReportJson` → S3 put to `OCCUPANCY_S3_BUCKET` / `data/occupancy/latest.json`.

## Banned claims

- "No pricing-tool / Pricing Lambda code is available"
- "I cannot pull GitHub" / "only R2Lambda is in this session"
- "Cannot assess performance vs goals" **without** fetching S3 `latest.json` first
- Treating live Hospitable guest names as the **goal** (live status ≠ target)
- Looking in DynamoDB for SEASON_BANDS or weekly fill goals

| Question type | Source |
|---------------|--------|
| What are the goals / SEASON_BANDS? | Code / GitHub (`report.js`) |
| Pricing strategy / fill vs ADR / reach 85% without leaving money? | Code / GitHub (`index.js` levers) |
| How are we doing vs goals? | **S3 weekly report first** |
| Who is in unit 2 right now? | Hospitable (skill **r2**) |
| Fresher fill than weekly report | Hospitable reservations + optional calendar (above) |

## Related

- Skill **r2** — invoke R2Lambda (S3 report + optional Hospitable + GitHub)
- Skill **hospitable** — full API map (not goals definition)
- R2Memory `decisions.md` — standing note: goals live in pricing-tool; performance in S3 report
