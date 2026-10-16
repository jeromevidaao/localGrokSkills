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

**Token refresh (hardened 2026-10-09, repo `home-exchange-cal-sync` `token-refresh/`):** EventBridge `he-token-refresh-proactive` every 15 min; renews from **12h before exp** (`PROACTIVE_WINDOW_MIN=720`), **1 login per run** (2, 45s apart, once < 3h left), validate `/v1/users/me` before overwrite. Failure mode seen 10/8–10/9 and again **2026-10-11 17:32Z → 2026-10-12 02:48Z**: from Lambda IPs Auth0 answers the identifier POST with **400 (bot detection/captcha)** (`identifier blocked kind=captcha`); AWS WAF answers rapid retries with **202 challenge**. The same headless flow from the box works (2026-10-12 box recovery: identifier 200, `/v1/users/me` 200, SSM overwritten, proactive invoke then `noop reason=fresh`). Code stops before posting the password when the identifier step is blocked. Alarms (SNS `homeexchange-alerts`): `he-token-expiring-soon` (min-to-expiry < 180 for 2×15 min = early warning) and `he-token-expired` (< 0). After a box rewrite the alarm stays ALARM until **two** 15-min Minimum datapoints are ≥ 180 — invoke `he-token-refresh` with `{"mode":"proactive"}` so it emits `HETokenMinutesToExpiry` without logging in. Rollback: Lambda version **1** = pre-hardening code. Manual recovery when Lambda keeps getting captcha: run the same `form_login_once` from the box (venv with boto3 + `requests`), validate, write SSM — never print the token.

**Harness (2026-09-30):** `HomeExchangeClient` does this in-process — on HE HTTP 401 it invokes `he-token-refresh` (or an injectable `tokenRefresh` hook), clears the bearer cache, reloads SSM `/homeexchange/bearer-token`, stamps `/homeexchange/last-token-received` (epoch seconds; never the JWT), and retries the same HE call **once**. HE-only paths (approve / send / decline) still fail closed if refresh+retry cannot recover. Mixed occupancy (`loadCurrentGuestsByListing` for early_checkin / lockout / smoke) treats HE `listConversations` as **best-effort**: after client refresh+retry still fails, log and continue with Hospitable/Airbnb guests so an HE outage does not abort Airbnb unit-ready (`occupancy_lookup_failed`). Do not merge `/homeexchange/credentials` into the bearer parameter.

**IAM (2026-09-30, production):** harness role `auto-reply-sqs-role-3i2ozrop` may invoke `he-token-refresh` via resource-based Sid `GuestMessagingHarnessInvokeHeTokenRefresh` (Titan `PutRolePolicy` AccessDenied). Optional out-of-band identity `HeTokenRefreshInvokeAndStamp` for `ssm:PutParameter` on `/homeexchange/last-token-received` (stamp soft-fails without it).

## Pine mapping

| Unit | HE home | Hospitable | Airbnb |
|---|---|---|---|
| Apt **#3** | **`3202475`** | `60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd` | `24259977` |
| Apt **#2** | **`3285044`** (created 2026-08-15) | `114663c5-0709-4eff-a868-fa9ebd6ed42d` | `20150380` |
| Apt **#1B** | **`3285159`** (created 2026-08-15) | `c899481f-2e5b-402d-80c4-3167fd824d96` | `20904545` |

**Names:** Jerome calls Apt #1B **"the studio"** (HE title *Downtown Studio*, sleeps 3 max). `/v1/homes/me` returns exactly these 3 homes. **Public guest booking links** (verified 200, 2026-10-15): [#3](https://www.homeexchange.com/en/holiday-home/3202475), [#2](https://www.homeexchange.com/en/holiday-home/3285044), [studio/#1B](https://www.homeexchange.com/en/holiday-home/3285159). `/homes/edit/{id}` is owner-only; `/home/{id}` and `/en/home/{id}` 404. Never tell Jerome a unit isn't on HE without mapping his nickname first.

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

## Booking guard (2026-10-15)

`home-exchange-cal-sync/booking-guard` Lambdas on role **`homeexchange-lambda-role`**:

| Lambda | Schedule | What |
|---|---|---|
| `pine-booking-sync` | every 15 min | Airbnb nights → HE `RESERVED`; active HE stays → Hospitable block. Writes calendars. |
| `pine-booking-audit` | hourly `:07` | Read-only overlap audit. Never cancels, messages, or changes door codes. |

