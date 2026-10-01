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

13. **Travel skip.** Before every book, check Jerome’s Google Calendar as the
    **source of truth** for ANY vacation/travel — not only a fixed list. Skip the
    Sunday if class overlaps flights, hotel/Airbnb stays, out-of-town blocks,
    Palm Springs, school breaks away, Hawaii, Japan, or similar (including travel
    days). Do not book tennis while the family is away. Known examples (still
    re-check live):
    - Hawaii Dec 21–31 2026 (AS 811 SFO→HNL / AS 940 HNL→SEA)
    - Japan Bamboo-Hill Nozawa Onsen Feb 15–19 2027 (and flight days)
    - Palm Springs Oct 23–25 2026 → **SKIP Oct 25** Future Stars while return
      AS 759 PSP→SEA ~3:53–6:44pm PT overlaps 1:00–2:30 class
    Midweek Santa Clara alone does not block a Sunday if they are home that day.


14. **Tennis Ops series keys:** never merge **Mini Group** / “of 3” / Coach Davi
    lessons into the U8 Future Stars card. Mini Group (e.g. Sep 27 9–10am with
    Coach Davi) is its own series; U8/201 drop-ins (Oct 4/11/18 1:00–2:30pm) stay
    on the U8 card. `buildGorinSeries` in cleaningbutton-api enforces this.

15. **Calendar links = eventedit only.** When sharing or deep-linking a Google
    Calendar event for Jerome, always use:
    `https://calendar.google.com/calendar/u/0/r/eventedit/{base64(eventId + " " + calendarId).replace(/=+$/,"")}?tab=mc`
    with `calendarId = "jerome.ans@m"` (not the full mailbox, not
    `www.google.com/calendar/event?eid=`). Day-view URLs (`/r/day/...`) are
    fallback-only on website/Android; prefer API `gcalByDate` / `gcalUrl`.

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

## Door-code ping (5 minutes before class ends)

EventBridge rule `gorin-door-ping` runs every minute and invokes Lambda `api`
with `{ "mode": "gorin_door_ping" }`. Inside the last 5 minutes of a Julie
Gorin class it sends one R2 Android FCM `type=gorin_door_code`. When that
booking’s CourtReserve Pin Code is present, the title is `Gorin door 7675#`
(example of the shape, not a live pin). It does not invent a pin. If the pin
is missing, the ping says so, and one later poll in that same window sends
again when the pin appears. Dedupe is DynamoDB `homeexchangeMessageState` pk
`gorin_door_ping`. CourtReserve is refreshed at most hourly from 7am–9pm PT,
and every 6 hours overnight. Tap opens Tennis / Swim on app 1.3.102+.

Created 2026-09-27 by IAM user `jeromeans` with
`bash scripts/ensure-gorin-door-ping.sh` in `cleaningbutton-api`. Confirmed
ENABLED, `rate(1 minute)`, target Lambda `api`, input
`{"mode":"gorin_door_ping"}`. The GitHub deploy role
`github-actions-cleaningbutton-deploy` cannot `events:PutRule` on this rule.
That deploy step runs under `set +e` and still prints a green check, which
does not mean the rule exists. Re-apply with the script as `jeromeans` (or
grok-bot-titan, which has `events:*`). Do not delete the rule.

Live check 2026-09-27 afternoon PT: the ping’s CourtReserve fetch sees the
Oct 4/11/18 U8 classes and no Pin Code. `GetAllTransactions` has no pin
field, and `my-bookings-portal/get-list` returns an empty list, so the ping
cannot repeat the pins that were on the My Bookings screen that morning. It
says the code isn’t on the booking, then looks again during those five
minutes.

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

- **Upcoming Julie lessons on CourtReserve: none** (re-verified 2026-09-21 PT). Live Lambda `act=tennis_ops_status` + direct CourtReserve probe: login OK as `ngoc.h.dinh@gmail.com`, Julie #11433210 found, GetAllTransactions=2 past only (U6 9/13, U8 9/20), My Bookings `get-list` rawCount=0 for all DatesString/OrgMemberIds variants. Oct U8 catalog is not a registration. API now passes live family org Ids (`11427703,11433210`) into My Bookings (was stale `10788691/10785548`). Do not invent lessons.
- Oct U8 (201) **T2M7CEQ7306110** / eventId **2269553** / resIds 60796521–60796524 is the **catalog** full-event (11/12 spots). Re-checked **2026-09-21 ~9:54pm PT**: single-date still closed — SignUpToEvent_Get says opens in **4 days and 7 h** (~Sat Sep 26 AM). Not on GetAllTransactions until paid/booked.
- History on tennis-ops comes from GetAllTransactions: U6 9/13 (LJON17306/XUIWA7306), U8 9/20 (ISFVM7306/C5T4Y7306).
- API `act=tennis_ops_status` now merges GetAllTransactions + My Bookings (`sourcesChecked`). GCal has no upcoming Gorin events (only those two past).


