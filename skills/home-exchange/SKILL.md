---
name: home-exchange
description: >
  HomeExchange (HE) API for CleaningButton Pine Apt #3: inbox, calendar,
  exchanges, pre-approve. Always load the bearer from AWS SSM
  /homeexchange/bearer-token — never store tokens locally or in git.
  Use when the user asks about HomeExchange, HE guests, HE calendar,
  HE conversations, pre-approve, or runs /home-exchange.
---

# HomeExchange API

Undocumented web API used by homeexchange.com. Same client as `cleaningbutton-api` HE chat and `auto-reply-sqs-harness` `HomeExchangeClient`.

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
| `/homeexchange/refresh-token` | optional Auth0 refresh (usually empty) |

On **401**: invoke Lambda **`he-token-refresh`** (reads credentials from SSM, writes a new bearer), then retry once.

## Live CLI

```bash
S=~/.grok/skills/home-exchange/scripts/he_api.py
python3 $S me
python3 $S conversations --limit 20
python3 $S messages CONVERSATION_ID
python3 $S calendar            # home 3202475
python3 $S exchanges CONVERSATION_ID
python3 $S send CONVERSATION_ID --text "…"
python3 $S approve CONVERSATION_ID --yes
```

`--json` dumps the API payload. Writes (`send`, `approve`) only when the user asked.

## Pine mapping

| | |
|---|---|
| HE home | **`3202475`** |
| Hospitable Apt **#3** | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` |
| Airbnb listing | `24259977` |

HE guest stays are Apt **#3** only. Airbnb occupancy/revenue is skill **`hospitable`**, not this API.

## Endpoints we actually call

| Method | Path | Use |
|---|---|---|
| `GET` | `/v1/users/me` | Self id / email |
| `GET` | `/v3/conversations/me?limit=` | Inbox |
| `GET` | `/v3/conversations/me/{id}` | One thread |
| `GET` | `/v3/messages?conversation_id=` | Thread body |
| `POST` | `/v1/messages` | `{ content, conversation }` — **conversation id** (int if numeric) |
| `GET` | `/v1/homes/{homeId}/calendar` | `[start_on, end_on)` ranges |
| `POST` | `/v1/homes/{homeId}/calendar` | `{ type, start_on, end_on }` — owned by `homeexchange-processor` |
| `GET` | `/v1/exchanges/{conversationId}/get-exchanges` | Exchange array |
| `PATCH` | `/v1/exchanges/{conversationId}/approve` | Body = that array. **Conversation id, not exchange id** (exchange-id URL is a 400 PHP Undefined offset) |

Calendar range types: `NON_RECIPROCAL` (open for GuestPoints), `RESERVED` (blocked/booked). Nights not listed are closed (owner long-block). June–August + listed holidays are forced `UNAVAILABLE` by cal-sync.

Required headers (script sets these):

```
Accept: application/json
authorization: Bearer <ssm>
he_web_version: 20.29.1-rc.1
origin: https://www.homeexchange.com
referer: https://www.homeexchange.com/conversations
```

## Pre-approve (do not invent a different path)

1. Dates open on **both** Hospitable and `GET /v1/homes/3202475/calendar`.
2. `GET /v1/exchanges/{conversationId}/get-exchanges` then `PATCH …/approve` with that array. Skip if already `approved_at` / `finalized_at`.
3. Hospitable `PUT calendar` `available:false` for `[checkIn, checkOut)` (checkout day stays free).
4. Guest text: **I just sent you a pre-approval and blocked those dates for you.** Never “you’re booked.”

Retries in production: 4×, 5s / 15s / 30s. Permanent 4xx (except 408/429) do not retry.

## Implementation map

| Layer | Location |
|---|---|
| This CLI | `~/.grok/skills/home-exchange/scripts/he_api.py` |
| API HE chat + poll | `~/cleaningbutton-api/index.js` (`heRequest`, `hePollNewMessages`) |
| Auto-reply / approve | `~/auto-reply-sqs-harness/src/clients/HomeExchangeClient.js` |
| Calendar sync | `~/home-exchange-cal-sync` (`homeexchange-processor`) |
| Token refresh | Lambda `he-token-refresh` + Chrome ext backup |

## Slash

`/home-exchange` → run `he_api.py` for the user’s ask (default `me` + `conversations` if unspecified). Never echo the bearer.