Metrics are **CloudWatch Embedded Metric Format** in namespace `PineBookingGuard` (log line only). The role has **no** `cloudwatch:PutMetricData` and **no** `sns:Publish`. A direct `put_metric_data` call fails the invoke (`pine-booking-audit-errors`, 2026-10-15 20:30Z). Direct SNS to `homeexchange-alerts` logs `sns_direct_publish_failed` and is swallowed; the metric alarms on that topic still page once EMF lands. Titan **cannot** `iam:PutRolePolicy` on this role — an admin must attach the inline policy if direct PutMetricData / SNS publish is wanted:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PineBookingGuardPutMetricData",
      "Effect": "Allow",
      "Action": "cloudwatch:PutMetricData",
      "Resource": "*",
      "Condition": {"StringEquals": {"cloudwatch:namespace": "PineBookingGuard"}}
    },
    {
      "Sid": "PineBookingGuardSnsPublish",
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:834917996497:homeexchange-alerts"
    }
  ]
}
```

Attach as inline policy `PineBookingGuardMetrics` on `homeexchange-lambda-role`. Rollback of the EMF deploy: Lambda version **2** (PutMetricData code, sha `2Jpcq/KEixDwexlHx0pxmcKW3lo0Hveg/3TnplbA/S8=`). EMF package is version **3** on both functions (sha `e/EgkVOoAGb0C0CVf6SPBACnIL/jGMgW2bnHFjz+QlE=`).

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

## Permanent booking-safety rules (Jerome, 2026-10-15)

1. **HE↔Airbnb sync is two-way and fails closed.** `pine-booking-sync` (every 15 min) blocks Airbnb nights on HE and active HE stays on Airbnb/Hospitable, reads every write back, and on any read/write failure blocks the dates on both sides rather than leaving them open. Any skipped, unconfirmed or partial block alarms (SNS `homeexchange-alerts` → ansia@mail.grokbot.com; DLQ `pine-booking-guard-dlq`). `pine-booking-audit` (hourly) is the independent overlap check.
2. **Never send a door code or check-in instructions to a stay that overlaps another booking.** The harness HE check-in sender (`src/useCases/heCheckinOverlapGuard.js`) calls `pine-booking-audit` before building the message and holds + alarms on: an unresolved overlap for that conversation, a manual hold (`DEFAULT_HE_CHECKIN_HOLD_CONVS` / env `HE_CHECKIN_HOLD_CONVS`), or missing/erroring audit data (fail closed). The cleaningbutton-api scheduler hold is `checkinInstructionsQueuedAt = "HOLD:..."` on the conversation in DynamoDB `homeexchangeMessageState` pk=`cursor` (do not run the poll with `force=1` while a hold is set). Remove a hold only after Jerome confirms the overlap is resolved.
3. **Every change ships with a test plus a live readback on both platforms** (HE calendar and Airbnb/Hospitable calendar, or the live Lambda result), and keeps a published Lambda version for rollback.

Skills hold SSM path names only (e.g. `/homeexchange/bearer-token`), never secret values.

## 2026-10-15 — double-booking incident (lessons)
- **Root cause:** HE→Airbnb block silently skipped nights Airbnb had already sold (no alert), and there was no Airbnb→HE sync. Fixed: two-way fail-closed `pine-booking-sync` + hourly `pine-booking-audit` (code `/tmp/hecs/booking-guard`, `infra.sh`), **540-day horizon** (fail-closed fallback must match), daily 8:17am PT Grok Bot cross-check, alarms → SNS `homeexchange-alerts`. Double booking is Jerome's worst case.
- **Resolution:** HE stays host-cancelled 2:05pm PT: Clara & Mathis (conv 95472973, Apt #3, Oct 19) and Katie (conv 95201321, Apt #2, Oct 29–Nov 3). Airbnb guests kept (Raz HMZZ9QXJC8, Hayley HM99TP4XKH). Host-cancel cost: GuestPoints refunded, guest may review, repeat cancels risk the account, HE may reimburse guest up to $120/night.
- **Katie follow-up:** offered the studio (3285159) Oct 29–Nov 3; studio HE calendar opened NON_RECIPROCAL Oct 29–Nov 5 so she can request; Airbnb side stays held, and sync must not re-block those nights. HE auto-reply sent her an unapproved, confusing message at 2:21pm PT (msg 1003802226) — stop auto-replies on threads Jerome is handling manually.

## Booking guard / first-stay ops (2026-10-15, end of day)

**Units** (mapping in `home-exchange-cal-sync/booking-guard/guard_core.py`): Apt #3 = HE `3202475`; Apt #2 = HE `3285044`; Studio/Apt 1B = HE `3285159`, Hospitable `c899481f-2e5b-402d-80c4-3167fd824d96`, Airbnb `20904545`.

**System** (repo `home-exchange-cal-sync`, `booking-guard/`, deploy `bash booking-guard/infra.sh`):
- `pine-booking-sync` every 15 min, two-way: Airbnb nights → HE `RESERVED`; requested/pre-approved/finalized HE stays → Hospitable block noted `HomeExchange <guest> conv <id>`. Read-back verify, capped backoff retries, DLQ `pine-booking-guard-dlq`, fail closed over the 540-day horizon.
- `pine-booking-audit` separate hourly Lambda at `:07`.
- Alarms → SNS `homeexchange-alerts` (ansia@mail.grokbot.com): sync-failure/heartbeat/errors, audit-conflict/unblocked/heartbeat/errors, dlq-depth. Audit alarm settings live in `infra.sh` (Period 900, 1/1, TreatMissingData ignore) — never hand-edit; a redeploy reverts.
- Manual holds with a note starting `Hold for` or `MANUAL` are never released by sync.
- Dated open-exceptions: SSM `/homeexchange/open-exceptions`, shared by the guard and `homeexchange-processor` (nightly 11 PM PT sync; skips HE-booked nights).

**Guards:**
- Harness HE reply gate: holds + alarms on muted convs (`DEFAULT_HE_MUTED_CONVS` / `HE_MUTED_CONVS`), cancelled exchange (status 6), overlap, unreadable conv, or audit error.
- Check-in overlap guard: `heCheckinOverlapGuard.js`.
- PIN guard in `addDeleteCodeWiFiPyschlage`: fail closed; held codes never deleted; dry run `he_pin_guard_dry_run` with `listUpcoming`.
- Harness + PIN roles have `lambda:InvokeFunction` on `pine-booking-audit` (harness role ARN includes `service-role/`).
- Cancelled stays never get instructions or PINs. DDB `homeexchangeMessageState` marker: `checkinInstructionsQueuedAt`.

**Root-cause lessons:**
- Hospitable block calls return 202 — always read back. Clara/Katie blocks were later reopened by an unknown API writer and nothing re-checked.
- Old inbox call ignores paging: use the newer list or paginate with `first`/`after`; fail closed if incomplete.
- PIN loader missed newer convs (e.g. `1000923027`) on the older conversation list.
- Harness availability counted our own `Hold for <guest>` as unavailable and auto-declined that guest's re-request — a hold must count as open for the same guest.
- Auto-replies must not fire on cancelled exchanges.

**Rules:** two-way sync, fail closed, alarm on any skipped/partial block. Never send door codes/instructions to an overlapping stay. Every change = test + live read-back on both platforms. Guest messages need Jerome's direct OK in the owning bot's chat. Never auto-approve an overlapping HE request.

**First-stay ops:** first HE stay = Katie McGovern, Studio, conv `1000923027`, exchange `129847475`, Oct 29–Nov 3 2026. Daily 9 AM PT routine `katie-studio-stay-daily-watch` checks booking, overlap, alarms, instructions, PIN load/removal. Use it as the template for future first stays.


## HE guest phone for door codes (2026-10-15, Jerome approved 3:03 PM PT)

**Problem:** Newer BFF-only conversations (ids ≥ ~1e9, e.g. Katie `1000923027`) 404 on `GET api…/v3/conversations/me/{id}`. BFF `exchange/v2` and `v4/conversations` return guest with only `id` + `first_name` — **no phone**. Old v3 detail still has `guest.phone`.

**Primary source (works for BFF-only + finalized stays):**
`GET https://api.homeexchange.com/v1/exchanges/{conversationId}/get-exchanges`
→ use `additional_informations.phone` when `additional_informations.is == "guest"`.
(The nested `guest` object on that payload still omits phone.) Phone appears at/after finalization, not N days before arrival.

