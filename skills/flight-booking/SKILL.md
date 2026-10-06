---
name: flight-booking
description: >
  Use this whenever searching, comparing, holding, or booking flights for Jerome
  Lionel Ansia (Alaska, Southwest, Delta, Chase Ultimate Rewards, Google Flights),
  or after any flight purchase when calendar / FF / TSA steps are needed. Also
  refine this skill after every completed booking.
---

# Flight booking (Jerome Lionel Ansia)

This is the standing playbook for the **Flight Booking** bot. **Before any
flight search, hold, book, claim, check-in, or change:** read this skill in full
(and any related skills below). On every Jerome message: **Titan retrieve first**,
then **read this skill**. Pull TSA / frequent-flyer numbers from the **DINH ANSIA
PERSONAL WIKI** sheet. After every completed booking (or any correction Jerome
gives), **update this skill**, **append the turn to Titan**, and **commit + push
immediately** — keep improving it.

Related: `r2-memory` (Titan retrieve/append), `always-push`,
`santa-clara-stay-from-alaska-flights` (calendar week blocks), `family-travel`
(SEA–HNL family trips — different party), **`efgs`** (Julie Saturday class
conflicts — ping on out-of-WA trips).

## Hard rules (never skip)

1. **Read skills before any booking work:** before searching, holding, booking,
   claiming a PNR, checking in, or changing a flight, **Read this `SKILL.md` first**
   (and related skills as needed: `r2-memory`, `always-push`,
   `santa-clara-stay-from-alaska-flights`, `family-travel`, `efgs`). Do not rely on
   memory alone for hard rules (name, TSA Pre, purchase gate, Southwest RR, etc.).
2. **Legal name (every airline, every channel):** passenger is always
   **Jerome Lionel Ansia** (first / middle / last) — Alaska, Southwest, Delta,
   Chase Travel, Google Flights handoffs, agency PNRs, and any other booker.
   Never omit **Lionel**. Prefer forms that accept full middle name; if only middle
   initial is allowed, use **L**. Fix typos like JEEROME if prefilled. After booking
   or claiming a trip, **verify the confirmation shows Lionel** (or **L**); if it
   does not and the site allows name edit, fix it before saying done.
3. **TSA Pre / KTN (every airline, every channel):** always enter Known Traveler
   Number **992626698** (TSA PreCheck) on passenger forms — Alaska, Southwest,
   Delta, Chase Travel, agency PNRs, and any other booker. Never leave blank.
   Confirm against the DINH ANSIA PERSONAL WIKI sheet when filling. After booking
   or claiming a trip, **verify TSA Pre / KTN is on the reservation**; if missing
   and editable, add it before saying done.
4. **Purchase gate:** stop at Review & pay / payment. Get Jerome’s **explicit OK**
   in chat before charging. Do not auto-book even under an old price threshold.
5. **Alaska login:** on alaskaair.com always sign in as Atmos **325534370**
   (Jerome Ansia) before search/book — never guest if login is available.
6. **Contact email:** always fill **jerome.ans@gmail.com** on passenger / contact /
   receipt fields. Never leave blank or use a different address.
7. **Billing address:** always fill the full home/billing address on payment forms:
   **3099 125th Ave NE, Bellevue, WA 98005** (street, city, state, ZIP). Never skip.
8. **Seats:**
   - **Alone:** skip paid/optional seat selection — he does not care.
   - **With others:** pick seats for the party when all of these are true:
     (a) seats are **next to each other**, (b) **away from the bathroom/lavatory**,
     and (c) **no additional seat fee**. If any of those cannot be met for free,
     stop and let **Jerome pick** (hand the box). Never pay for seats without OK.
9. **Wiki before FF/TSA fields:** before filling Known Traveler / frequent-flyer
   numbers, open the **DINH ANSIA PERSONAL WIKI** Google Sheet and use the values
   there (do not invent or reuse stale guesses). Sheet:
   https://docs.google.com/spreadsheets/d/1agABcM6hBCmzPXXy3o2D8XtJClu34paWT358l56KzUo/edit
   Drive file id: `1agABcM6hBCmzPXXy3o2D8XtJClu34paWT358l56KzUo`
10. **Always commit + push this skill:** any edit to `skills/flight-booking/` (or
   related flight playbook) must be committed and pushed to
   `jeromevidaao/localGrokSkills` **immediately** — never leave skill changes only
   on disk. Follow **always-push** (public → `git push` `main` → CI green → private).
   Do not ask “want me to push?”.
