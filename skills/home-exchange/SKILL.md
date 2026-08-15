---
name: home-exchange
description: >
  HomeExchange (HE) API for CleaningButton Pine Apt #3, Apt #2, and Apt #1B:
  inbox, listings, calendar, photos, exchanges, pre-approve. Always load the
  bearer from AWS SSM /homeexchange/bearer-token — never store tokens locally
  or in git. Use when the user asks about HomeExchange, HE guests, HE calendar,
  HE conversations, pre-approve, or runs /home-exchange.
---

# HomeExchange API

Undocumented web API used by homeexchange.com. Same client as `cleaningbutton-api` HE chat, `auto-reply-sqs-harness` `HomeExchangeClient`, and `homeexchange-processor`.

**Base:** `https://api.homeexchange.com`  
**Auth:** `authorization: Bearer <jwt>` + `he_web_version`  
**Token:** AWS SSM **`/homeexchange/bearer-token`** (SecureString), fetched at call time.

## Standing: credentials

- **Always** `ssm get-parameter --with-decryption` (or this skill’s script).
- **Never** write the bearer, `/homeexchange/credentials`, or poll secret to disk, skill files, GitHub, chat, or R2Memory.
- **Never** put a token on the CLI (`--token …`) — it lands in shell history.
- Do not print Authorization headers or JWT bodies. Redact if an error includes them.