**Fallback:** same guest id’s phone from another of their v3 conversation details (Katie: `95201321`).

**Fail closed:** no resolvable phone → no PIN load, no check-in send.

**Never** ask the guest for their phone. **Never** log/print phone numbers (report `last4 present: yes/no` + `phoneSource` only).

**7-day private alert:** `addDeleteCodeWiFiPyschlage` on each sync runs `he_check_missing_phones_upcoming` — confirmed Pine HE stay with check-in ≤7 days and no phone → SNS `homeexchange-alerts` only, deduped in DynamoDB `homeexchangeMessageState` pk `he_missing_phone#{conv}#{check_in}#{day}`. No guest message / no draft.

**Shipped:**
- PIN Lambda `addDeleteCodeWiFiPyschlage` commit `0186c1e`, published version **7** (rollback: version **6** / prior sha `b83980b`).
- Harness `guest-messaging-agent-harness` commit `2fdbf64`, published version **8** (rollback: version **7** / prior sha `d4d8440`).
- Dry-run proof (2026-10-15): `he_pin_guard_dry_run` today=`2026-10-29` listUpcoming → Katie conv `1000923027` `phoneSource=get-exchanges` `last4Present=yes` `pinResolves=true`. Live harness `resolveGuestPhoneLast4` same source/result. No PIN load, no guest message.

