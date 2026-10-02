---
name: hospitable
description: >
  Full Hospitable Public API v2 index for CleaningButton / R2: properties,
  reservations (incl. financials), calendar, messages, reviews, user, webhooks,
  scopes, rate limits, and Pine unit UUID map. Use when the user asks about
  Hospitable API, occupancy, revenue financials, guest messaging, calendar
  pricing, reviews, PAT auth, or runs /hospitable. Official docs:
  https://developer.hospitable.com/docs/public-api-docs/
---

# Hospitable Public API v2 (R2 skill)

Indexed from the official Public API docs
([Introduction](https://developer.hospitable.com/docs/public-api-docs/d862b3ee512e6-introduction))
and the published **OpenAPI 3.1** surface (`references/openapi-v2.yaml`).

**Base URL:** `https://public.api.hospitable.com/v2`  
**Auth:** `Authorization: Bearer <PAT>`  
**Contact:** team-platform@hospitable.com  
**V1 EOL:** 2025-02-03 (use v2 only)

## When to use this skill

- Implement or debug **R2Lambda** `lib/hospitable.js` (occupancy / revenue)
- **Occupancy goal definitions** (SEASON_BANDS) are **not** in Hospitable — see skill **`pricing`** / repo `jeromevidaao/pricing-tool`
- **Performance vs goals** (trailing/forward fill already scored) lives in the weekly S3 report first — see skill **`pricing`**. Use Hospitable only when the host wants live/fresher than that snapshot
- Answer questions about **what Hospitable can return** (fields, includes, scopes)
- Rework analysis when revenue/occupancy fails because of API misuse
- Wire new features: messages, calendar, reviews, webhooks
- PAT setup / scope requirements

**Prefer live answers via R2** (`/r2` skill) for “who is in unit 2?” / “July revenue?” — this skill is the **API map**, not a live client.

## Authentication (PAT)

1. Log in → [my.hospitable.com](https://my.hospitable.com)
2. **Apps** → **API access** → **Access tokens** → **+ Add new**
3. Scopes: **Read** (properties/reservations/calendar view) and/or **Write** (calendar updates)
4. Header on every request:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Accept: application/json
```

**CleaningButton production token:** AWS SSM `/hospitable/bearer-token`  
(Injected into R2Lambda / cleaningbutton-api — **never** put the raw token in chat, R2Memory notes, or skill files.)

**2026-10-01 8:31pm PT:** that parameter returned **401** on `GET /v2/user` and on `GET /v2/reservations`. Lambda `code_not_there_text_alert` retried 5 times, errored, and CloudWatch alarm `code_not_there_text_alert-errors` emailed Jerome. The expiry alarms `hospitable-token-expiry-auto-reply-sqs` and `hospitable-token-expiry-pricing-tool` have been in ALARM since 2026-09-02 (about 29.5 days of life left). A new PAT has to be written to `/hospitable/bearer-token`. Do not paste it into chat.

**Hardened (`eb98aea`):** that 401/403 is no longer retried or titled as a missing door code. One plain-text alerts page per 12 hours, subject `Hospitable token rejected — door codes not checked`, stamp `/code-not-there/hospitable-auth-alert-at`. The run still errors so `code_not_there_text_alert-errors` stays ALARM.

### Required scopes (by feature)

| Scope | Use |
|-------|-----|
| `property:read` | List/get properties; reservation `include=properties` |
| `listing:read` | `include=listings` (platform listing ids) |
| `calendar:read` | GET property calendar |
| `calendar:write` | PUT property calendar |
| `reservation:read` | List/get reservations |
| `financials:read` | `include=financials` / `financialsV2` |
| `message:read` | GET reservation messages |
| `message:write` | POST messages (**must request** from team-platform@hospitable.com) |
| `reviews:read` | Property reviews + reservation `include=review` |
| `reviews:write` | Respond to a review |
| `pat:read` | Listing platform_name / platform_email on PAT tokens |

## Endpoint catalog (complete v2 surface)

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/properties` | List properties |
| `GET` | `/properties/search` | Search availability + pricing (Direct self-hosted site required) |
| `GET` | `/properties/{uuid}` | Get one property |
| `GET` | `/properties/{uuid}/calendar` | Availability + nightly price |
| `PUT` | `/properties/{uuid}/calendar` | Update price/availability |
| `GET` | `/reservations` | List reservations (**`properties[]` required**) |
| `GET` | `/reservations/{uuid}` | Get one reservation |
| `GET` | `/reservations/{uuid}/messages` | Message thread |
| `POST` | `/reservations/{uuid}/messages` | Send guest message |
| `GET` | `/properties/{uuid}/reviews` | Guest reviews |
| `POST` | `/reviews/{uuid}/respond` | Public review response |
| `GET` | `/user` | Authenticated user + billing address |

Full parameter tables, request bodies, and schemas:  
→ **`references/endpoints.md`**  
→ **`references/openapi-v2.yaml`** (machine-readable source of truth)

### Amenities (Airbnb listing content)

Public API **cannot write** amenities (`GET /properties/{uuid}` is read-only; PATCH/PUT 405). Hospitable web listing editor uses the **internal** API:

`PUT https://api.hospitable.com/v1/properties/{uuid}` `{ "name": "<current name>", "amenities": ["…","dishwasher","freezer"] }`

Requires a **web session** (magic-link / password login), not the PAT. `name` is required on PUT or 422. Airbnb listings that are `fully_managed` get the amenity push. PAT still used to **read** `amenities[]` after the write.

Pine (2026-08-15): Apt **#2** added `dishwasher` + `freezer`; Apt **#1B** added `freezer`. Apt **#3** already had both.

### Not in Public API OpenAPI (do not invent)

These appear in community/Make.com integrations but are **not** in the official OpenAPI v2 used here:

- Payouts / bank transactions / owner statements
- Generic “transactions” or accounting ledger endpoints
- Arbitrary status filters not listed below

If R2 needs something outside this catalog, say so explicitly — do not fabricate paths.

## Pagination

- `page` (default 1), `per_page` (default 10, **max 100**; reviews max **50**)
- List responses: `{ "data": [...], "meta": { current_page, last_page, per_page, total, ... } }`

## Errors

```json
{
  "status_code": 400,
  "reason_phrase": "…",
  "message": "The given data was invalid."
}
```

| Code | Meaning |
|------|---------|
| 400 | Bad request / validation |
| 401 | Unauthorized (bad/missing PAT) |
| 403 | Forbidden (scope or review response window) |
| 404 | Not found |
| 429 | Rate limited |
| 500 | Server error |

## Rate limits

| Surface | Limit |
|---------|--------|
| Calendar **PUT** | **1000 req/min** |
| Messages **POST** | **2/min per reservation**; **50 / 5 min** global |
| General | Contact support for higher limits |

## Webhooks (outbound events)

Configure in Hospitable; payload shape:

```json
{
  "id": "unique-ordered-payload-id",
  "action": "reservation.created",
  "data": { /* resource */ },
  "created": "2024-01-01T12:00:00Z",
  "version": "1.0"
}
```

| `action` | Resource |
|----------|----------|
| `reservation.created` | Reservation |
| `reservation.updated` | Reservation |
| `property.updated` / `property.merged` | Property |
| `message.created` | Message |
| `review.created` | Review |

## CleaningButton / R2 mapping

### Pine property UUIDs (Hospitable)

| Unit | Airbnb listingId | Hospitable property UUID |
|------|------------------|--------------------------|
| Pine Apt **#1B** | `20904545` | `c899481f-2e5b-402d-80c4-3167fd824d96` |
| Pine Apt **#2** | `20150380` | `114663c5-0709-4eff-a868-fa9ebd6ed42d` |
| Pine Apt **#3** | `24259977` | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` |

Source of truth in code: `~/R2Lambda/lib/hospitable.js` (`LISTING_TO_PROPERTY` / `UNIT_META`).

### What R2 already calls

| Intent | How |
|--------|-----|
| **Performance vs goals (default)** | **Not Hospitable** — public S3 `https://www.cleaningbutton.com/data/occupancy/latest.json` (Lambda pricing-tool-report). R2 flag `needOccupancyReport`. Skill **`pricing`**. |
| Occupancy (live guests) | `GET /reservations?properties[]=…&include=properties,guest,financials` over a date window; skip cancelled/inquiry |
| Fill refresh (when host wants live beyond weekly report) | Same reservations window with explicit `start_date`/`end_date` covering trailing-30 + forward-30; optional **`GET /properties/{uuid}/calendar?start_date=&end_date=`** per Pine unit for night-level status |
| **Block / unblock a night** | R2 chat **executes** `PUT /properties/{uuid}/calendar` `{ date, available: false, closed_for_checkin: true, closed_for_checkout: true }`. Night is not fully blocked if check-in is still open. Token has **`calendar:write`**. Skips RESERVED nights. |
| **Send guest message** | R2 chat **executes** `POST /reservations/{uuid}/messages` `{ body }` (`message:write`). |
| **Public review reply** | R2 chat **executes** `POST /reviews/{uuid}/respond` `{ response }` (`reviews:write`). |
| Revenue | Same reservations call; **net** = `financials.host.accommodation.amount` + sum `financials.host.host_fees[].amount` (cents); **excludes** cleaning / guest fees |
| Airbnb cleaning fee line | `financials.host.guest_fees` (or guest fees) labels matching `/clean/i` |
| Month bucketing | By **check-in** month in `America/New_York` |

### Hospitable calls for goal-tracking refresh (when S3 is not enough)

Use only after the weekly S3 report, or when the host asks for live/fresher data.

```bash
# 1) Reservations for trailing + forward window (R2 lib/hospitable.js pattern)
# Auth: Bearer from SSM /hospitable/bearer-token
curl -sS -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" \
  "https://public.api.hospitable.com/v2/reservations?\
properties[]=c899481f-2e5b-402d-80c4-3167fd824d96&\
properties[]=114663c5-0709-4eff-a868-fa9ebd6ed42d&\
properties[]=60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd&\
start_date=2026-07-01&end_date=2026-09-30&\
include=properties,guest,financials&per_page=100&page=1"

# 2) Night-level calendar for one unit (repeat for each UUID)
curl -sS -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" \
  "https://public.api.hospitable.com/v2/properties/114663c5-0709-4eff-a868-fa9ebd6ed42d/calendar?\
start_date=2026-08-01&end_date=2026-08-31"
```

R2 chat escalation phrase:

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "How are we doing with goals — refresh live from Hospitable"
```

### Critical reservation rules (from OpenAPI)

1. **`properties[]` is required** on `GET /reservations` — always pass the three Pine UUIDs (or a subset).
2. Default window if you omit dates: **check-ins in the next ~2 weeks** — always pass explicit `start_date` / `end_date` for historical revenue.
3. `date_query`: `checkin` (default) or `checkout` — how start/end apply.
4. Revenue **must** use `include=financials` and token scope **`financials:read`**.
5. Single reservation also supports `include=financialsV2` (same scope).
6. Status: prefer `reservation_status.current.category`  
   (`request` | `accepted` | `cancelled` | `not accepted` | `checkpoint` | `unknown`).  
   Legacy `status` string is **deprecated**.
7. Money fields are **integer minor units** (cents for USD), plus `formatted` strings when present.

### Agent rules for R2 work

- **Do** use this skill before inventing Hospitable endpoints or payload shapes.
- **Do** keep net-revenue definition aligned with `netRevenueCentsFromFinancials` (accommodation + host_fees only).
- **Do not** claim payouts/owner statements exist on Public API unless OpenAPI is updated.
- **Do not** send guest messages without `message:write` approval.
- **Do** execute host “block/unblock night” requests in R2Lambda (`parseCalendarCommand` / `applyCalendarCommand`). The production PAT has `calendar:write` (PUT returns 202, not 403). Never tell the host R2 lacks calendar permission.
- **Do not** update calendars when `calendar_restricted: true` on the property. Pine units are `calendar_restricted: false`.
- Messages: plain text only (no HTML); `\n` for line breaks; max 3 images @ 5MB.
- Calendar PUT: up to **3 years** ahead; OpenAPI marks max **60** date objects per body; rate 1000/min.
- Property search requires a **self-hosted Direct** site; max **90-day** stay window, up to 3 years out.

## Quick curl patterns

```bash
# Who is staying (next 2 weeks default — pass dates for history)
curl -sS -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" \
  "https://public.api.hospitable.com/v2/reservations?\
properties[]=c899481f-2e5b-402d-80c4-3167fd824d96&\
properties[]=114663c5-0709-4eff-a868-fa9ebd6ed42d&\
properties[]=60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd&\
start_date=2026-07-01&end_date=2026-07-31&\
include=properties,guest,financials&per_page=100&page=1"

# One property
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://public.api.hospitable.com/v2/properties/114663c5-0709-4eff-a868-fa9ebd6ed42d?include=listings"

# Calendar
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://public.api.hospitable.com/v2/properties/114663c5-0709-4eff-a868-fa9ebd6ed42d/calendar?\
start_date=2026-08-01&end_date=2026-08-31"

# Auth check
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://public.api.hospitable.com/v2/user"
```

Live ops via Lambda (preferred for end-user Q&A):

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py "What was last month net revenue by unit?"
python3 ~/.grok/skills/r2/scripts/r2_chat.py "Is unit 2 occupied right now?"
```

## Implementation map

| Layer | Location |
|-------|----------|
| R2Lambda client | `~/R2Lambda/lib/hospitable.js` |
| Mirror (if present) | `~/cleaningbutton-ai-code-push/lib/hospitable.js` |
| SSM token | `/hospitable/bearer-token` |
| Android skill cards | Occupancy + Revenue in `R2SkillCatalog` (source: Hospitable) |
| This skill | `~/.grok/skills/hospitable/` |
| OpenAPI dump | `references/openapi-v2.yaml` |
| Endpoint deep-dive | `references/endpoints.md` |

## Official links

- Docs hub: https://developer.hospitable.com/docs/public-api-docs/
- Introduction: https://developer.hospitable.com/docs/public-api-docs/d862b3ee512e6-introduction
- App / PAT: https://my.hospitable.com (Apps → API access)

## Slash

`/hospitable` → load this skill; summarize endpoint needed for the user’s task; for live data call `/r2`.
