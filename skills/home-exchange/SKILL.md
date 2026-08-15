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

#1B is **not** on HE. Airbnb occupancy/revenue is skill **`hospitable`**.

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
```

`--json` dumps the API payload. Writes (`send`, `approve`, PATCH/POST) only when the user asked.

## Endpoints (discovered)

| Method | Path | Use |
|---|---|---|
| `GET` | `/v1/users/me` | Self + `homes[]`. `verified_only` = verified-members-only requests |
| `PATCH` | `/v1/users/{id}` | User prefs. `{"verified_only": true}` = only verified members can send requests (account-wide) |
| `GET` | `/v1/homes/me` | Our listings only |
| `GET` | `/v1/homes/{id}` | One home (detail, descriptions, images, feature) |
| `POST` | `/v1/homes` | **Create** listing. Required: `type` (2=apartment), `shared_part` (1), `address`, `location` `{street_number,street_name,formatted_address,zipcode,longitude,latitude}` |
| `PATCH` | `/v1/homes/{id}` | Update `min_nights`, `prefers_reciprocal`, `detail`, `descriptions[]`, `feature` bit arrays, **`contact_allowed`**. **`{"status": 5}` publishes** (needs completion ≥ 80). Status **5** = online, **-5** = offline/unpublished. `GET /v1/homes/me` shows status; `GET /v1/homes/{id}` often omits it. |
| `POST` | `/v1/images/home/{id}` | Multipart `file=` JPEG/PNG (max 10MB) |
| `DELETE` | `/v1/images/{imageId}` | Remove photo |
| `PATCH` | `/v1/images/order` | Reorder |
| `GET` | `/v3/conversations/me?limit=` | Inbox |
| `GET` | `/v3/conversations/me/{id}` | One thread |
| `GET` | `/v3/messages?conversation_id=` | Thread body |
| `POST` | `/v1/messages` | `{ content, conversation }` — conversation id |
| `GET` | `/v1/homes/{homeId}/calendar` | `[start_on, end_on)` ranges |
| `POST` | `/v1/homes/{homeId}/calendar` | `{ type, start_on, end_on }` |
| `GET` | `/v1/exchanges/{conversationId}/get-exchanges` | Exchange array |
| `PATCH` | `/v1/exchanges/{conversationId}/approve` | Body = that array. **Conversation id, not exchange id** |

`size` on `detail` is **m²**; `localized_size` + `size_unit: "sqft"` is the display size (Apt 3 = 74 m² / 800 sqft).

Calendar **contact preference** (`contact_allowed` on the home — Calendar → contact preferences):

| Value | HE UI |
|---|---|
| **`0`** | **Members can only send me requests when my home is marked as being available** (`CONTACT_NOT_ALLOWED_ON_UNAVAILABLE`) |
| **`1`** | Members can send me requests at any time in the year (`CONTACT_ALLOWED_ON_UNAVAILABLE`, API default after publish) |

Publishing / unpublishing resets this to **`1`**. Re-apply `PATCH {"contact_allowed": 0}` after publish. Both Pine homes set to **`0`** on 2026-08-15 (Apt **#3** `3202475`, Apt **#2** `3285044`).

**According to members’ status** is a **user** flag (both homes), not per listing:

| Field | Value | HE UI |
|---|---|---|
| `verified_only` | **`true`** | Only receive exchange requests from members whose accounts have been verified |

`PATCH /v1/users/{userId}` with `{"verified_only": true}`. UI also requires `verified_status >= 1` (verified) to toggle; the API still accepted it while Ruby’s account is `verified_status=-1` (on verification). Set **true** 2026-08-15 (user `5703979`).

```bash
python3 $S request PATCH /v1/homes/3202475 --body '{"contact_allowed":0}'
python3 $S request PATCH /v1/homes/3285044 --body '{"contact_allowed":0}'
python3 $S request PATCH /v1/users/5703979 --body '{"verified_only":true}'
```

Calendar types: `NON_RECIPROCAL` (open for GuestPoints), `RESERVED` (blocked/booked), `UNAVAILABLE`. Nights not listed are closed. **June–August** + Thanksgiving/Christmas/NYE are forced `UNAVAILABLE` by `homeexchange-processor` on **both** homes.

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
