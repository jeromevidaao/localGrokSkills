---
name: home-exchange
description: >
  HomeExchange (HE) API for CleaningButton Pine Apt #3 and Apt #2: inbox,
  listings, calendar, photos, exchanges, pre-approve. Always load the bearer
  from AWS SSM /homeexchange/bearer-token — never store tokens locally or in git.
  Use when the user asks about HomeExchange, HE guests, HE calendar,
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
| `/hospitable/bearer-token` | Hospitable PAT (Apt #2 calendar sync) |

On **401**: invoke Lambda **`he-token-refresh`**, then retry once.

## Pine mapping

| Unit | HE home | Hospitable | Airbnb |
|---|---|---|---|
| Apt **#3** | **`3202475`** | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` | `24259977` |
| Apt **#2** | **`3285044`** (created 2026-08-15) | `114663c5-0709-4eff-a868-fa9ebd6ed42d` | `20150380` |
| Apt **#1B** | **`3285159`** (draft, `status=-5`, completion 50) | `c899481f-2e5b-402d-80c4-3167fd824d96` | `20904545` |

Airbnb occupancy/revenue is skill **`hospitable`**. Do **not** publish 1B unless Jerome asks.

## Live CLI

```bash
S=~/.grok/skills/home-exchange/scripts/he_api.py
python3 $S me
python3 $S homes
python3 $S home 3285044
python3 $S calendar 3285044
python3 $S conversations --limit 20
python3 $S publish 3285044
python3 $S request PATCH /v1/homes/3285044 --body '{"min_nights":3}'
python3 $S request PATCH /v1/homes/3285044 --body '{"prefers_reciprocal":false}'
python3 $S request PATCH /v1/users/5703979 --body '{"verified_only":true}'
```

`--json` dumps the API payload. Writes (`send`, `approve`, PATCH/POST) only when the user asked.

**Standing:** when you discover a working HE path or field, **append it here** (this table + listing prefs). Do not leave it only in chat.

## Listing prefs (Pine — both homes unless noted)

| Setting | Where | Field | Pine value (2026-08-15) | Notes |
|---|---|---|---|---|
| Only request when dates marked available | home | `contact_allowed` | **`0`** both | `0` = only available dates; `1` = any time in the year (HE default after **publish** — re-apply `0`) |
| Reciprocal exchange | home | `prefers_reciprocal` | **`false`** both | UI: “For a reciprocal exchange, I want my home at 0 GuestPoints.” `true` = reciprocal-at-0-GP. Open nights are already `NON_RECIPROCAL` (GuestPoints only); processor never writes `RECIPROCAL`. |
| Verified members only | **user** `5703979` | `verified_only` | **`true`** | Account-wide (both homes). UI wants `verified_status>=1`; API accepted while Ruby is `-1` (on verification). |
| Publish | home | `status` | **`5`** both | `5` online, `-5` offline. `GET /v1/homes/me` shows it; `GET /v1/homes/{id}` often omits it. Needs completion ≥ 80. |
| Min stay | home | `min_nights` | `3` both | |
| Listing title | home `descriptions[]` | `title` | **#3** `Cozy West End Victorian \| EV Charging + Parking` (Airbnb). **#2** `1875 West End Victorian \| EV Charging + Parking` | PATCH full `descriptions[]` (`locale`,`title`,`good_feature`,`good_place`,`other`). Hospitable `public_name` = Airbnb title; `name` is the internal nickname. |

```bash
python3 $S request PATCH /v1/homes/3202475 --body '{"contact_allowed":0,"prefers_reciprocal":false}'
python3 $S request PATCH /v1/homes/3285044 --body '{"contact_allowed":0,"prefers_reciprocal":false}'
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
| `PATCH` | `/v1/homes/{id}` | `min_nights`, `prefers_reciprocal`, `contact_allowed`, `detail`, **`descriptions[]`** (`locale`,`title`,`good_feature`,`good_place`,`other`), `feature` bit arrays, `{"status":5}` publish |
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

Calendar `type`: `NON_RECIPROCAL` (GuestPoints — Pine default), `RECIPROCAL` (home swap), `available` (both, search UI), `RESERVED` (blocked/Airbnb), `UNAVAILABLE` (owner closed), `BOOKED` (HE exchange; `details.conversation_id`). Nights **not listed** are closed. Processor: both homes, open gaps → `NON_RECIPROCAL`; June–Aug + Thanksgiving/Christmas/NYE → `UNAVAILABLE`.

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

Feature PATCH: send bit IDs as arrays (`multimedia: [1, 8, 1024]` = TV + wifi + smart TV). Sending the OR’d integer (`1033`) does **not** expand bits. Categories `remote` / `kids` / `surrounding` / `animal` 400 on this form.

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

- Daily `sync_availability`: Apt **#3** from Airbnb iCal; Apt **#2** from Hospitable `GET /v2/properties/{uuid}/calendar` (SSM `/hospitable/bearer-token`). Then June–Aug + holidays `UNAVAILABLE`.
- Reservation webhooks on `home-exchange-reservations` SQS: block HE calendar for **#2 or #3** (`HE_HOMES`). Other properties are dropped.

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
