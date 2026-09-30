---
name: home-exchange
description: >
  HomeExchange (HE) API for CleaningButton Pine Apt #3, Apt #2, and Apt #1B:
  inbox, listings, calendar, photos, exchanges, pre-approve, destination search,
  outbound stay requests. Always load the bearer from AWS SSM
  /homeexchange/bearer-token — never store tokens locally or in git. Use when
  the user asks about HomeExchange, HE guests, HE calendar, HE conversations,
  pre-approve, searching HE homes, contacting a host, or runs /home-exchange.
---

# HomeExchange API

Undocumented web API used by homeexchange.com. Same client as `cleaningbutton-api` HE chat, `auto-reply-sqs-harness` `HomeExchangeClient`, and `homeexchange-processor`.

**Base:** `https://api.homeexchange.com` (listings, inbox, calendar)  
**Search / stay-request BFF:** `https://bff.homeexchange.com` (destination search + `POST /exchange/v3`)  
**Auth:** `authorization: Bearer <jwt>` + `he_web_version` (`20.32.0-rc.1`)  
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

**Harness (2026-09-30):** `HomeExchangeClient` does this in-process — on HE HTTP 401 it invokes `he-token-refresh` (or an injectable `tokenRefresh` hook), clears the bearer cache, reloads SSM `/homeexchange/bearer-token`, stamps `/homeexchange/last-token-received` (epoch seconds; never the JWT), and retries the same HE call **once**. HE-only paths (approve / send / decline) still fail closed if refresh+retry cannot recover. Mixed occupancy (`loadCurrentGuestsByListing` for early_checkin / lockout / smoke) treats HE `listConversations` as **best-effort**: after client refresh+retry still fails, log and continue with Hospitable/Airbnb guests so an HE outage does not abort Airbnb unit-ready (`occupancy_lookup_failed`). Do not merge `/homeexchange/credentials` into the bearer parameter.

**IAM (2026-09-30, production):** harness role `auto-reply-sqs-role-3i2ozrop` may invoke `he-token-refresh` via resource-based Sid `GuestMessagingHarnessInvokeHeTokenRefresh` (Titan `PutRolePolicy` AccessDenied). Optional out-of-band identity `HeTokenRefreshInvokeAndStamp` for `ssm:PutParameter` on `/homeexchange/last-token-received` (stamp soft-fails without it).

## Pine mapping

| Unit | HE home | Hospitable | Airbnb |
|---|---|---|---|
| Apt **#3** | **`3202475`** | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` | `24259977` |
| Apt **#2** | **`3285044`** (created 2026-08-15) | `114663c5-0709-4eff-a868-fa9ebd6ed42d` | `20150380` |
| Apt **#1B** | **`3285159`** (created 2026-08-15) | `c899481f-2e5b-402d-80c4-3167fd824d96` | `20904545` |

Airbnb occupancy/revenue is skill **`hospitable`**.

**Auto-reply wiring (Katie 2026-08-17):** `heBuildAutoReplySqsPayload` and harness `resolveHeUnit` must map the HE home id to **that** unit’s Hospitable UUID + Airbnb listing. Never hardcode Apt #3 when `listing.platform_id` is `3285044` or `3285159`.

**Host-only auto-reply (Jen 2026-09-02):** Poller + harness send **only when we are the host of a Pine home**. Outbound guest threads (we contacted Jen / Vina / Dan / Janet) FCM the owner but must not run auto-reply — Jen declined our Kailua request and got “You're welcome, Jen!”. Reciprocal (our listing + theirs, Nina/Marie) still replies because we are hosting.

## Live CLI

```bash
S=~/.grok/skills/home-exchange/scripts/he_api.py
python3 $S me
python3 $S homes
python3 $S home 3285159
python3 $S calendar 3285159
python3 $S conversations --limit 20
python3 $S publish 3285159
python3 $S request PATCH /v1/homes/3285159 --body '{"min_nights":2}'
python3 $S request PATCH /v1/homes/3285044 --body '{"prefers_reciprocal":false}'
python3 $S request PATCH /v1/users/5703979 --body '{"verified_only":true}'
python3 $S search --place manhattan --from 2026-12-25 --to 2027-01-03 --adults 2 --children 3 --bedrooms 3
python3 $S search --place oahu --from 2026-12-28 --to 2027-01-03 --adults 2 --children 1
python3 $S request-stay --home 2087763 --from 2026-12-28 --to 2027-01-03 --adults 2 --children 1 --text "…" --yes
python3 $S decline 95201321 --yes   # WITH-GP pending only; reciprocal is skipped
```

`--json` dumps the API payload. Writes (`send`, `request-stay`, `approve`, `decline`, PATCH/POST) only when the user asked.

**Standing:** when you discover a working HE path or field, **append it here** (this table + listing prefs). Do not leave it only in chat.

## Standing: destination search (Jerome 2026-08-16)