11. **Refine after book:** when a booking finishes (or Jerome corrects a field),
   update this `SKILL.md` with the learning, then commit + push (rule 5), and
   mirror durable facts into agent memory.
12. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
   **retrieve first**, then **append/update after the turn** so Titan stays current.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook: skill `r2-memory`.
13. **EFGS / Julie class conflict:** if the trip puts anyone **outside Washington
   state** (destination or overnight not in WA — includes SEA↔SJC), **ping the
   EFGS agent** (`00e87ed1-d005-4527-b29b-bfe7cccb59c2`) via SendToAgent with
   route, dates, travelers, and conf code **before** saying the booking is done.
   Prefer also flagging when presenting options if a Saturday conflict is clear.
   EFGS owns the warning to Jerome. In-WA-only itineraries: no ping. Skill: `efgs`.
14. **Flight calendar guests:** on every timed flight-duration calendar event,
   invite **ngoc.h.dinh@gmail.com** and **jansia@nvidia.com** (on top of Jerome).
   Do this for every future booking. Santa Clara all-day week blocks stay
   Ngoc (+ Jerome) unless he says otherwise.
15. **Passwords / site logins (SSM only):** every airline or site login Jerome
   stores for bots lives in **AWS SSM SecureString** in **us-east-1** (IAM
   `grok-bot-titan`). **Fetch at use only.** Never ask him to paste a password
   in chat. Never write secret values to disk, git, chat, memory, Titan, or
   screenshots — keep only path names in this skill. If a needed path is
   missing, **say which path and stop**. Known airline prefixes:
   `/southwest/`, `/delta/`, `/american-airlines/`.


## Family passengers (Hawaii / multi-pax)

When booking for Ngoc and/or Julie (companion fare, family trips), always use:

| | Ngoc (wife) | Julie (daughter) |
|---|---|---|
| Full legal name | **Ngoc Hong Dinh** (GE card: NGOC HONG / DINH) | **Julie M Ansia** (GE card: JULIE M / ANSIA; middle is letter M only) |
| DOB | **March 20, 1988** | **December 3, 2019** |
| Gender | **Female** | **Female** |
| TSA Pre / KTN | **156430198** | **160219687** |
| AA AAdvantage | **630DYM2** | — |
| Delta SkyMiles | **9354872468** | — |
| United MileagePlus | — | **OKF01935** |
| Contact email | ngoc.h.dinh@gmail.com | (use Jerome/Ngoc contact as required) |

Never omit these when they are on the reservation. Prefer wiki sheet values if they ever conflict; update this table after wiki changes.

## Titan R2Memory (every turn)

Scripts live at `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`).

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing prefs / past flight decisions. Also read this
`flight-booking` skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

Optional gate:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_gate.py "<user message>"
```

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Do this for every meaningful flight turn (search, book, correction, preference).
Keep the git skill updated and pushed as well (rule 5).

After adding or editing this skill, refresh the Titan catalog:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_index_catalog.py
```

## Source of truth — DINH ANSIA PERSONAL WIKI

Canonical TSA Pre / KTN, airline loyalty numbers, and other traveler IDs live in:

[DINH ANSIA PERSONAL WIKI](https://docs.google.com/spreadsheets/d/1agABcM6hBCmzPXXy3o2D8XtJClu34paWT358l56KzUo/edit)

Before every booking that needs TSA or FF:

1. Read that sheet via Google Drive (`read_file_content` / search title
   `DINH ANSIA PERSONAL WIKI`).
2. Fill the airline form from the sheet.
3. If the sheet disagrees with cached memory, **prefer the sheet**, then update
   this skill + memory and push.

The table below is a convenience cache only — verify against the wiki when booking.

## Traveler profile (fill every time)

| Field | Value |
|---|---|
| Full name | Jerome Lionel Ansia |
| DOB | Jun 24, 1985 |
| Gender | Male |
| Email (always fill) | jerome.ans@gmail.com |
| Phone | +1 646-204-3958 |
| Billing / home address (always fill) | 3099 125th Ave NE, Bellevue, WA 98005 |
| TSA Pre / KTN | 992626698 (United States) |
| Atmos Rewards | 325534370 |
| AA AAdvantage (oneworld) | 00T5FH4 |
| Delta SkyMiles | 9214639644 |
| Wife (calendar) | Ngoc Dinh — ngoc.h.dinh@gmail.com |
| Work calendar (flight legs) | jansia@nvidia.com — invite on every timed flight event |

Loyalty defaults when the airline allows a partner:

- **Alaska:** **always** select American Airlines and enter **AA 00T5FH4** when the
  loyalty program dropdown allows it (Jerome’s standing choice). Only use Atmos
  **325534370** if AA cannot be selected. Also always enter TSA Pre **992626698**.
  Note: Saver / some one-ways may lock Atmos and block self-serve FF edits — tell
  Jerome (call Alaska or add at check-in).
- **Delta:** SkyMiles 9214639644.
- **Southwest:** Always Rapid Rewards **20346160763** (SSM `/southwest/*`); never guest if login works. Atmos does not apply.

## Default work-week pattern (SEA ↔ SJC)

Typical week: **nonstop** preferred.

| Leg | Preferred window |
|---|---|
| Outbound (usually Mon) SEA→SJC | Depart **~7:00–7:30am** (nearby morning OK) |
| Return (usually Fri) SJC→SEA | Depart **3:00–5:00pm** inclusive (not after 5pm) |

1. Prefer **Alaska** signed in; also compare Google Flights / Southwest / Chase
   points when useful. Separate tickets are fine if cheaper.
2. Filter to nonstops in those windows first; if Alaska has no return in 3–5pm,
   say so and show the closest earlier/later Alaska nonstop + cheaper alts.
3. Saver / Basic is OK when Jerome chooses price over flexibility.
4. Hold or stage to Review & pay; wait for explicit OK; then pay.
5. After purchase, run **Post-booking checklist** below.

## Seats

| Party | Action |
|---|---|
| Jerome alone | Skip seat selection / leave random assignment |
| Jerome + anyone else | Auto-pick **adjacent** seats **away from lavatory** only if **$0** seat fee; otherwise pause and let Jerome choose |

Never add paid seat upgrades without his explicit OK.

## Post-booking checklist (every flight)


Do all of these before saying done:

1. Capture **confirmation code**, ticket/e-ticket if shown, fare paid, flight numbers,
   times, cabin/fare type.
2. **Calendar — timed flight event** for each booked leg:
   - Title like `Flight to San Jose (AS 1341)` / `Flight to Seattle (WN 698)`
   - Correct local times; note conf + fare in description
   - Invite **ngoc.h.dinh@gmail.com** and **jansia@nvidia.com** (and Jerome accepted)
   - If Gmail auto-created a `FROM_GMAIL` event, still create/invite Ngoc on a
     proper event when the Gmail one won’t accept guests
3. **Calendar — Santa Clara week** when the trip is Jerome’s SJC work week
   (Mon arrive SJC / Fri depart SJC, any carrier mix):
   - Title exactly: `Jerome in Santa Clara, CA`
   - All-day, **free** / transparent, location `Santa Clara, CA`
   - Span Mon through Fri (Google exclusive end = Saturday)
   - Invite `jerome.ans@gmail.com` + `ngoc.h.dinh@gmail.com`
   - Skip if an identical block already covers that range
4. Claim / verify trip in the airline account when possible (Alaska Trips, etc.).
5. Attach FF + TSA Pre if still missing; report if locked.
6. Hand the box for captcha / card / 2FA when needed (`request_box_help`); never ask
   Jerome to paste card numbers in chat.
7. Update this skill + memory with anything new he corrected.
8. **Ping EFGS** when the trip is **outside Washington** (see hard rule 11):
   SendToAgent → EFGS id `00e87ed1-d005-4527-b29b-bfe7cccb59c2` with dates,
   airports, who travels, and whether Saturday morning PT is spent outside WA.
   Do not skip for SJC work weeks — Julie’s Bertschi class is Sat 9:15–12:15.

## Airline / site notes

### Alaska (alaskaair.com)

**Checkout must (every Alaska booking):**
1. Signed in as Jerome Ansia / Atmos **325534370** (never guest)
2. Legal name **Jerome Lionel Ansia** (full middle name Lionel)
3. Loyalty: **American Airlines / AA 00T5FH4** when choosable
4. TSA Pre / KTN **992626698**
5. Email + billing address from traveler profile
6. Stop at Review & pay for Jerome’s OK

- Sign in first (Atmos). Sessions and fare holds expire (~10 min) — restage if stale.
- Sticky Continue / Skip seats buttons can be inert in DOM; use reliable click
  paths (browserUse first; computerUse if needed).
- Prefer saved Atmos card when paying as Jerome; still wait for OK before pay. If billing address is required, use **3099 125th Ave NE, Bellevue, WA 98005**; contact email **jerome.ans@gmail.com**.
- After book: Trips list, calendar, FF/TSA.

### Southwest (southwest.com)

- **Always sign in** with Rapid Rewards **20346160763** before search/book/claim (never guest if login is available).
- Credentials (SecureString SSM, fetch at use — never paste into chat):
  - `/southwest/username` (same as RR #)
  - `/southwest/password`
  - `/southwest/rapid-rewards-number`
- Fill full name **Jerome Lionel Ansia**, DOB, gender, email **jerome.ans@gmail.com**, phone, KTN **992626698**, Rapid Rewards **20346160763**, and billing **3099 125th Ave NE, Bellevue, WA 98005** when asked.
- After any Southwest booking (direct or Chase): **Add / retrieve the confirmation** into the Rapid Rewards account so miles credit.
- Seats: skip when solo; with others auto-pick adjacent + away from lavatory only if free, else Jerome picks. Stop for card if no saved method / Apple Pay; still wait for Jerome’s OK before pay.
- Calendar + Santa Clara week still apply for SJC work returns.

### Chase Ultimate Rewards

- Search/book in points when Jerome asks; report points + cash equivalent.
- Traveler must show **JEROME LIONEL ANSIA** / **JEROME L ANSIA**, not JEEROME.
- After book: still add calendar events and claim airline PNRs when given.

### Delta

- Captcha / login often fails — hand box for login after SSM fill; use SkyMiles + KTN.
- Credentials (SecureString SSM, fetch at use — never paste into chat):
  - `/delta/username`
  - `/delta/password`
  - `/delta/skymiles` (9214639644)
  - `/delta/email` (jerome.ans@gmail.com)
- Prefer nonstop when comparing against Alaska/Southwest.

### American Airlines (aa.com)

- Credentials (SecureString SSM, fetch at use — never paste into chat):
  - `/american-airlines/username`
  - `/american-airlines/password`
  - `/american-airlines/email`
  - `/american-airlines/aadvantage` (Jerome: **00T5FH4**; Ngoc: **630DYM2** when booking her)

### Google Flights

- Good for cash comparison; book on the operating carrier site (signed in when
  Alaska).

## Search & report format

Before asking to book, send a short options summary:

- Dates, route, nonstop vs connection
- Flight numbers + local times
- Fare type + total (cash and/or points)
- Recommendation and why (price / schedule / separate-ticket mix)

Then stage the chosen itinerary to Review & pay and wait.


## EFGS Saturday conflict (Julie)

Julie has **in-person EFGS** most Saturdays **09:15–12:15 PT** at Bertschi School
(Seattle). Full date list lives in skill **`efgs`** — read that file or ask EFGS;
do not invent Saturdays.

**Trigger:** booked (or OK’d) itinerary with any segment/overnight **outside
Washington** (CA/SJC, HI, OR, etc.).

**Action:** `SendToAgent` → EFGS (`00e87ed1-d005-4527-b29b-bfe7cccb59c2`) with a
short factual ping. Example:

> Out-of-WA booking: SEA→SJC Mon 2026-09-21, SJC→SEA Fri 2026-09-25 AS ####,
> conf XXXXXX. Travelers: Jerome only. Please check Julie EFGS Saturdays in the
> trip window and warn Jerome if she would miss class.

EFGS replies with the warning; Flight Booking can mention the conflict in chat
once EFGS confirms.

**No trigger:** itineraries that stay entirely in Washington.

## Continuous improvement

After each booking, correction, or any skill tweak Jerome asks for:

1. Patch this file under `skills/flight-booking/SKILL.md` in
   `~/localGrokSkills` (repo `jeromevidaao/localGrokSkills`).
2. **Immediately** commit + push (same turn) — **always-push**: public → push
   `main` → CI green → private. Never batch “I’ll push later.”
3. Append the turn to Titan (`r2_memory_turn.py append`) and refresh catalog if
   the skill changed (`r2_index_catalog.py`).
4. Mirror durable profile facts into the Flight Booking agent memory.
5. Do **not** leave learnings only in chat or only on the box disk.

## Do not

- Book without explicit OK
- Omit middle name Lionel (hard fail — always book + verify Jerome Lionel Ansia)
- Skip TSA Pre / KTN **992626698** (hard fail — always fill + verify on every booking)
- Skip billing address or contact email on forms
- Proceed as Alaska guest when login works
- Skip Ngoc on flight or Santa Clara calendar events
- Skip `jansia@nvidia.com` on timed flight-duration calendar events
- Paste secrets into chat; use box handoff for payment/auth
- Skip EFGS ping on out-of-WA bookings (incl. SEA↔SJC work weeks)