## Google Calendar event IDs (Gorin one-shots, calendarId jerome.ans@m)

Stored in DynamoDB `tennisOpsGcalEvents` pk `julie-gorin-events`. Verified:

| Date (PT) | Program | eventId |
|---|---|---|
| 2026-09-27 | Future Stars Mini Group with Coach Davi 9–10am | `ttrorsojek4j6imeefejlq4b74` |
| 2026-10-04 | U8 Future Stars 1:00–2:30pm | `o69pi2jc1al25hknnab3b2rm10` |
| 2026-10-11 | U8 Future Stars 1:00–2:30pm | `p046fgch9injh8fd4299n01cs4` |
| 2026-10-18 | U8 Future Stars 1:00–2:30pm | `ff101so6utpuria2rsq649cv8k` |

Share links via eventedit (rule 15). Tennis Ops API attaches these as `gcalByDate` / `gcalUrl`.

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

## Latest booking (2026-09-26 ~9:03am PT)

- **Julie** Bellevue **Future Stars Mini Group with Coach Davi** (Davi Sandes), **Sun Sep 27 2026 9:00–10:00am PT**, Bellevue Kids Court.
- Drop-in Register (not Full Event). Receipt **JW7IF7306**, **$62.79** card …8431. Pin not shown at book time.
- Calendar on jerome.ans@gmail.com with invites to Jerome + Ngoc. GCal eventId `ttrorsojek4j6imeefejlq4b74` (eventedit via jerome.ans@m).
- Tennis Ops: Mini Group must stay a separate card from U8 Oct drop-ins (not merged under Davi).
- Context: Bellevue U8 1:00–2:30 and U6 2:30–3:30 that Sunday were Registration Closed; this 60-min mini-group was the open Julie-fit option (1 of 3 spots).

## Prior watch (live API 2026-10-01 ~4:20pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (plus outbound AS 792 Oct 23 SEA→PSP). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only: Nov 2–6, 16–20, from Nov 30).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-10-01 ~12:17pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (plus outbound AS 792 Oct 23 SEA→PSP). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only: Nov 2–6, 16–20).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-30 ~4:10pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (plus outbound AS 792 Oct 23 SEA→PSP). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only: Nov 2–6, 16–20, from Nov 30).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-30 ~12:17pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (plus outbound AS 792 Oct 23 SEA→PSP). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only: Nov 2–6, 16–20, from Nov 30).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-30 ~8:16am PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- 8am drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-29 ~4:18pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (events Flight to Seattle AS 759). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-29 ~12:11pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-29 ~8:29am PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; nov_cards empty; novOpenDates=[]; candidates=[]; ApiLoadEvents 404/HTML). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- 8am drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-28 ~4:15pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=8/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; nov_cards empty; novOpenDates=[]; candidates=[]). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-28 ~12:17pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=8/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (LoadEvents/embed hasNovU8=false; nov_bel_u8_count=0; Nov catalog Sundays not Bellevue U8). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear (Santa Clara midweek only).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-28 ~8:30am PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=8/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (LoadEvents Bellevue U8 Sunday cards only Oct 4/11/18/25; nov_bel_u8_count=0; Nov catalog Sundays are USTA evenings only). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear (Santa Clara midweek only: Nov 2–7, 16–21, 30–Dec 5).
- 8am drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-27 ~12:18pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms tid **118181133** $195.21 plus per-date 118181135/136/137 $62.87 (Julie #11433210); prior receipt VGSWU7306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get open (AllowDropIns=true, AvailablePlaces=9/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (nov_cards empty; Events `ApiLoadEvents` 404/empty; public embed hasNovU8=false; Bellevue U8 Sunday cards end Oct 25). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear (Santa Clara midweek only: Nov 2–7, 16–21, 30–Dec 5).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-27 ~8:19am PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date codes 5TZR57306 / 1N3GN7306 / PCHY67306.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get shows drop-in open (AllowDropIns=true, 9/12 spots, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (EventsApi `ApiLoadEvents` Bellevue U8 Sunday cards end Oct 25; no Nov-dated Bellevue U8 (201) cards). Register N/A. My Bookings get-list rawCount=0; pins TBD.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear (Santa Clara midweek only: Nov 2–7, 16–21, 30–Dec 5).
- 8am drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-26 ~4:19pm PT)