## HE day boundary is Europe/Paris (lesson 2026-10-15, booking-guard 6535fd8)
- HE's calendar GET drops nights before HE's "today" in Europe/Paris, and they can't be written. Around 3 PM PT (midnight Paris) the PT-current night disappears. Before the fix, the read-back reported "nights still open on HE: [today]" and `pine-booking-sync-failure` fired falsely (Oct 15, 4:42 PM PT).
- Rule: `sync_handler._write_he` skips any night earlier than `he_today()` (Paris date). It logs `he_past_night_skipped` as a warning only, with no failure metric. Every night from the Paris date onward is still written, read back, and fail-closed.
- Tests pin the cutoff to the injected `today`. Check with `C.he_night_map(IO.he_calendar(home))`: the earliest key is the Paris date.

## Booking-guard fire drill (booking-guard 5595a86, tested 2026-10-15)
- `aws lambda invoke --function-name pine-booking-audit --payload '{"drill":"conflict"}' out.json` (or `"unblocked"`). It adds a fake in-memory HE stay (conv DRILL) on a real Airbnb night, or on an open night. Nothing is written and the dedupe state isn't touched. The SNS subject starts with "DRILL".
- `aws lambda invoke --function-name pine-booking-sync --payload '{"drill":"failure"}' out.json` forces SyncFailures=1 plus a DRILL SNS. It reads and writes nothing, and nothing goes to the DLQ. Unknown drill values raise an error.
- Heartbeat: `aws cloudwatch set-alarm-state --alarm-name pine-booking-{sync,audit}-heartbeat --state-value ALARM --state-reason "DRILL: ..."`. It returns to OK on the next evaluation.
- NEVER put DRILL in AlarmDescription (persistent config). DRILL tags belong only in drill payloads and set-alarm-state reasons. If config drifts, re-run infra.sh.
- Cleanup: the conflict/unblocked/failure alarms are Maximum over 900s, so wait for the next 15-min bucket, run a normal audit and sync, then confirm all 8 alarms are OK and the DLQ is 0.