**GuestPoints only — never reciprocal unless he explicitly asks to swap.**

| Default | Value |
|---|---|
| Exchange type | **`calendar.exchange_types: ["available","guest-wanted"]`**. `available` = nights open to GP *or* swap; `guest-wanted` = GP-only nights. **Both take points.** Do not send only `guest-wanted` (drops dual/`AVAILABLE` homes). Reciprocal-only = `["reciprocal"]` — omit unless he asks to swap. Other strings 422. |
| Host quality | `filters: ["response-rate-above-threshold"]` (~≥80%) unless he says skip |
| Kids | Amenity `children-welcome` only if he asks or results are plentiful (stacking it on scarce dates can zero the set). Filter tag 422. |
| Bedrooms | **Match the party.** 2 adults + 1 child (Hawaii family): **no 3BR min**. Manhattan 5 people / 3 kids: **`--bedrooms 3`**. Katherine [1673876](https://www.homeexchange.com/homes/view/1673876) is **1 BR** — do not re-offer for that stay. BFF `detail.bedroom_nb` confirms (API `bedrooms_nb` is often null). |
| CLI | `he_api.py search` defaults to points + response-rate + calendar verify |
| Result rows | **Always show the HE listing id** as a clickable markdown link `[1673876](https://www.homeexchange.com/homes/view/1673876)`. **Never** `/home/{id}` — that is a **404**. `/homes/view/{id}` 200s (lands on `/holiday-home/{id}`). Test a new URL pattern with GET before presenting. Never title-only. |

Do **not** first-contact hosts unless he picks a listing.

### Fast-track playbook (every dest search)

1. Parse: place, dates (checkout = last day mentioned), guests. “5 people and 3 kids” = **2 adults + 3 children** unless he says 5 adults. Year = next occurrence of those dates.
2. `python3 $S search --place <city> --from YYYY-MM-DD --to YYYY-MM-DD --adults N --children N`  
   Add `--bedrooms 3` only when the stay needs it (Manhattan 5-person). Known polygons: `manhattan`, `nyc`. `oahu` / `honolulu` / any other city → Nominatim bounds (no Jawg token on disk). Or `--location-id whosonfirst:…`.
3. CLI already: GuestPoints (`available`+`guest-wanted`), good response rate, drops `min_nights` > stay, **Manhattan clip** (polygon leaks Brooklyn / Jersey City / Queens), **calendar verify** (keep `AVAILABLE` / `NON_RECIPROCAL`, drop `RECIPROCAL`-only). `--children-welcome` if he wants that amenity. Calendar ranges are half-open `[start,end)` — checkout day is `end`.
4. Rank by `resp` then `exchange_count`. Present a short table whose **first column is Listing** = markdown `[id](https://www.homeexchange.com/homes/view/{id})` (numeric id visible + clickable). Then host, area, capacity, reply %, GP/night + stay total, calendar type. **Never** `https://www.homeexchange.com/home/{id}` (404). If a new path is guessed, GET it first and confirm 200 + listing title before showing or `open`.
5. Skip titles that demand reciprocal / beach / ski only, and `min_nights` longer than the stay. Confirm `detail.bedroom_nb` on `GET /v1/homes/{id}`.
6. If he asks for reciprocal, rerun `--exchange reciprocal`. Never send messages in this step.

`--no-response-rate` / `--no-verify` / `--exchange both` only when asked.

### Current dest search (2026-08-16)

Manhattan · **2026-12-25 → 2027-01-03** (9 nights) · 2 adults + 3 children · GuestPoints · **≥ 3 BR**.

| Listing | Host | Beds | Area | Reply | Notes |
|---|---|---|---|---|---|
| [3192196](https://www.homeexchange.com/homes/view/3192196) | Tracey | 3BR/2BA · ~1700 sqft · 2 floors | Inwood / Washington Heights | 68% | Best family fit. `NON_RECIPROCAL` those nights. ~360 GP/night. |
| [2466431](https://www.homeexchange.com/homes/view/2466431) | Olivier | 3BR/3BA · 3 kings | Upper East Side | 20% | Weak reply. ~327 GP/night. |
| [2779098](https://www.homeexchange.com/homes/view/2779098) | Ed | 3BR/2BA · ~160 m² | Chelsea | 17% | Kids’ bed. Weak reply. ~378 GP/night. |
| [992945](https://www.homeexchange.com/homes/view/992945) | Elise & Michael | 3BR/2BA | **LIC / Queens** (not island) | 75% | Strongest host; one subway stop from Midtown. ~341 GP/night. |

Do **not** re-offer [1673876](https://www.homeexchange.com/homes/view/1673876) Katherine (1 BR / 650 sqft) or [3099298](https://www.homeexchange.com/homes/view/3099298) Julian (1 BR). Dropped: Sandy [916443](https://www.homeexchange.com/homes/view/916443) min 14, Kim [2547120](https://www.homeexchange.com/homes/view/2547120) min 20, Olga [1253413](https://www.homeexchange.com/homes/view/1253413) no GPs.

Manhattan clip: keep Inwood (`lat≥40.82` east to −73.91). Never substring-match `lic ` (hits “pub**lic** transit”). BFF `detail.bedroom_nb` / `bathroom_nb` — API `bedrooms_nb` is often null.

### Current dest search (2026-08-28)

Oahu · **2026-12-28 → 2027-01-03** (6 nights) · 2 adults + 1 child (6yo) · GuestPoints · **no 3BR min**.

| Listing | Host | Beds | Area | Reply | Notes |
|---|---|---|---|---|---|
| [2087763](https://www.homeexchange.com/homes/view/2087763) | Vina | 2BR/1BA · 1200 sqft · cap 6 | Kaimuki / Wilhelmina Rise | 88–89% | Only GP listing covering checkout **3 Jan**. Car, parking, stairs. **$150 cleaning**. `NON_RECIPROCAL` 15 Dec → 8 Jan. |
| [2471881](https://www.homeexchange.com/homes/view/2471881) | Catherine | 3BR/2BA | Manoa | 100% | Calendar open through 3 Jan but **min 7** — search drops a 6-night stay. |
| [2778013](https://www.homeexchange.com/homes/view/2778013) | Jen | 3BR/2BA · Kailua Beach | Kailua | 94% | Checkout **2 Jan** — misses the 2 Jan night. |
| [2788923](https://www.homeexchange.com/homes/view/2788923) | Dan | 3BR/2BA · 2100 sqft | Kailua | 100% | Checkout **1 Jan**, then `BOOKED`. |

Outreach 2026-08-28: **not sent**. Ruby user `5703979` `verified_status=-1` (on verification). HE blocks new stay requests until `verified_status>=1`.

## Outbound stay request (guest contacting a host)

HE web `createStayRequestV3` → **BFF** (not `api.homeexchange.com`).

```bash
python3 $S me   # refuse if verified_status != 1
python3 $S request-stay --home 2087763 --from 2026-12-28 --to 2027-01-03 \
  --adults 2 --children 1 --text "…" --yes
```

| | |
|---|---|
| Endpoint | `POST https://bff.homeexchange.com/exchange/v3` |
| Body | `{stayType, startDate, endDate, homeId, hostId, guestId, guestNumber, content}` |
| `stayType` | **`WITH-GP`** (GuestPoints, default) · `RECIPROCAL` · `RECIPROCAL-WITH-GP`. Strings only. Numeric `1` **400**. |
| `guestNumber` | adults+children+babies |
| Message | No emails or links (HE 400). UI warns if under ~35 words. Sign as **Ruby** (account `first_name`). |
| Verify first | `GET /v1/users/me` `verified_status` **must be `1`**. `-1` = on verification — do not send. |
| 429 | `"Rate limit exceeded too many request"` after a failed POST. **Do not loop.** Wait (minutes, not seconds) and retry once. |

Do **not** first-contact hosts unless he picks a listing **and** the account is verified.

**Auto-reply must not fire on these threads.** We are the guest. Poller FCM is fine; SQS auto-reply is host-only (Jen 2026-09-02).

## Listing prefs (Pine — all three homes unless noted)

| Setting | Where | Field | Pine value (2026-08-15) | Notes |
|---|---|---|---|---|
| Only request when dates marked available | home | `contact_allowed` | **`0`** all three | `0` = only available dates (UI: “Members can only send me requests when my home is marked as being available”). `1` = any time in the year. HE defaults to `1` after **publish** and randomly flips back to `1` after calendar writes / reservation blocks (Catherine / Downtown Studio 2026-09-07: daily sync restored `0`, then `blockCalendar` left `1` again). `he_api.py publish` re-applies `0`. **Durable fix (main `bf33db6`, 2026-09-07):** `homeexchange-processor` **unconditionally force-PATCHes** `HE_LISTING_PREFS` (`contact_allowed:0`, `prefers_reciprocal:false`) on every `sync_availability` **and** after every reservation `blockCalendar` — never skip based on GET. Logs: `force-setting … reason=sync_availability|reservation_block`. Check live: `python3 $S homes --json` → `contact_allowed`. |
| Reciprocal exchange | home | `prefers_reciprocal` | **`false`** all three | UI: “For a reciprocal exchange, I want my home at 0 GuestPoints.” `true` = reciprocal-at-0-GP. **Does not block inbound swaps** — guests can still send `exchange.type=2` (Nina 2026-08-29). Auto-reply **messages** that we only host GuestPoints stays. HE has **no pending decline for reciprocal** (see Inbox / exchanges). Open nights are already `NON_RECIPROCAL`; processor never writes `RECIPROCAL`. |
| Verified members only | **user** `5703979` | `verified_only` | **`true`** | Account-wide (all homes). UI wants `verified_status>=1`; API accepted while Ruby is `-1` (on verification). |
| Publish | home | `status` | **`5`** all three | `5` online, `-5` offline. `GET /v1/homes/me` shows it; `GET /v1/homes/{id}` often omits it. Needs completion ≥ 80. |
| Min stay | home | `min_nights` | **`2`** all three | UI: “Minimum of nights recommended.” (was 1; set 2026-08-15) |
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

Calendar `type`: `NON_RECIPROCAL` (GuestPoints — Pine default), `RECIPROCAL` (home swap), `available` (both, search UI), `RESERVED` (blocked/Airbnb), `UNAVAILABLE` (owner closed), `BOOKED` (HE exchange; `details.conversation_id`). Nights **not listed** are closed. Processor: all three homes, Hospitable `BLOCKED` → `UNAVAILABLE` (skip `BOOKED`), open gaps → `NON_RECIPROCAL`; **May 15–Oct 31** (every year) + Thanksgiving/Christmas/NYE → `UNAVAILABLE`. Airbnb/Hospitable stay open for paid stays.

### Inbox / exchanges

| Method | Path | Use |
|---|---|---|
| `GET` | **BFF** `/exchange/conversations/me?first=` | **Inbox source of truth** (Jessica 2026-09-26, id `1000201434`). New ~1e9+ conversation ids are **missing** from api `/v3/conversations/me` and `/v2`. |
| `GET` | `/v3/conversations/me?limit=` | Legacy inbox (incomplete for new threads — do not use alone) |
| `GET` | `/v3/conversations/me/{id}` | One thread |
| `GET` | `/v1/conversations/stats/me` | Counts by status / preapproved |

Conversation `GET /v3/conversations/me/{id}` (used by Android/web HE chat header):

| Field | Use |
|---|---|
| `interlocutor.images[].cdn_link` | Guest profile photo (`images.homeexchange.com`) |
| `exchanges[]` / `all_exchanges[]` | Each requested stay (can be our home **and** their home) |
| `exchange.start_on` / `end_on` | Check-in / check-out (`YYYY-MM-DD`, half-open) |
| `exchange.home.id` + `home.descriptions[].title` + `home.images[].cdn_link` | Listing they are booking (map `3202475`/`3285044`/`3285159` → Apt #3/#2/#1B) |
| `exchange.status` | **0** requested · **1** pre-approved (`approved_at`) · **3** finalized (`finalized_at`) · **5** cancelled (`canceleted_at`) |
| `exchange.type` | **1** GuestPoints (`WITH-GP`) · **2** reciprocal home swap (`guestpoint_amount` 0, often a second exchange on *their* home). Pine **only accepts type 1**. Auto-reply **messages** that we don't do home swaps. **Do not** convert type 2 → WITH-GP. |
| Conversation `accepted` | `null` pending · `false` host declined the request (unstarted). Form children on `PATCH /v1/conversations/{id}` are `title`, `accepted`. |
| System chat `type` / `type_auto` | **type 0** user chat · **type 1** system. `type_auto` **1** host approved · **2** guest finalized · **3** cancelled pre-approval · **9/10** modified start/end date · **15** host/guest transformed into a **non-reciprocal** (WITH-GP) · **16** transformed into a **reciprocal** swap (Nina). There is **no** “declined the request” system line. Conversation `last_message` often **does not update** for type=1 — poll watches `reservationStatus` / `finalized_at` and enqueues `act=homeexchange_approval_status`. Auto-reply thanks the guest for confirming (never "You're welcome", never re-approve). First-message path must ignore system lines when counting `message_count`. |
| `exchange.guest_nb` / `night_nb` | Party size / nights |
| `exchange.guest.phone` | E.164 **on conversation DETAIL only** (`GET /v3/conversations/me/{id}`). Inbox list omits it. Present after pre-approve (`status=1`) or finalize (`status=3`). Last-4 is the Schlage PIN — see `addDeleteCodeWiFiPyschlage`. Never log the full number. |
| `exchange.guest.email` | Also on conversation detail after approve/finalize. Do not store in git / R2Memory. |

**Pending stay decline (2026-08-29):** HE product has **no host decline for a pending reciprocal stay.** `PATCH …/manual-decline` is WITH-GP-only. After any host user-chat the thread is “in conversation”: 4-day auto-decline stops, and HE staff (forum, Sep 2025) say you cannot manually decline and do not need to. Auto-reply: send the GuestPoints-only / dates-closed message; **leave the stay `NEW` `RECIPROCAL`**. Do not convert. Closed WITH-GP still uses `manual-decline`. Restore a mistaken convert with `change-to-reciprocal/{theirHomeId}`.

`cleaningbutton-api` `act=homeexchange_messages` returns `guestImageUrl`, `checkIn`, `checkOut`, `unitLabel`, `reservationStatus`, `exchanges[]`.

Owner Android FCM (HE poll every 5m, `act=homeexchange_poll`): new guest chat is `homeexchange_message`. **Guest finalized / accepted** (exchange `status` 3 after we had them as Requested/Pre-approved) is `homeexchange_reservation_accepted` — title `HE guest accepted — {name}`, tap opens the HE chat. Cursor stores `reservationStatus` so we notify once on the transition, not on historical finalized threads.

**Check-in instructions (3 days before arrival):** poller also enqueues `act=homeexchange_checkin_instructions` onto `grok_message` for finalized Pine stays when `daysUntilCheckIn <= 3` (same-day / 2-day accepts go out immediately). Conversation DETAIL `exchange.guest.phone` last-4 is the keypad PIN. Templates live in S3 `s3://cleaningbutton-ai-context-us-east-1/data/checkin-templates/apt-{1b,2,3}.json` (must match HE home `3285159` / `3285044` / `3202475`). Harness never defaults an unknown home to Apt #3. Owner FCM on every send (`HE check-in instructions sent`).
| `GET` | `/v1/conversations/search` | Search threads |
| `POST` | `/v1/conversations/batch` / `…/archive` | Batch archive |
| `GET` | **BFF** `/v4/messages?conversation_id=` | Thread body (api `/v3/messages` 404/403/500 on new ids) |
| `POST` | **BFF** `/v1/messages` | `{content, conversation}` (api message routes reject new conversation entities) |
| `GET` | `/v3/messages/config` | Allowed email/link lists |
| `GET` | `/v1/exchanges/{conversationId}/get-exchanges` | Exchange array |
| `PATCH` | `/v1/exchanges/{conversationId}/approve` | Body = that array. **Conversation id, not exchange id** |
| `PATCH` | `/v1/conversations/{id}` | `{accepted:0}` is **not** a stay-request decline (v3 still shows exchange status 0). JSON `false` 200s but does not persist. |
| `PATCH` | `https://bff.homeexchange.com/exchange/{conversationId}/manual-decline` | **WITH-GP pending only.** Body `{isPresetModified:true}` after we sent our own message. Empty body 400 (`isPresetModified` boolean required). Reciprocal → **400 `Invalid exchange type for manual decline`**. `/v1/exchanges/{id}/cancel` is only for **started** stays (`"The exchange is not started yet"`). |
| `PATCH` | `https://bff.homeexchange.com/exchange/{conversationId}/change-to-non-reciprocal/{theirExchangeId}` | **Not a decline.** Drops their home, posts `type_auto` **15** (“transformed into a non-reciprocal”), stay becomes WITH-GP. Do **not** use this to refuse a swap (Nina 2026-08-29). Path param is the **exchange id to delete**. Reciprocal v2 GET often 500s until converted. |
| `PATCH` | `https://bff.homeexchange.com/exchange/{conversationId}/change-to-reciprocal/{theirHomeId}` | Undo a convert. Path param is their **home id** (Nina Berlin `3298786`, Marie Québec `2222089`) — **not** their exchange id (exchange id → 409 already reciprocal). Posts `type_auto` **16**. Resets `stayRequest` to **`NEW` `RECIPROCAL`**. |
| `GET` | `https://bff.homeexchange.com/exchange/v2/{conversationId}` | `{stayRequest:{stayRequestStatus,stayType,stayDrafts[]}, exchanges[]}`. Statuses: `NEW` · `ACCEPTED` · `EXPIRED` · **`MANUALLY_DECLINED`** · `AUTOMATICALLY_DECLINED` · `PAST_DATES_DECLINE`. `stayType`: `WITH-GP` · `RECIPROCAL` · `RECIPROCAL-WITH-GP`. |
| `PATCH` | `/v1/exchanges/{conversationId}/cancel` | Started/finalized stays only. Pending 200 `{"error":"The exchange is not started yet"}`. Host cancel status is **6** (`STATUS_HOST_CANCELED`); **5** is guest cancel. |
| `PATCH` | `/v1/conversations/{id}/archive` | Archive thread (204). `PATCH …/unarchive` restores. Not a decline — exchange stays status 0. |
| `GET` | `/v1/exchanges/user/me?filter=&limit=&offset=` | User exchanges (`filter=all` 400 — use a real filter) |
| `GET` | `/v1/exchanges/restrictions` | `{has_post_expired_subscription_exchange}` |
| `GET` | `/v1/exchanges/approved/ready` | Ready-to-finalize |
| `POST` | `/v1/exchanges/{id}/modify/check` | Date/home/GP change preview |

### Search (BFF)

Listing search is **not** on `api.homeexchange.com`. Use the BFF with search-v2 headers.

| Method | Path | Use |
|---|---|---|
| `POST` | `https://bff.homeexchange.com/search/homes?offset=&limit=` | Destination search. Headers: `X-SEARCH-API-VERSION: v2`, `X-LEGACY-RESPONSE: true`, `X-HE-PAGE-NAME: /search-v2`. Body `{search_query:{…}}` (optional `last_search`) |
| `POST` | `https://bff.homeexchange.com/exchange/v3` | **New stay request.** Body `{stayType,startDate,endDate,homeId,hostId,guestId,guestNumber,content}`. `stayType`: `WITH-GP` \| `RECIPROCAL` \| `RECIPROCAL-WITH-GP`. Also `POST /exchange` (v1, same body). |
| `GET` | `https://bff.homeexchange.com/exchange/config` | `{NB_DAYS_PREAPPROVAL_EXPIRATION, NB_DAYS_TO_AUTO_DECLINE}` |

`search_query` fields that work (2026-08-16):

| Field | Example | Notes |
|---|---|---|
| `location.polygon` | `{location_id:"whosonfirst:borough:421205771", provider:"jawg"}` | **Manhattan** borough. NYC city = `whosonfirst:locality:85977539`. Polygon leaks Brooklyn / Jersey City / Queens — filter results to Manhattan coords (`lat` 40.70–40.88, `lon` −74.02 to −73.94; drop `admin1=New Jersey` and titles with Brooklyn). |
| `location.bounds` | `{sw:{lat,lon}, ne:{lat,lon}}` | Alternate to polygon |
| `calendar.date_ranges` | `[{from:"2026-12-25", to:"2027-01-03"}]` | Stay window (checkout = `to`) |
| `calendar.exchange_types` | `["available","guest-wanted"]` | **Default (points).** `available` = GP or swap those nights; `guest-wanted` = GP-only. Reciprocal-only = `["reciprocal"]`. Only `guest-wanted` drops dual homes. Other strings 422. |
| `home.size.beds` | `{adults:2, children:3, babies:0}` | Guest mix. `guests_nb` also works |
| `home.size.bedrooms` | `3` | Min bedrooms. Use only when the stay needs it. `bedrooms_nb` is ignored. |
| `filters` | `["response-rate-above-threshold"]` | Host response ≥ HE average (~80%). `children-welcome` / `guest-wanted` as **filters** are 422 |
| `home.amenities` | `["children-welcome"]` | Works. `kids-friendly` is 422 |
| `extended` | `true` | Ignores availability — do not use for dated trips |

Response: `{homes, total, bounds, last_search_id}`. Card fields: `id`, `capacity`, `guestpoint_per_night`, `min_nights`, `exchange_count`, `is_verified`, `descriptions[].title`, `user.{id,first_name,response_rate,is_verified}`, `location.{latitude,longitude}`, `translated_admins`. Then `GET /v1/homes/{id}/calendar` to confirm nights (`AVAILABLE` = GP or both, `RECIPROCAL` = swap only — **drop unless he asked**, `NON_RECIPROCAL` = GuestPoints).

Place IDs: Jawg autocomplete `https://api.jawg.io/places/v1/autocomplete` (public token in HE `commons*.js`). **Do not commit the token.** Unknown `--place` uses Nominatim bounds instead.

### Users / account

| Method | Path | Use |
|---|---|---|
| `GET` | `/v1/users/me` | Self + `homes[]`, `verified_only`, `verified_status` (`-1` on verification, `0` not, `1` verified), `verification_pending`, `verification.{phoneIsVerified,emailIsVerified,email[]}`, `homes[].is_verified` / `completion_rate`. No dedicated verification-status route (`GET /v1/users/me/verification` 404). |
| `PATCH` | `/v1/users/{id}` | `{verified_only:true}` and other user fields |
| `GET` | `/v1/users/{id}` | Public-ish profile |
| `GET` | `/v1/notification/headband` | Banner (204 if none) |
| `GET` | `/v1/users/me/alerts` | Saved-search alerts |
| `GET` | `/v1/search/last?version=2` | Recent search history (`query.location`, `calendar.date_ranges`, `home.size.beds`) |
| `GET` | `/v1/settings/mail-subscribe/list` | Email prefs |

### Account verification (Ruby `5703979`)

HE identity + address verification is **UI-only** (cannot be completed via this CLI). Docs: [what is the process](https://help.homeexchange.com/hc/en-us/articles/360000611557-What-is-the-verification-process), [how to verify](https://help.homeexchange.com/hc/en-us/articles/360001061618-How-do-I-verify-my-identity-and-home-address-on-HomeExchange). Upload: [homeexchange.com/user/verification](https://www.homeexchange.com/user/verification). Profile name (first/last): [homeexchange.com/user/edit/5703979](https://www.homeexchange.com/user/edit/5703979) (`user.edit.url`; needs the user id — `/user/edit` 404s).

| Step | Requirement | Ruby status (2026-08-29) |
|---|---|---|
| Listing ≥ 80% | First home complete enough to start | All three Pine homes `completion_rate=100`, `status=5` |
| Phone | SMS code from profile “Confidential information” | `phoneIsVerified=true` (`+16462043958`) |
| Email | Click the verify link | `verification.email[].verified=true` for `ngoc.h.dinh@gmail.com`; wrapper `emailIsVerified` can still be `false` — re-check in UI |
| Government ID | Passport, ID card, or driver’s license of the **account holder** | Pending (`verified_status=-1`, `verification_pending=true`, all `homes[].is_verified=0`) |
| Proof of address | Last **6 months**, name + address match listing **53 Pine Street, Portland, ME** (utility, bank, lease, tax, insurance) | Same pending state |
| Selfie | Face must match the ID | Same pending state |

**Retry:** HE allows **3 re-uploads**. Generic UI fail: “It looks like your documents couldn’t go through for some reason.” After 3, a support ticket is auto-created — [open one here](https://help.homeexchange.com/hc/en-us/requests/new) if the button is gone.

**Do not retry the same packet.** Two likely fails for this account:

1. **Name mismatch.** Profile is **Ruby Dinh**; ID/email is **Ngoc**. HE’s own help: change the profile first/last name to match the ID *before* the next upload (nicknames like Ruby=Ngoc need an explanation to support).
2. **Proof of address is not the listed home.** Must be last **6 months**, **53 Pine Street, Portland, ME**, and the **same legal name as the ID**. A Bellevue / Jerome / LLC bill will fail. Pine is not the primary residence — still need a Pine document (tax, insurance, utility, or deed).

Photo rules: color, all four corners, no glare, both sides of a license, live selfie (not a photo of a photo). Formats: jpg / png / pdf. Camera permission required.

Additional listings only need extra proof of address (ID is once). Instant or email within ~48h. Do **not** send stay requests until `verified_status=1`.

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
# Apt #2 (bathtub + dishwasher + freezer)
python3 $S request PATCH /v1/homes/3285044 --body '{"feature":{"practical":8100,"multimedia":1033,"various":5,"personal":2,"rule":6,"kids":16,"remote":3}}'
# Apt #1B (dishwasher + freezer, no bathtub) + re-apply contact_allowed after publish
python3 $S request PATCH /v1/homes/3285159 --body '{"contact_allowed":0,"prefers_reciprocal":false,"feature":{"practical":7076,"multimedia":1033,"various":5,"personal":2,"rule":6,"kids":16,"remote":3}}'
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
| `dishwasher` | `practical` 4 dishwasher (all three — Apt #2 added on Hospitable/Airbnb 2026-08-15) |
| `freezer` | `practical` 128 freezer (all three — #1B/#2 added on Hospitable/Airbnb 2026-08-15) |
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
| #2 `3285044` | 8100 (dishwasher+microwave+freezer+oven+fridge+bathtub+heating+EV) | 1033 | 5 | 16 | 3 | 6 | 2 |
| #1B `3285159` | 7076 (dishwasher+microwave+freezer+oven+fridge+heating+EV) | 1033 | 5 | 16 | 3 | 6 | 2 |

Required headers (script sets these):

```
Accept: application/json
Accept-Language: en
authorization: Bearer <ssm>
he_web_version: 20.32.0-rc.1
origin: https://www.homeexchange.com
referer: https://www.homeexchange.com/conversations
```

**Never send `Accept-Language: *`.** Node `fetch` (undici, Lambda Node 22) defaults to `*`. HE `GET /v1/homes/me` then 500s `{message:"Invalid \"*\" locale."}` — that was the 2026-08-31 `homeexchange-processor` / DLQ alarm. `he_api.py`, auto-reply `HomeExchangeClient`, and the processor all send `en`.

## Door codes (Schlage)

Same flow as Airbnb / Hospitable, in `addDeleteCodeWiFiPyschlage` (every 5 min):

1. Inbox `GET /v3/conversations/me?limit=50` — keep exchanges on Pine homes with `status` **1** (pre-approved) or **3** (finalized). Skip requested (`0`) and cancelled (`5` / `canceleted_at`).
2. If stay is in the code window (**5:00 America/New_York on check-in day** through checkout day until **11:00**), fetch `GET /v3/conversations/me/{id}` for `guest.phone`. Do **not** program the day before check-in (Michael 2026-08-20: early arrival unlocked while the prior guest was still in).
3. PIN = last 4 of that phone (same NANP ranking as Hospitable). Lock name `{first} - HE CI:MM-DD - CO:MM-DD`.
4. Checkout after 11:00 ET: code is removed with the rest of the desired list.
5. HE guests are **not** passed to `doorCodeMessageMismatchHeal` (no Hospitable check-in message). `code_not_there_text_alert` still expects the HE PIN.

Parse `start_on` / `end_on` as the `YYYY-MM-DD` calendar date. Do **not** `astimezone` UTC midnight into `America/New_York` (that would drop the PIN a day early).

## Calendar sync (AWS)

`jeromevidaao/home-exchange-cal-sync` Lambda `homeexchange-processor` (must send `Accept-Language: en`; retries 429/5xx with 2s/5s/15s; does not redrive DLQ after a processing failure):

- Daily `sync_availability` (`homeexchange-daily-sync` → `homeexchange-sync-trigger` → SQS): Apt **#3** from Airbnb iCal **plus** Hospitable calendar; Apt **#2** and Apt **#1B** from Hospitable `GET /v2/properties/{uuid}/calendar` (SSM `/hospitable/bearer-token`). Hospitable `BLOCKED` nights (manual USER blocks, vendor API blocks) are written to HE as `UNAVAILABLE` for every listing; HE `BOOKED` exchanges are skipped. Then **May 15–Oct 31** (every year; `getSeasonalOverridePeriods`) + holidays `UNAVAILABLE`. Airbnb/Hospitable stay open. **End of every sync:** `restoreListingPrefs` force-PATCHes `contact_allowed:0` + `prefers_reciprocal:false` on all three homes (HE resets these randomly — do not conditional-skip).
- Reservation webhooks on `home-exchange-reservations` SQS: `blockCalendar` for **#1B, #2, or #3** (`HE_HOMES`), then **again** `restoreListingPrefs` (`reason=reservation_block`) so calendar mutations cannot leave `contact_allowed=1` until the next daily sync. Other properties are dropped.

## Pre-approve

**HARD (2026-09-26):** **Never** approve / pre-approve until `cleaningFeeAccepted: true`. Fee-ask first (Katie / Caroline / Jessica). Cancel-after-wrong-approve is **not** recovery.

1. Dates open on **both** Hospitable and `GET /v1/homes/{heHomeId}/calendar` for that unit.
2. Recheck Hospitable calendar + reservations **immediately before** PATCH approve. If nights are no longer open, do not approve.
3. Confirm guest accepted the cleaning fee (`cleaningFeeAccepted` on reservation / DDB). If not, send fee-ask only — do not PATCH approve.
4. `GET /v1/exchanges/{conversationId}/get-exchanges` then `PATCH …/approve` with that array.
5. Hospitable `PUT calendar` `available:false` for `[checkIn, checkOut)`.
6. Guest text: **I just sent you a pre-approval and blocked those dates for you.** Never “you’re booked.”

**Cleaning fee is paid separately — never “included”.** Guests pay us after the stay. Do not say the fee is included in GuestPoints / the exchange / the reservation. Self-clean is never allowed.

**Live Jessica Dec 18–20 Apt #3 $125 (2026-09-26):** fee-ask already sent — **do not re-spam**; leave the thread unless Jerome asks.

**Cancel + extra night (Katie 2026-08-17 Apt #2):** guest cancels the pre-approval, adds a night, resubmits. Check Hospitable for the extra night. Prior nights we already blocked (no Airbnb reservation) are leftover USER/VENDOR blocks — treat as open for this guest. If the extra night is free, say so and pre-approve the new stay + block the full range again. Never ask for an Airbnb alteration. “Just submitted, thank you!” after a cancelled pre-approval is a re-approve turn, not shared “You’re welcome.”

**Cleaning fee — thank once, keep it on the reservation:** Pull the **full** HE thread (**BFF** `GET /v4/messages?conversation_id=` — api `/v3/messages` breaks on new ids) on every auto-reply. Guest yes (Caroline “the cleaning fee is fine” / Katie “We’re completely fine with the cleaning fee!” / Clara “Yes we accept paying $125 cleaning fee”) is stored as `reservation.cleaningFeeAccepted` on the SQS payload and `heReservation.cleaningFeeAccepted` in the harness (also on the DDB pre-approval block). Do **not** thank them for the fee again if a prior host message already said “thanks for confirming … cleaning fee” (the extra-night re-approve must not repeat it). Self-clean ask (Clara “clean the apartment ourselves”) is refused; they still pay the fee separately after the stay.

## Implementation map

| Layer | Location |
|---|---|
| This CLI | `~/.grok/skills/home-exchange/scripts/he_api.py` |
| API HE chat + poll | `~/cleaningbutton-api/index.js` — BFF inbox/messages path shipped (`a7a37a9` era) |
| Auto-reply / approve | `~/auto-reply-sqs-harness/src/clients/HomeExchangeClient.js` — same BFF list/messages/send |
| Calendar sync | `~/home-exchange-cal-sync` (`HE_HOMES`) |
| Token refresh | Lambda `he-token-refresh` |
| Schlage door codes | `~/add-delete-code-wifi-pyschlage` — HE last-4 same window as Airbnb (**5:00 ET on CI day** → CO 11:00 ET). Verifier: `~/code_not_there_text_alert`. |

## Slash

`/home-exchange` → run `he_api.py` for the user’s ask. Destination / dates / “find a stay” → `search` (GuestPoints default). “Contact / request that listing” → `request-stay` only if he picked it **and** `verified_status=1`. Otherwise `homes`. Never echo the bearer.