| SSM path | What |
|---|---|
| `/homeexchange/bearer-token` | Access JWT (~24h). **This is what API calls use.** |
| `/homeexchange/credentials` | `{email,password}` for Lambda `he-token-refresh` only |
| `/homeexchange/poll-secret` | `cleaningbutton-api` HE poll |
| `/hospitable/bearer-token` | Hospitable PAT (Apt #2 and #1B calendar sync) |

On **401**: invoke Lambda **`he-token-refresh`**, then retry once.

## Pine mapping

| Unit | HE home | Hospitable | Airbnb |
|---|---|---|---|
| Apt **#3** | **`3202475`** | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` | `24259977` |
| Apt **#2** | **`3285044`** (created 2026-08-15) | `114663c5-0709-4eff-a868-fa9ebd6ed42d` | `20150380` |
| Apt **#1B** | **`3285159`** (created 2026-08-15) | `c899481f-2e5b-402d-80c4-3167fd824d96` | `20904545` |

Airbnb occupancy/revenue is skill **`hospitable`**.

## Live CLI

```bash
S=~/.grok/skills/home-exchange/scripts/he_api.py
python3 $S me
python3 $S homes
python3 $S home 3285159
python3 $S calendar 3285159
python3 $S conversations --limit 20
python3 $S publish 3285159
python3 $S request PATCH /v1/homes/3285159 --body '{"min_nights":3}'
python3 $S request PATCH /v1/homes/3285044 --body '{"prefers_reciprocal":false}'
python3 $S request PATCH /v1/users/5703979 --body '{"verified_only":true}'
```

`--json` dumps the API payload. Writes (`send`, `approve`, PATCH/POST) only when the user asked.

**Standing:** when you discover a working HE path or field, **append it here** (this table + listing prefs). Do not leave it only in chat.

## Listing prefs (Pine — all three homes unless noted)

| Setting | Where | Field | Pine value (2026-08-15) | Notes |
|---|---|---|---|---|
| Only request when dates marked available | home | `contact_allowed` | **`0`** all three | `0` = only available dates; `1` = any time in the year (HE default after **publish** — re-apply `0`) |
| Reciprocal exchange | home | `prefers_reciprocal` | **`false`** all three | UI: “For a reciprocal exchange, I want my home at 0 GuestPoints.” `true` = reciprocal-at-0-GP. Open nights are already `NON_RECIPROCAL` (GuestPoints only); processor never writes `RECIPROCAL`. |
| Verified members only | **user** `5703979` | `verified_only` | **`true`** | Account-wide (all homes). UI wants `verified_status>=1`; API accepted while Ruby is `-1` (on verification). |
| Publish | home | `status` | **`5`** all three | `5` online, `-5` offline. `GET /v1/homes/me` shows it; `GET /v1/homes/{id}` often omits it. Needs completion ≥ 80. |
| Min stay | home | `min_nights` | `3` all three | |
| Listing title | home `descriptions[]` | `title` | **#3** `Cozy West End Victorian \| EV Charging + Parking` (Airbnb). **#2** `1875 West End Victorian \| EV Charging + Parking`. **#1B** `Downtown Studio, Parking with EV charger` | PATCH full `descriptions[]` (`locale`,`title`,`good_feature`,`good_place`,`other`). Hospitable `public_name` = Airbnb title; `name` is the internal nickname. |
| Amenities | home `feature` | integer bitmasks | Matched to Hospitable/Airbnb 2026-08-15 (see catalog below) | **PATCH integers** (OR of bit IDs). Arrays are ignored (value stays old) or 400 on `kids`/`remote`/`surrounding`/`animal`. Frontend `featureArrayToFlag` XOR-reduces arrays → ints before send. |

```bash
python3 $S request PATCH /v1/homes/3202475 --body '{"contact_allowed":0,"prefers_reciprocal":false}'
python3 $S request PATCH /v1/homes/3285044 --body '{"contact_allowed":0,"prefers_reciprocal":false}'
python3 $S request PATCH /v1/homes/3285159 --body '{"contact_allowed":0,"prefers_reciprocal":false}'
python3 $S request PATCH /v1/users/5703979 --body '{"verified_only":true}'
```

## Endpoints (discovered)

Add new rows when a call succeeds. Source: live API + HE web `commons*.js`.

### Homes / listing

| Method | Path | Use |
|---|---|---|
| `GET` | `/v1/homes/me` | Our listings + `status`, `contact_allowed`, `prefers_reciprocal` |
| `GET` | `/v1/homes/{id}` | One home (detail, descriptions, images, feature). Often **omits** `status`. |
| `POST` | `/v1/homes` | Create. Required: `type` (2=apartment), `shared_part` (1), `address`, `location` `{street_number,street_name,formatted_address,zipcode,longitude,latitude}` |
| `PATCH` | `/v1/homes/{id}` | `min_nights`, `prefers_reciprocal`, `contact_allowed`, `detail`, **`descriptions[]`** (`locale`,`title`,`good_feature`,`good_place`,`other`), **`feature` integer bitmasks** (not arrays), `{"status":5}` publish |
| `GET` | `/v3/homes?user_id=` | GraphQL-style home list (`status` query uppercased) |
| `POST` | `/v1/homes/{id}/flag` | Flags (HE Collection etc.) |
| `GET` | `/v1/homes/{id}/ratings` | Listing reviews |
| `GET` | `/api/home/similar/{id}` | Similar homes |
| `GET` | `/v1/homes/disponibilities` | Legacy global disponibilities (numeric `type`). **Do not use** for Pine — use `/v1/homes/{id}/calendar`. |

### Calendar

| Method | Path | Use |
|---|---|---|
| `GET` | `/v1/homes/{id}/calendar` | `{updated_at, data:[{start_on,end_on,type,details}]}` half-open `[start,end)` |
| `POST` | `/v1/homes/{id}/calendar` | `{type, start_on, end_on}` upsert a range |
| `POST` | `/v1/homes/disponibilities` | Legacy `{start_on,end_on,type,home}` — prefer calendar POST |

Calendar `type`: `NON_RECIPROCAL` (GuestPoints — Pine default), `RECIPROCAL` (home swap), `available` (both, search UI), `RESERVED` (blocked/Airbnb), `UNAVAILABLE` (owner closed), `BOOKED` (HE exchange; `details.conversation_id`). Nights **not listed** are closed. Processor: all three homes, Hospitable `BLOCKED` → `UNAVAILABLE` (skip `BOOKED`), open gaps → `NON_RECIPROCAL`; June–Aug + Thanksgiving/Christmas/NYE → `UNAVAILABLE`.

### Inbox / exchanges

| Method | Path | Use |
|---|---|---|
| `GET` | `/v3/conversations/me?limit=` | Inbox (also `/v2/conversations/me`, `/v4/conversations`) |
| `GET` | `/v3/conversations/me/{id}` | One thread |
| `GET` | `/v1/conversations/stats/me` | Counts by status / preapproved |
| `GET` | `/v1/conversations/search` | Search threads |
| `POST` | `/v1/conversations/batch` / `…/archive` | Batch archive |
| `GET` | `/v3/messages?conversation_id=` | Thread body |
| `POST` | `/v1/messages` | `{content, conversation}` |
| `GET` | `/v3/messages/config` | Allowed email/link lists |
| `GET` | `/v1/exchanges/{conversationId}/get-exchanges` | Exchange array |
| `PATCH` | `/v1/exchanges/{conversationId}/approve` | Body = that array. **Conversation id, not exchange id** |
| `GET` | `/v1/exchanges/user/me?filter=&limit=&offset=` | User exchanges (`filter=all` 400 — use a real filter) |
| `GET` | `/v1/exchanges/restrictions` | `{has_post_expired_subscription_exchange}` |
| `GET` | `/v1/exchanges/approved/ready` | Ready-to-finalize |
| `POST` | `/v1/exchanges/{id}/modify/check` | Date/home/GP change preview |

### Users / account

| Method | Path | Use |
|---|---|---|
| `GET` | `/v1/users/me` | Self + `homes[]`, `verified_only`, `verified_status` (`-1` on verification, `0` not, `1` verified) |
| `PATCH` | `/v1/users/{id}` | `{verified_only:true}` and other user fields |
| `GET` | `/v1/users/{id}` | Public-ish profile |
| `GET` | `/v1/notification/headband` | Banner (204 if none) |
| `GET` | `/v1/users/me/alerts` | Saved searches |
| `GET` | `/v1/settings/mail-subscribe/list` | Email prefs |

### Photos

| Method | Path | Use |
|---|---|---|
| `POST` | `/v1/images/home/{id}` | Multipart `file=` JPEG/PNG (max 10MB) |
| `DELETE` | `/v1/images/{imageId}` | Remove photo |
| `PATCH` | `/v1/images/order` | Reorder |
| `POST` | `/v1/images/user` | Profile photo |

`size` on `detail` is **m²**; `localized_size` + `size_unit: "sqft"` is the display size (Apt 3 = 74 m² / 800 sqft).

## Amenities (`feature` bitmasks)

HE amenities are **not** Airbnb’s list. Source: HE web `commons*.js` `FEATURES` + `AMENITIES_BIT`. GET returns each category as an **int**; decode with `bit & value`.

**PATCH:** send `{"feature":{"practical":8100,"multimedia":1033,…}}` with **integer ORs**. Sending arrays (`[1,8,1024]`) returns 200 but **does not persist** (or 400 on `kids`/`remote`/`surrounding`/`animal`). `others` must be omitted (frontend deletes it).

```bash
# Apt #3 (dishwasher + freezer + bathtub + kids-toys + seaside)
python3 $S request PATCH /v1/homes/3202475 --body '{"feature":{"practical":8100,"multimedia":1033,"various":5,"personal":2,"rule":6,"kids":17,"remote":3,"surrounding":4}}'
# Apt #2 (bathtub, no dishwasher/freezer)
python3 $S request PATCH /v1/homes/3285044 --body '{"feature":{"practical":7968,"multimedia":1033,"various":5,"personal":2,"rule":6,"kids":16,"remote":3}}'
# Apt #1B (dishwasher, no bathtub/freezer) + re-apply contact_allowed after publish
python3 $S request PATCH /v1/homes/3285159 --body '{"contact_allowed":0,"prefers_reciprocal":false,"feature":{"practical":6948,"multimedia":1033,"various":5,"personal":2,"rule":6,"kids":16,"remote":3}}'
```

### Catalog (category → bit → name)

| Category | Bits |
|---|---|
| `practical` | 1 disabled-access · 4 dishwasher · 8 dryer · 16 washing-machine · 32 microwave · 128 freezer · 256 oven · 512 fridge · 1024 bathtub · 2048 heating-system · **4096 electric-car-plug** |
| `multimedia` | 1 tv · 2 computer · **8 wifi** · 16 home-cinema · 64 satellite · 128 phone · 512 console · 1024 smart-tv |
| `various` | **1 ac** · 2 elevator · **4 parking-space** · 8 piano · 16 jacuzzi · 32 sauna · 64 fireplace · 128 gym · 256 pool-table |
| `kids` | 1 kids-toys · 2 playground · 4 baby-gear · 8 secured-pool · 16 baby-bed (crib) |
| `remote` | 1 dedicated-work-space · 2 high-speed-connection |
| `rule` | 1 smokers-welcome · 2 pets-welcome · 4 children-welcome |
| `personal` | 1 doorman · 2 cleaning-person · 4 babysitter · 8 cook · 16 guide |
| `outdoor` | 1 garden · 2 pool · 4 bbq · 16 tennis · 32 ping-pong · 64 balcony |
| `transportation` | 1 car · 2 bicycle · 4 scooter · 8 motorcycle · 16 motorboat · 32 sailboat · 64 electric-car |
| `eco` | 1 renewable-energy · 2 low-consumption · 4 waste-sorting · 8 veg-garden · 16 public-transit · 32 solar |
| `surrounding` | 1 countryside · 2 mountains · 4 seaside · 8 lakes · 16 cities · 32 villages · 64 isolated · 128 island · 256 river |
| `animal` | 1 dog · 2 cat · 4 other |
| `favor` | 1 dog-to-feed · 2 cat-to-feed · 4 plants-to-water |

### Airbnb / Hospitable → HE (Pine)

Hospitable `GET /properties/{uuid}` `amenities[]` + `house_rules`. Only map what HE has. **No HE checkbox** for iron, hair dryer, hangers, shampoo, linens, smoke/CO/extinguisher, coffee maker, cooking basics, dishes, private entrance, long-term stays, blackout shades.

| Airbnb / Hospitable | HE |
|---|---|
| `ev_charger` | `practical` 4096 electric-car-plug |
| `wireless_internet` | `multimedia` 8 wifi + `remote` 2 high-speed-connection |
| `ac` | `various` 1 ac |
| `free_parking` / `street_parking` | `various` 4 parking-space |
| `heating` | `practical` 2048 heating-system |
| `tv` | `multimedia` 1 tv + 1024 smart-tv (Pine units are Roku/smart) |
| `kitchen` + `refrigerator` | `practical` 512 fridge |
| `oven` / `stove` | `practical` 256 oven |
| `microwave` | `practical` 32 microwave |
| `dishwasher` | `practical` 4 dishwasher (#1B, #3 only) |
| `freezer` | `practical` 128 freezer (#3 only — listed on Airbnb) |
| `bathtub` | `practical` 1024 bathtub (#2, #3 only) |
| `laptop_friendly_workspace` | `remote` 1 dedicated-work-space |
| `crib` / `pack_n_play_travel_crib` | `kids` 16 baby-bed + `rule` 4 children-welcome |
| `childrens_books_and_toys` | `kids` 1 kids-toys (#3 only) |
| `house_rules.pets_allowed` | `rule` 2 pets-welcome (all three) |
| (copy: cleaner / cleaning fee) | `personal` 2 cleaning-person |
| `iron`, `hair_dryer`, washers, detectors… | **no HE field** |

Washer/dryer: **none** of the three Airbnb listings have them — do not set 8/16.

### Pine live values (2026-08-15)

| Unit | practical | multimedia | various | kids | remote | rule | personal |
|---|---|---|---|---|---|---|---|
| #3 `3202475` | 8100 (dishwasher+microwave+freezer+oven+fridge+bathtub+heating+EV) | 1033 | 5 | 17 | 3 | 6 | 2 |
| #2 `3285044` | 7968 (microwave+oven+fridge+bathtub+heating+EV) | 1033 | 5 | 16 | 3 | 6 | 2 |
| #1B `3285159` | 6948 (dishwasher+microwave+oven+fridge+heating+EV) | 1033 | 5 | 16 | 3 | 6 | 2 |

Required headers (script sets these):

```
Accept: application/json
authorization: Bearer <ssm>
he_web_version: 20.29.1-rc.1
origin: https://www.homeexchange.com
referer: https://www.homeexchange.com/conversations
```

## Calendar sync (AWS)

`jeromevidaao/home-exchange-cal-sync` Lambda `homeexchange-processor`:

- Daily `sync_availability`: Apt **#3** from Airbnb iCal **plus** Hospitable calendar; Apt **#2** and Apt **#1B** from Hospitable `GET /v2/properties/{uuid}/calendar` (SSM `/hospitable/bearer-token`). Hospitable `BLOCKED` nights (manual USER blocks, vendor API blocks) are written to HE as `UNAVAILABLE` for every listing; HE `BOOKED` exchanges are skipped. Then June–Aug + holidays `UNAVAILABLE`.
- Reservation webhooks on `home-exchange-reservations` SQS: block HE calendar for **#1B, #2, or #3** (`HE_HOMES`). Other properties are dropped.

## Pre-approve

1. Dates open on **both** Hospitable and `GET /v1/homes/{heHomeId}/calendar` for that unit.
2. `GET /v1/exchanges/{conversationId}/get-exchanges` then `PATCH …/approve` with that array.
3. Hospitable `PUT calendar` `available:false` for `[checkIn, checkOut)`.
4. Guest text: **I just sent you a pre-approval and blocked those dates for you.** Never “you’re booked.”

## Implementation map

| Layer | Location |
|---|---|
| This CLI | `~/.grok/skills/home-exchange/scripts/he_api.py` |
| API HE chat + poll | `~/cleaningbutton-api/index.js` |
| Auto-reply / approve | `~/auto-reply-sqs-harness/src/clients/HomeExchangeClient.js` |
| Calendar sync | `~/home-exchange-cal-sync` (`HE_HOMES`) |
| Token refresh | Lambda `he-token-refresh` |

## Slash

`/home-exchange` → run `he_api.py` for the user’s ask (default `homes` if unspecified). Never echo the bearer.