## HE auto-reply global kill switch (pause / resume) — added 2026-10-16
Jerome 2026-10-16 09:40 PT: "Pause all HE auto reply for now." **Currently PAUSED. Do not resume until Jerome says so in chat.**
- Switch: SSM `/homeexchange/autoreply-paused` (String, us-east-1) **and** Lambda env `HE_AUTOREPLY_PAUSED` on `guest-messaging-agent-harness`. Paused if env is `true` OR SSM is anything but `false`. SSM missing/unreadable = paused (fail closed).
- Enforced in `HomeExchangeClient.sendMessage / approveConversation / declineConversation` (harness 82cb8ec), so it covers every automated HE write: auto-replies, reply-gate sends, HE check-in instructions (homeExchangeCheckin.js, same path, so held), pre-approve/approve/decline auto-actions, early-checkin / ring-smoke / keypad-lockout HE notices. Hospitable/Airbnb sends are NOT affected.
- Held sends log `[he_autoreply_paused]` once per conv+op per container, no SNS.
- Not touched: pine-booking-sync, pine-booking-audit, alarms, PIN loading (addDeleteCodeWiFiPyschlage), homeexchange-processor (calendar POSTs only, never messages).
- Stopgap also applied 09:41 PT: env `HE_MUTED_CONVS` = all ~143 known Pine HE conv ids. Pre-pause env saved at /workspace/harness-env-before-pause-20261016.json (had no HE_MUTED_CONVS). Rollback code version: published version 9 (= 2fdbf64).
- Probe (read-only, never sends): `aws lambda invoke --function-name guest-messaging-agent-harness --region us-east-1 --cli-binary-format raw-in-base64-out --payload '{"he_autoreply_pause_probe":true,"conversationId":"1000923027"}' /tmp/p.json && cat /tmp/p.json`
- **Pause:** `aws ssm put-parameter --region us-east-1 --name /homeexchange/autoreply-paused --type String --value true --overwrite` (instant, next send).
- **Resume (only on Jerome's explicit OK):**
  1. `aws ssm put-parameter --region us-east-1 --name /homeexchange/autoreply-paused --type String --value false --overwrite`
  2. Restore env from the backup (removes HE_AUTOREPLY_PAUSED and the stopgap HE_MUTED_CONVS): `python3 -c "import json;print(json.dumps({'Variables':json.load(open('/workspace/harness-env-before-pause-20261016.json'))['Environment']['Variables']}))" > /tmp/env.json && aws lambda update-function-configuration --function-name guest-messaging-agent-harness --region us-east-1 --environment file:///tmp/env.json` (re-read current env first in case other vars changed since).
  3. Run the probe; expect `wouldSend:true`.
  - **IAM gap (2026-10-16):** role auto-reply-sqs-role-3i2ozrop gets AccessDenied on ssm:GetParameter for /homeexchange/autoreply-paused, so SSM reads fail closed (= paused). Before resume, Jerome must add ssm:GetParameter on arn:aws:ssm:us-east-1:834917996497:parameter/homeexchange/autoreply-paused to that role (grok-bot-titan has no IAM rights).
  - Note: messages held while paused are not auto-resent; check-in instructions whose window passed need a manual look (Katie 1000923027 due ~Oct 26).

## HE approval mode (run every HE send by Jerome first) — added 2026-10-16 10:12 PT
Jerome: "instead of pausing, run them by me here for approval prior sending". Code: auto-reply-sqs-harness `21a1fa4`, `3360bc8`, `20c4ebb`, `c54fcf2` (src/useCases/heApprovalMode.js).
- **On when** the kill switch is on (env `HE_AUTOREPLY_PAUSED=true` on guest-messaging-agent-harness; keep it true). Drafts are generated as normal (classify, draft, reviewer/judge, shared categories, check-in template). Every HE write (`sendMessage`, `approveConversation`, `declineConversation`) is intercepted by a client Proxy: it stores a pending item and publishes ONE SNS to `homeexchange-alerts`, then throws `he_pending_approval:<op>:<conv>:<approvalId>` (terminal, no SQS retry, no FCM "send failed"). Nothing posts. The real client still asserts the pause too (double guard).
- **Covers** guest replies, check-in instructions (kind `checkin_instructions`), pre-approve and decline (described as the proposed action). NOT covered (still just held by the pause, no approval card): ring-smoke / keypad-lockout / early-check-in notices.
- **Gates still apply** before drafting: cancelled exchange, overlap (pine-booking-audit), unreadable thread. In approval mode a conversation mute does NOT skip draft generation. The 143-conv `HE_MUTED_CONVS` stopgap was removed 10:35 PT (backup: /workspace/harness-env-backup-before-unmute-20261016.json).
- **Store:** role auto-reply-sqs-role-3i2ozrop has NO access to homeexchangeMessageState (AccessDenied on Put/Get/Update/Delete), so env `HE_APPROVAL_TABLE=airbnb-harness-dedup`, `HE_APPROVAL_KEY_ATTR=webhookId`, key `he_pending#<approvalId>` (no ttl attr, so it persists). Role has only Put+Get there, so status changes are conditional full-item Puts. Fields: status (pending/sending/sent/send_failed), op, kind, conversationId, text (exact), actionArgs, guestName, unit, checkIn, checkOut, guestMessage, createdAt, proof. If Jerome grants the role Put/Get on homeexchangeMessageState, just drop the two env vars.
- **Dedupe:** approvalId = `he` + sha256(conv|op|normalized guest message|discriminator)[0:12]. Same guest message → same id → no 2nd row or email (log `deduped:true`). Check-in uses discriminator `checkin:<checkIn>`.
- **APPROVAL email** (to ansia@mail.grokbot.com, SNS JSON envelope; read the `Message` field):
  Subject `APPROVAL: HE reply for <first name> (conv <id>)`. Body: Approval id, Conversation, Guest, Unit, Stay `<in> to <out>`, Kind, Proposed action, Guest's latest message, the exact proposed reply between `-----` lines (or the action args), and the send command. Relay it to Jerome in chat verbatim (proposed text exact) and wait for his explicit OK. These are NOT alarms: the alarm responder must not treat them as incidents.
- **Send an approved draft (only after Jerome says yes to that specific draft):**
  `echo '{"he_send_approved":"<approvalId>"}' > /tmp/sa.json && aws lambda invoke --region us-east-1 --function-name guest-messaging-agent-harness --payload fileb:///tmp/sa.json /tmp/sa-out.json && cat /tmp/sa-out.json`
  It re-runs the cancel/overlap gate, claims pending→sending (concurrent invokes post once), posts exactly the stored text with `heApproved` (bypasses only the pause), marks `sent`+`sentAt`. Refuses: `bad_approval_id`, `not_found`, `status_sent`/`status_send_failed`/`already_claimed`, `gate:<reason>` (e.g. cancelled), `proof_item_never_sendable`. A failed post becomes `send_failed` and is never retried automatically (check the thread before doing anything by hand). If Jerome edits the text, post his version manually instead; never edit the stored row to send.
- **Stale caution:** only approve drafts for fresh messages. A replay of an old message can produce a wrong action (e.g. replaying Katie's 10-15 "submitting as discussed" proposed DECLINING her confirmed stay because her own block makes the dates look closed).
- **Proof / test replay:** add top-level `"he_approval_proof": true` to an SQS-shaped replay event (only works in approval mode). Skips the already-on-thread check so an answered message still yields a draft; the item is `proof:true`, the email starts "TEST / PROOF ONLY", and send-approved always refuses it. Proof 10-16 10:33 PT: Catherine conv 95940761 → `heea1dad10bc95`, text "You're welcome, Catherine!", replay again → deduped. Payload: test-payloads/he-95940761-approval-replay.json.
- **Store probe:** `{"he_approval_store_probe":true}` writes/deletes a probe row per candidate table and reports put/get/update/delete (delete is denied on the dedup table, so remove `he_pending#probe-*` rows with your own creds afterwards).
- **Versions / rollback:** v10 = pre-approval-mode (cce9aae kill switch only, old env with mutes); v11 = approval mode c54fcf2. Code rollback: redeploy cce9aae or `git revert` the 4 commits; env rollback: restore /workspace/harness-env-backup-before-approval-env-20261016.json (has the 143 mutes, no approval vars).
- **Resume full auto later:** needs Jerome's OK, the SSM read permission (see kill switch section), then set HE_AUTOREPLY_PAUSED=false and SSM false.

## Own-guest holds never make a guest's own dates "not open" — added 2026-10-16 10:54 PT
Bug: Katie (HE guest id 4052575) was auto-declined on her re-request 1000923027 (10-15 2:36 PM PT) and a replay proposed declining her finalized stay, because Apt 1B nights carried "Hold for Katie McGovern HE conv 95201321" (her old conv) and HE showed them RESERVED for her own exchange. Fix: auto-reply-sqs-harness `dafa8a4` (src/useCases/heOwnGuestBlocks.js), Lambda v12 (rollback v11).
- Hospitable/Airbnb calendar block whose note names any of this guest's ids counts as OPEN for that guest only. Ids = current conv, every exchange id on it, the HE guest user id, plus every other inbox conv (listConversations limit 50) whose exchanges/interlocutor have the same guest id, and their exchange ids. Only digit runs of 5+ are compared; name alone never matches. Covers "HomeExchange <guest> conv <id>", "Hold for <guest> HE conv <id>", "MANUAL hold for <guest> HE conv <id>". Reasons show `ownGuestHold: true`.
- HE calendar RESERVED nights of the guest's own status 1/3 exchange count open (passed as leftoverNights to analyzeHeCalendarOpen).
- Still unavailable: real Airbnb reservations (Hospitable reservations list) and any other guest's hold.
- Hard guard: no decline for a conversation with a pre-approved (1) or finalized (3) exchange: shouldDeclineHeRequest returns false, HomeExchangeClient.declineConversation throws `he_decline_refused_active_exchange` (fails closed if unreadable), and the approval-mode wrapper refuses before storing/emailing a decline.
- Proof 10-16 11:04 PT: Katie 10-15 message replayed (proof=true) → calendar open (all 5 nights ownGuestHold), no decline, pending proof draft `he4696d8fdbc6a` (never sendable). Residual: for a finalized stay the draft still re-asks the cleaning fee ($80) — first-message flow isn't skipped for an already-finalized exchange; don't approve such drafts.
