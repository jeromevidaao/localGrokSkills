---
name: gorin-tennis-booking
description: >
  Use this whenever Jerome asks about Gorin Tennis / CourtReserve lessons for
  Julie (Bellevue Tiny Tigers / U6 or Future Stars / U8): search, book, cancel,
  refunds, or calendar. Read it at the start of every Gorin Tennis Booking
  conversation; update and push after anything new.
---

# Gorin tennis booking (Julie Ansia)

Standing playbook for the **Gorin Tennis Booking** bot. On every Jerome
message: **Titan retrieve first**, then read this skill. After the conversation
(or any new fact), **update this file**, **append the turn to Titan**, and
**commit + push immediately**.

Related: `r2-memory` (Titan retrieve/append), `always-push`, `family-travel`
(Julie is the same 6-year-old).

## Hard rules (never skip)

1. **Bellevue only** unless Jerome says otherwise. Do not book Redmond, Tacoma,
   or Tukwila.
2. **Student is Julie Ansia**, DOB **3 Dec 2019** (girl, 6). Book her, never
   Ruby as the player. CourtReserve child member **#11433210**.
3. **Account:** Gorin Sports Washington CourtReserve club **7306**, signed in as
   **Ruby Dinh** (guest / non-member). Portal:
   https://app.courtreserve.com/Online/Portal/Index/7306
   Login email: `ngoc.h.dinh@gmail.com`. Intended SSM:
   `/gorin/courtreserve/username` and `/gorin/courtreserve/password` (SecureString).
   `GrokBotTitanAccess` **v6** can `ssm:PutParameter` (granted 2026-09-13).
   `/bellevue-club/*` is Bellevue Club — never use it for Gorin.
   Never put the CourtReserve password in this skill or in chat.
   Owner monitor: **More → Tennis Ops** on Android (OTA 1.3.78) and website
   `#!/tennis-ops` (`act=tennis_ops_status`) lists Julie U6 upcoming/past from
   CourtReserve. Do not invent lessons if that section is unavailable.
4. **No Sunday lock-in.** Winter Sundays are for skiing. Book Sunday only when
   Jerome asks for a specific date (week-ahead is usually enough).
5. **Drop-in, not packages.** Single date only unless he asks for a full-event
   block. Do not click “Register for Full Event”.
6. **Julie is 6** (DOB 3 Dec 2019). Jerome is **flexible on class type** at
   Bellevue. **90-min is even better** than 60-min when pairing a court:
   prefer **Future Stars / U8 (201)** (ages 6–8, 90 min, $57 + tax) plus a
   matching full court, then **Tiny Tigers / U6 (101)** (ages 4–6, 60 min,
   $40 + tax). Gorin prefers ~6 months of tennis before U8 at age 6; ages
   7–8 can join U8 with no experience. Still Bellevue only, drop-in only.
   **Sunday is better than Saturday** when both work (this overrides the
   “no Sunday lock-in” rule only for a date Jerome names).
7. **Always calendar + invite both + pin:** after every confirmed booking,
   create a timed Google Calendar event on `jerome.ans@gmail.com` and
   **always invite Jerome and Ngoc** (`jerome.ans@gmail.com`,
   `ngoc.h.dinh@gmail.com`). Never skip the invite. No Google Meet.
   **Always put that booking’s CourtReserve Pin Code in the event
   description** (e.g. `Door pin for this class: 7675#`). Pins are
   per-class; never copy an old pin onto a new date. If a pin is found
   later, update that event.
8. **Always commit + push this skill** after any edit (public → `git push`
   `main` → CI green → private). Never ask “want me to push?”. Do not add a
   GitHub connector or MCP for this repo.
9. **Waiver / payment:** do not draw Ruby’s liability signature. Hand the box
   (`request_box_help`) for waiver, 2FA, or a new card. Card on file ends
   **8431** (Preferred; brand not shown in CourtReserve).
10. After each chat: patch this `SKILL.md` with anything new, then push (rule 8)
    and mirror durable facts into agent memory.
11. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
    **retrieve first**, then **append/update after the turn** so Titan stays
    current. Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook:
    skill `r2-memory`.
12. **Never half court.** Jerome never wants **BTA Half** or any half-court.
    Only book a **full court** (BTA 1–4). If the only open slot is half-court,
    skip it and say so. Do not hold or pay for a half-court “to save money.”
    The cheaper ~$23 quote is typically a half-court, not a week-ahead discount.

13. **Travel skip.** Before booking any class date, check Jerome’s Google Calendar
    for flights, Hawaii, or out-of-town blocks that overlap that Sunday. Skip
    those dates (example: end-of-year Hawaii Dec 21–31 2026). Do not book tennis
    while the family is away.

## Titan R2Memory (every turn)