- Bellevue U8 (201) series still eventId **2269553** / Oct resIds 60796521–24. Range **Oct 4–Oct 25** Sundays 1:00–2:30pm.
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “You already registered for this event.” GetAllTransactions confirms VGSWU7306 / tx **118181133** $195.21; per-date codes 5TZR57306 / 1N3GN7306 / PCHY67306; eventId 2269553.
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal. SignUp Get shows drop-in open (AllowDropIns=true, ~10/12 spots, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (EventsApi `ApiLoadEvents` Bellevue U8 Sunday cards end Oct 25; no Nov-dated U8 (201) Bellevue cards; Nov 29 absent from catalog text). Register N/A. My Bookings get-list rawCount=0; pins TBD.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear (Santa Clara midweek only: Nov 2–7, 16–21, 30–Dec 5).
- 4pm drop-in watch: **no book, silent**.

## Latest single-date watch (live API 2026-09-26 ~8:30am PT)

- Bellevue U8 (201) series eventId **2269553** / Oct resIds 60796521–24. Single-date **OPEN** this morning.
- **BOOKED drop-in** Julie Ansia #11433210 for **Oct 4, Oct 11, Oct 18** via `EventApi_SignUpToEvent_DropIn_Post` + ProcessPayment card …8431. **Did not** Full Event. **SKIP Oct 25** (Palm Springs AS 759).
- Combined receipt **VGSWU7306** · Subtotal $171.00 + tax $17.61 + convenience $6.60 = **$195.21** (≈$62.87/date).
- Spots after book: **9 of 12** remaining on each Oct Sunday.
- Coaches: Oct 4 Fatma Tapan & Omer Dogu Sahin; Oct 11/18 Fatma Tapan & Gulcin Odemis.
- Reservations: Oct4 T2M7CEQ7306110/60796521; Oct11 J4BVP237306130/60796522; Oct18 ML2PHM57306153/60796523. ReservationMemberIds 128684029/128684031/128684035.
- Calendar events created on jerome.ans@gmail.com with invites to Jerome + Ngoc (no Meet). Door pins: My Bookings API returned rawCount=0 at book time — pin TBD in CourtReserve closer to class.
- November Bellevue U8 Sundays **not listed** (embed/GetEvents/EventsList scan).
- Travel: SKIP Oct 25 Palm Springs; Oct 4/11/18 bookable; Nov Sundays clear when series appears.

## Prior watch (live API 2026-09-25 ~4:19pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`): **“Registration not yet open for this date. Registration opens in 13 h and 10 min .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- November Bellevue U8 Sundays scan inconclusive this run (`ApiLoadEvents`/`GetEvents` returned HTML 404); prior watches had Nov Sundays not listed. No Oct/Nov bookings made this run.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- Note: Node `aws-sdk` LogInReact hit Cloudflare **403**; Python urllib login + EventsApi probe succeeded.
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-25 ~12:15pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`): **“Registration not yet open for this date. Registration opens in 17 h and 14 min .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- November Bellevue U8 Sundays scan inconclusive this run (`ApiLoadEvents`/`GetEvents` returned HTML 404); prior watches had Nov Sundays not listed. My Bookings `get-list` **rawCount=0** for 9/21–12/1. No Oct/Nov bookings made this run.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-25 ~8:15am PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`): **“Registration not yet open for this date. Registration opens in 21 h and 13 min .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- November Bellevue U8 Sundays scan inconclusive this run (`ApiLoadEvents` returned an HTML error page); prior watches had Nov Sundays not listed. No Oct/Nov bookings made this run.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- Browser computerUse check failed (`resource_exhausted`); curl+JWT API probe succeeded. 8am drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-24 ~4:18pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`): **“Registration not yet open for this date. Registration opens in 1 day and 13 h .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- November Bellevue U8 Sundays **not listed** (Bellevue U8 cards through Oct 31 weekday/Sat only). No Oct/Nov bookings made this run.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live UI 2026-09-24 ~12:26pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm, Bellevue Kids Court. Price **$57 single / $228 full**. **10 of 12 spots remaining**.
- **Oct 4/11/18/25 single-date still CLOSED.** Live CourtReserve UI (logged in as Ruby): **“Single date registration opens in 1 day and 17 h”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- Per-date list reservations (same series): Oct 4 T2M7CEQ7306110 / 60796521; Oct 11 J4BVP237306130 / 60796522; Oct 18 ML2PHM57306153 / 60796523; Oct 25 PX8U4Z17306174 / 60796524.
- November U8 Sundays **not listed**. My Bookings empty for Oct/Nov (past U6 9/13 + U8 9/20 only).
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- Noon drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-24 ~8:28am PT)

- Same series; message then **“opens in 1 day and 20 h”**; Full Event only; Nov not listed; My Bookings empty; silent.

## Prior watch (live API 2026-09-23 ~4:30pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm, Bellevue Kids Court. Price **$57 single / $228 full**. Event cards show **12 spots remaining** on Oct 4/11/18/25 Sundays.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`) returned exact message: **“Registration not yet open for this date. Registration opens in 2 days and 12 h .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- Per-date list reservations (same series): Oct 4 T2M7CEQ7306110 / 60796521; Oct 11 J4BVP237306130 / 60796522; Oct 18 ML2PHM57306153 / 60796523; Oct 25 PX8U4Z17306174 / 60796524.
- November U8 Sundays **not listed** (Events ApiLoadEvents Bellevue U8 cards end Oct 31; no Nov Sunday U8 series). My Bookings `get-list` Data empty for 9/21–12/1.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-23 ~12:36pm PT)

