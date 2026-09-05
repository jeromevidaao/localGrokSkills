---
name: flight-booking
description: >
  Use this whenever searching, comparing, holding, or booking flights for Jerome
  Lionel Ansia (Alaska, Southwest, Delta, Chase Ultimate Rewards, Google Flights),
  or after any flight purchase when calendar / FF / TSA steps are needed. Also
  refine this skill after every completed booking.
---

# Flight booking (Jerome Lionel Ansia)

This is the standing playbook for the **Flight Booking** bot. On every Jerome
message: **Titan retrieve first**, then read this skill. Pull TSA / frequent-flyer
numbers from the **DINH ANSIA PERSONAL WIKI** sheet. After every completed booking
(or any correction Jerome gives), **update this skill**, **append the turn to Titan**,
and **commit + push immediately** — keep improving it.

Related: `r2-memory` (Titan retrieve/append), `always-push`,
`santa-clara-stay-from-alaska-flights` (calendar week blocks), `family-travel`
(SEA–HNL family trips — different party).

## Hard rules (never skip)

1. **Legal name:** passenger is always **Jerome Lionel Ansia** (first / middle / last).
   Never omit **Lionel**. Prefer forms that accept full middle name; if only middle
   initial is allowed, use **L**. Fix typos like JEEROME if prefilled.
2. **Purchase gate:** stop at Review & pay / payment. Get Jerome’s **explicit OK**
   in chat before charging. Do not auto-book even under an old price threshold.
3. **Alaska login:** on alaskaair.com always sign in as Atmos **325534370**
   (Jerome Ansia) before search/book — never guest if login is available.
4. **Contact email:** always fill **jerome.ans@gmail.com** on passenger / contact /
   receipt fields. Never leave blank or use a different address.
5. **Billing address:** always fill the full home/billing address on payment forms:
   **3099 125th Ave NE, Bellevue, WA 98005** (street, city, state, ZIP). Never skip.
6. **Wiki before FF/TSA fields:** before filling Known Traveler / frequent-flyer
   numbers, open the **DINH ANSIA PERSONAL WIKI** Google Sheet and use the values
   there (do not invent or reuse stale guesses). Sheet:
   https://docs.google.com/spreadsheets/d/1agABcM6hBCmzPXXy3o2D8XtJClu34paWT358l56KzUo/edit
   Drive file id: `1agABcM6hBCmzPXXy3o2D8XtJClu34paWT358l56KzUo`
7. **Always commit + push this skill:** any edit to `skills/flight-booking/` (or
   related flight playbook) must be committed and pushed to
   `jeromevidaao/localGrokSkills` **immediately** — never leave skill changes only
   on disk. Follow **always-push** (public → `git push` `main` → CI green → private).
   Do not ask “want me to push?”.
8. **Refine after book:** when a booking finishes (or Jerome corrects a field),
   update this `SKILL.md` with the learning, then commit + push (rule 5), and
   mirror durable facts into agent memory.
9. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
   **retrieve first**, then **append/update after the turn** so Titan stays current.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook: skill `r2-memory`.

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

Loyalty defaults when the airline allows a partner:

- **Alaska:** prefer credit to **AA 00T5FH4** when the form lets you pick American;
  otherwise Atmos 325534370. Note: Saver / some one-ways may lock Atmos and block
  self-serve FF edits — tell Jerome (call Alaska or add at check-in).
- **Delta:** SkyMiles 9214639644.
- **Southwest:** Rapid Rewards if on file; otherwise guest OK. Atmos does not apply.

## Default work-week pattern (SEA ↔ SJC)

Typical week: **Mon ~7am SEA→SJC**, **Fri ~5pm SJC→SEA**, **nonstop** preferred.

1. Compare **Alaska** (signed in), **Google Flights**, and when useful **Southwest**
   / **Chase Ultimate Rewards** points. Separate tickets are fine if cheaper.
2. Prefer nonstops near those times; report options + totals before booking.
3. Saver / Basic is OK when Jerome chooses price over flexibility.
4. Hold or stage to Review & pay; wait for explicit OK; then pay.
5. After purchase, run **Post-booking checklist** below.

## Post-booking checklist (every flight)

Do all of these before saying done:

1. Capture **confirmation code**, ticket/e-ticket if shown, fare paid, flight numbers,
   times, cabin/fare type.
2. **Calendar — timed flight event** for each booked leg:
   - Title like `Flight to San Jose (AS 1341)` / `Flight to Seattle (WN 698)`
   - Correct local times; note conf + fare in description
   - Invite **ngoc.h.dinh@gmail.com** (and Jerome accepted)
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

## Airline / site notes

### Alaska (alaskaair.com)

- Sign in first (Atmos). Sessions and fare holds expire (~10 min) — restage if stale.
- Sticky Continue / Skip seats buttons can be inert in DOM; use reliable click
  paths (browserUse first; computerUse if needed).
- Prefer saved Atmos card when paying as Jerome; still wait for OK before pay. If billing address is required, use **3099 125th Ave NE, Bellevue, WA 98005**; contact email **jerome.ans@gmail.com**.
- After book: Trips list, calendar, FF/TSA.

### Southwest (southwest.com)

- Guest checkout is common; no Atmos.
- Fill full name **Jerome Lionel Ansia**, DOB, gender, email **jerome.ans@gmail.com**, phone, KTN, and billing **3099 125th Ave NE, Bellevue, WA 98005** when asked.
- Skip seats if optional; stop for card entry if no saved method / Apple Pay.
- Calendar + Santa Clara week still apply for SJC work returns.

### Chase Ultimate Rewards

- Search/book in points when Jerome asks; report points + cash equivalent.
- Traveler must show **JEROME LIONEL ANSIA** / **JEROME L ANSIA**, not JEEROME.
- After book: still add calendar events and claim airline PNRs when given.

### Delta

- Captcha / login often fails — hand box for login; use SkyMiles + KTN.
- Prefer nonstop when comparing against Alaska/Southwest.

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
- Omit middle name Lionel
- Skip billing address or contact email on forms
- Proceed as Alaska guest when login works
- Skip Ngoc on flight or Santa Clara calendar events
- Paste secrets into chat; use box handoff for payment/auth