Scripts live at `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`).

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing prefs / past tennis decisions. Also read this
`gorin-tennis-booking` skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Do this for every meaningful tennis turn (search, book, cancel, calendar,
preference). Keep the git skill updated and pushed as well (rule 8).

After adding or editing this skill, refresh the Titan catalog:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_index_catalog.py
```

## People

| | |
|---|---|
| Child | Julie Ansia, born 3 Dec 2019 |
| CourtReserve login | Ruby Dinh (Ngoc), guest |
| Ruby / Ngoc email | ngoc.h.dinh@gmail.com |
| Jerome calendar | jerome.ans@gmail.com |
| Front desk | (425) 274-2969 · WashingtonCustomerCare@GorinTennis.com |
| Door pin | **Per booking**, not static. CourtReserve event field **Pin Code**. Confirmed 13 Sep 2026: that day’s U6 was `2894#`; Julie’s Sun 20 Sep U8 is `7675#`. Unregistered events show no pin. Always read it from My Bookings for that date. |

## Club & location

| | |
|---|---|
| Club | Gorin Sports Washington, CourtReserve **7306** |
| Book | Bellevue Tennis Academy, 13203 NE Spring Blvd, Bellevue, WA 98005 |
| Court (U6) | Bellevue Kids Court |
| Public facility | No membership required |

Junior pages:
- https://www.gorintennis.com/our-washington-locations/bellevue-junior-programs
- Embed: https://app.courtreserve.com/Online/Public/EmbedCode/7306/22145 (category BELLEVUE JUNIOR TENNIS PROGRAM)

Naming: through Aug 31 2026 classes showed **TINY TIGERS U6** / **FUTURE STARS U8**.
From Sep 2026 the same slots are **U6 (101)** and **U8 (201)**.


## Tennis Ops / CourtReserve sync (2026-09-21 ~8pm PT)

- **Upcoming Julie lessons on CourtReserve: none.** My Bookings Active (custom date range, Julie+Ruby) and `backend.courtreserve.com/api/my-bookings-portal/get-list` both return empty. Do not invent Oct series as booked.
- Oct U8 (201) **T2M7CEQ7306110** / eventId **2269553** / resIds 60796521–60796524 is the **catalog** full-event (11/12 spots). Single-date opens ~Sat Sep 26 AM. Not on GetAllTransactions until paid/booked.
- History on tennis-ops comes from GetAllTransactions: U6 9/13 (LJON17306/XUIWA7306), U8 9/20 (ISFVM7306/C5T4Y7306).
- API `act=tennis_ops_status` now merges GetAllTransactions + My Bookings (`sourcesChecked`). GCal has no upcoming Gorin events (only those two past).

## Bellevue weekly pattern (as of 30 Aug 2026)

**Tiny Tigers / U6 (101)** — 60 min, **$40** single / $160 for 4 dates (prices + tax)

| Day | Time |
|---|---|
| Mon | 4:30–5:30pm |
| Wed | 4:30–5:30pm |
| Fri | 4:30–5:30pm |
| Sat | 11:30am–12:30pm |
| Sun | 2:30–3:30pm |

**Future Stars / U8 (201)** — 90 min, **$57** single / $228 for 4 dates

Mon–Fri 4:30–6:00pm, Sat 10:00–11:30am, Sun 1:00–2:30pm.

U8 Advanced (202) is Tue/Thu 4:30 — not a first class. Mini-group of 3 with
Coach Davi (Sat 12:30 or 2:30, $55) is usually waitlist.

Weekday 4:30s (especially 6-spot U6 Mon/Wed) fill faster than Sat/Sun.
Guest court window is ~7 days; group drop-ins are listed weeks out.

Optional junior membership $100/year: 12% off a monthly series. Not required.

## Court rentals (Bellevue / BTA)

As of 13 Sep 2026: full court **\$47.25 + \$4.87 tax = \$52.12** per hour
(same-day 13 Sep quote). Same-day hold must be paid within **15 minutes**.
Courts: BTA 1–4 (full — **these only**), BTA Half (**never book**), BTA Kids
(class court). Junior classes often block Kids + other courts Sunday 2:30.
Book via Reservations, not Events. Do not book Bellevue Club.

A ~$23–$26 quote is usually **BTA Half** (exactly half of $47.25), not a
week-ahead sale. Confirm duration and court type before treating any quote
as a discount.

**Pairing (ideal):** book Julie’s Bellevue class **and** a full court (BTA
1–4) for the **same window** so Jerome can play while she is in class.
**90-min U8 + 90-min (or overlapping) full court is better** than 60-min U6
+ 1-hour court. If both class and full court are open, book both. If only
the class is open, say so and do not book a half-court as a substitute.


## Book a drop-in (CourtReserve)

1. Sign in as Ruby Dinh on portal 7306 (browser; no CourtReserve connector).
2. Events → List. Search is unreliable — scan **U6 (101)** / Tiny Tigers,
   Bellevue, the requested date.