- Same series; message then **“opens in 2 days and 16 h”**; Full Event only; spots last known 10/12; coaches Fatma Tapan & Omer Dogu Sahin; Nov not listed; My Bookings empty.

## Prior watch (live API 2026-09-23 ~8:57am PT)

- Same series; message then **“opens in 2 days and 20 h”**; Full Event only; spots last known 11/12; Nov not listed; My Bookings empty.

## Prior watch (live API 2026-09-22 ~4:24pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm, Bellevue Kids Court. Coaches **Fatma Tapan, Gulcin Odemis**. Price **$57 single / $228 full**.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`) returned exact message: **“Registration not yet open for this date. Registration opens in 3 days and 13 h .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- Per-date list reservations (same series): Oct 4 T2M7CEQ7306110 / 60796521; Oct 11 J4BVP237306130 / 60796522; Oct 18 ML2PHM57306153 / 60796523; Oct 25 PX8U4Z17306174 / 60796524.
- November U8 Sundays **not listed** (Oct series ends Oct 25; no separate Nov series found via Events GetEvents). GetAllTransactions still only past U6 9/13 + U8 9/20.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only; Hawaii Dec 21–31).
- 4pm drop-in watch: **no book, silent**.

## Prior watch (live API 2026-09-22 ~12:15pm PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm, Bellevue Kids Court. Coaches **Fatma Tapan, Gulcin Odemis**. Price **$57 single / $228 full**. **11 of 12 spots remaining**.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`) returned exact message: **“Registration not yet open for this date. Registration opens in 3 days and 17 h .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- Per-date list reservations (same series): Oct 4 T2M7CEQ7306110 / 60796521; Oct 11 J4BVP237306130 / 60796522; Oct 18 ML2PHM57306153 / 60796523; Oct 25 PX8U4Z17306174 / 60796524.
- November U8 Sundays **not listed** (Oct series ends Oct 25; no separate Nov series found). My Bookings get-list **rawCount=0** for 9/21–12/1; GetAllTransactions still only past U6 9/13 + U8 9/20.
- Travel gate (parent-verified this run): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- CLI tip: after login + Details page for JWT/`requestData`, call  
  `GET /Online/EventsApi/EventApi_SignUpToEvent_Get?id=7306&reservationId=60796521&eventId=2269553&isReactCall=true&ajaxCall=true&requestData=…&isApiCall=true`  
  (works on app host). Book path when open: `EventApi_SignUpToEvent_DropIn_Post` (Julie #11433210 only).

## Prior watch (live API 2026-09-22 ~8:39am PT)

- Bellevue U8 (201) series still eventId **2269553** / reservation **T2M7CEQ7306110** (resId **60796521**). Range **Oct 4–Oct 25** (4 dates), 1:00–2:30pm, Bellevue Kids Court. Coaches **Fatma Tapan, Gulcin Odemis**. Price **$57 single / $228 full**. **11 of 12 spots remaining**.
- **Oct 4/11/18/25 single-date still CLOSED.** Live `EventApi_SignUpToEvent_Get` (logged in as Ruby via SSM `/gorin/courtreserve/*`) returned exact message: **“Registration not yet open for this date. Registration opens in 3 days and 20 h .”** (~**Sat Sep 26 early morning PT**). Only **Register for Full Event** is available. **Did not** click full-event.
- Per-date list reservations (same series): Oct 4 T2M7CEQ7306110 / 60796521; Oct 11 J4BVP237306130 / 60796522; Oct 18 ML2PHM57306153 / 60796523; Oct 25 PX8U4Z17306174 / 60796524.
- November U8 Sundays **not listed** (Oct series ends Oct 25; no separate Nov series found). My Bookings get-list **rawCount=0** for 9/21–12/1; GetAllTransactions still only past U6 9/13 + U8 9/20.
- Travel gate (GCal jerome.ans@gmail.com live): **SKIP Oct 25** — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT overlaps class. Oct 4/11/18 and Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only).
- CLI tip: after login + Details page for JWT/`requestData`, call  
  `GET /Online/EventsApi/EventApi_SignUpToEvent_Get?id=7306&reservationId=60796521&eventId=2269553&isReactCall=true&ajaxCall=true&requestData=…&isApiCall=true`  
  (works on app host). Book path when open: `EventApi_SignUpToEvent_DropIn_Post` (Julie #11433210 only).

## Prior watch (live API 2026-09-21 ~9:54pm PT)

- Same series; message then **“opens in 4 days and 7 h”**; Full Event only; 11/12 spots; Nov not listed; My Bookings empty.

## Prior watch (read-only 2026-09-21 ~4:13pm PT)

- DATES tab then: **“Single date registration opens in 4 days and 13 h”**; Full Event only; 11/12 spots; no November U8 Sundays listed; My Bookings empty.

## Current bookings

- **Sun 4 Oct 2026, 1:00–2:30pm** Bellevue U8 (201) / Future Stars
  Julie Ansia · Fatma Tapan, Omer Dogu Sahin
  Receipt **VGSWU7306** (combined) · $62.87 this date · card …8431 · booked 26 Sep 2026
  Calendar: https://www.google.com/calendar/event?eid=bzY5cGkyamMxYWwyNWhrbm5hYjNiMnJtMTAgamVyb21lLmFuc0Bt
- **Sun 11 Oct 2026, 1:00–2:30pm** Bellevue U8 (201) / Future Stars
  Julie Ansia · Fatma Tapan, Gulcin Odemis
  Receipt **VGSWU7306** (combined) · $62.87 · booked 26 Sep 2026
  Calendar: https://www.google.com/calendar/event?eid=cDA0NmZnY2g5aW5qaDhmZDQyOTluMDFjczQgamVyb21lLmFuc0Bt
- **Sun 18 Oct 2026, 1:00–2:30pm** Bellevue U8 (201) / Future Stars
  Julie Ansia · Fatma Tapan, Gulcin Odemis
  Receipt **VGSWU7306** (combined) · $62.87 · booked 26 Sep 2026
  Calendar: https://www.google.com/calendar/event?eid=ZmYxMDFzbzZ1dHB1cmlhMnJzcTY0OWN2OGsgamVyb21lLmFuc0Bt
- Past: Sun 13 Sep U6 LJON17306; Sun 20 Sep U8 ISFVM7306

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

## Door pins (as of Sun Sep 27 2026 AM PT)
- Sep 27 Davi mini-group: **9086#**
- Oct 4 U8: **7631#**
- Oct 11 U8: **2375#**
- Oct 18 U8: **8762#**
(Source: CourtReserve My Bookings Active list; also written into GCal event descriptions.)

## Drop-in watch log (2026-10-01 ~12:17 PM PT)
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.”
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (plus outbound AS 792 Oct 23 SEA→PSP). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only: Nov 2–6, 16–20).
- Noon drop-in watch: **no book, silent**.

## Drop-in watch log (2026-10-01 ~8:18 AM PT)
- **Oct 4/11/18 still HELD** (Julie): `EventApi_SignUpToEvent_Get` → “already registered.”
- **Oct 25 SKIP** unchanged — Palm Springs return AS 759 PSP→SEA ~3:53–6:44pm PT still on GCal (plus outbound AS 792 Oct 23 SEA→PSP). SignUp Get open (AllowDropIns=true, AvailablePlaces=7/12, coaches Fatma Tapan & Gulcin Odemis) but **did not book**.
- November Bellevue U8 Sundays **still not listed** (embed hasNovU8=false; novDates=[]; novOpenDates=[]; candidates=[]; ApiLoadEvents/getEvents 404/HTML; Events List listHasNovU8=false). Register N/A. My Bookings get-list rawCount=0.
- Travel gate (GCal jerome.ans@gmail.com live): SKIP Oct 25 Palm Springs AS 759. Nov 1/8/15/22/29 clear of overnight family travel (Santa Clara midweek only: Nov 2–6, 16–20, from Nov 30).
- 8am drop-in watch: **no book, silent**.