3. **Register for [that date]** only. Leave other Sundays unchecked.
4. If a liability waiver blocks, hand the box to Jerome/Ruby to sign. Do not
   sign it yourself.
5. If Julie is missing from My Family, add her (first Julie, last Ansia, DOB
   12/03/2019, Child, Female). Email not required; “Not Allowed To Log In” is OK.
6. Select **Julie Ansia**. Confirm total (~$40 + tax + convenience fee; Sept 13
   example was **$45.66**).
7. Pay with the card on file if that is what he asked. Stop for a new card.
8. Capture receipt #, who, date/time, amount.
9. Add Google Calendar (rule 7). Title like `Julie — Tiny Tigers tennis`.
   Location: Bellevue Tennis Academy address. Description must include
   coaches, receipt, 24h cancel, and **this booking’s Pin Code**.

## Cancel / refund

Drop-in cancelled **24+ hours** before start: **full refund** (Gorin group-class
policy). Inside 24 hours: no refund on the guest plan (no protection pass).
Cancel on CourtReserve (My Profile / the reservation), same Ruby account.
Confirm in chat before cancelling.

## Latest single-date watch (read-only 2026-09-21 ~4:13pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId 60796521). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm, Bellevue Kids Court. Coaches **Fatma Tapan, Gulcin Odemis**. Price **$57 single / $228 full**. **11 of 12 spots remaining**.
- DATES tab exact text on Oct 4, 11, 18, and 25: **“Single date registration opens in 4 days and 13 h”** (~Sat Sep 26 early morning). Only **Register for Full Event** is clickable. Do not click it.
- Per-date list reservations (same series): Oct 4 T2M7CEQ7306110 / 60796521; Oct 11 J4BVP237306130 / 60796522; Oct 18 ML2PHM57306153 / 60796523; Oct 25 PX8U4Z17306174 / 60796524.
- November U8 / Future Stars Sundays still **not listed**.
- My Bookings (Sep 21–Nov 30, Julie + Ruby): **No bookings found**.
- Travel gate: **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA Sun Oct 25 ~3:53–6:44pm PT overlaps class; Oct 4/11/18 and Nov Sundays still clear (SC midweek; Hawaii Dec 21–31).


## Follow-up read-only watch (2026-09-21 ~4:13pm PT)

- Bellevue U8 (201) Oct 4/11/18/25 DATES tab still showed exact text **“Single date registration opens in 4 days and 13 h”** for every date; single-date registration remains closed and **Register for Full Event** is still the only registration control.
- Series still showed **11 of 12 spots remaining**; instructors **Fatma Tapan, Gulcin Odemis**.
- Event List search for **U8 (201)** returned events only through Oct 31; no November Bellevue U8/Future Stars Sundays were listed.
- My Bookings Active with Ruby Dinh and Julie Ansia selected, custom Sep 21–Nov 30, showed **No bookings found**.

## Current bookings

- **Sun 13 Sep 2026, 2:30–3:30pm** Bellevue U6 (101) / Tiny Tigers
  Julie Ansia · Gulcin Odemis, Fatma Tapan
  Receipt **LJON17306** · $45.66 · card …8431 · booked 30 Aug 2026
  Calendar: https://www.google.com/calendar/event?eid=bjdvMmtrbzU2NWc1NDc1MDZjZGZiamZrZzQgamVyb21lLmFuc0Bt
- **Sun 20 Sep 2026, 1:00–2:30pm** Bellevue U8 (201) / Future Stars
  Julie Ansia · Fatma Tapan, Gulcin Odemis
  Receipt **ISFVM7306** · $65.07 · booked 13 Sep 2026
  Calendar (Jerome + Ngoc invited): https://www.google.com/calendar/event?eid=cnVtcTcxaGNodDYxczN1OHVrMW4yY3FvazQgamVyb21lLmFuc0Bt
  Free cancel until Sat 19 Sep 1:00pm PT

## Continuous improvement

After each book, cancel, schedule change, or correction:

1. Patch `skills/gorin-tennis-booking/SKILL.md` in `~/localGrokSkills`
   (repo `jeromevidaao/localGrokSkills`).
2. Commit + push the same turn (always-push).
3. Mirror durable facts into Gorin Tennis Booking agent memory **and Titan**
   (`r2_memory_turn.py append`).
4. Do not leave learnings only in chat.

## Do not

- Book Redmond / Tacoma / Tukwila
- Register Ruby as the player
- Buy a 4-week package unless asked
- Lock every Sunday (skiing)
- Sign the waiver or type card numbers
- Skip the calendar event, or skip inviting Jerome or Ngoc
- Add a GitHub connector just to update this repo
- Book **BTA Half** or any half-court (full court only: BTA 1–4)
