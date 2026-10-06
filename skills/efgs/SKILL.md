---
name: efgs
description: >
  Use this for Julie’s EFGS (Education Française Greater Seattle) school calendar,
  in-person Saturday classes at Bertschi, Google Calendar sync, inviting Ngoc,
  and flight/travel conflict warnings when family is outside Washington on a class
  Saturday. Also read and refine this skill on every EFGS conversation.
---

# EFGS (Julie — French school)

Standing playbook for the **EFGS** bot. On every Jerome message:
**Titan retrieve first**, then **read this skill**. After the conversation (or any
correction), **update this file**, **append the turn to Titan**, and **commit +
push immediately** to `jeromevidaao/localGrokSkills` (follow **always-push**:
public → `git push` `main` → CI green → private). Never ask “want me to push?”.
Do not add a GitHub connector or MCP for this repo.

Related: `r2-memory` (Titan retrieve/append), `always-push`, `flight-booking`
(must ping EFGS on out-of-WA trips).


## Titan R2Memory (every turn)

Jerome’s Titan is **read and write**. Bucket: `cleaningbutton-ai-context-us-east-1`.
Scripts: `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`). Full playbook: skill `r2-memory`.

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing prefs / past EFGS calendar decisions. Also read this
`efgs` skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

Optional gate:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_gate.py "<user message>"
```

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Do this for every meaningful EFGS turn (calendar sync, class dates, invites,
corrections). Keep this git skill updated and pushed as well.

After adding or editing this skill, refresh the Titan catalog:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_index_catalog.py
```

## Secrets (SSM)

Standing rule (2026-10-06): site logins/passwords for bots live in **AWS SSM SecureString** in **us-east-1** (IAM **grok-bot-titan**). Fetch at use only. Never ask Jerome to paste a password in chat. Never write secret values to disk, git, chat, memory, Titan, or screenshots — only SSM **path names** in this skill. If a needed path is missing, say which path and stop.

EFGS day-to-day uses Google Calendar / Gmail connectors (no EFGS-site password today). If an EFGS portal login is ever required, store paths here (e.g. `/efgs/username`, `/efgs/password`) and fetch via SSM; do not invent paths.

## Family

| | |
|---|---|
| Child | Julie Ansia — EFGS in-person student |
| Parent (calendar owner) | Jerome — jerome.ans@gmail.com |
| Wife (always invite) | Ngoc Dinh — **ngoc.h.dinh@gmail.com** (also appears as ngochdinh@gmail.com on older events) |

## In-person classes (source of truth)

Official page: https://efgseattle.org/calendar/  
Printable calendar (image/PDF):  
https://efgseattle.org/wp-content/uploads/2026/06/EFGS-School-Calendar-2026-2027-FINAL.jpg  
(PDF twin under same path with `.pdf`)

| | |
|---|---|
| School year | 2026–27 |
| Mode Jerome wants on calendar | **In-person only** (not weekday online) |
| When | Saturdays **9:15am–12:15pm** America/Los_Angeles (site typo “12:15am” = pm) |
| Where | Bertschi School, **2227 10th Ave E, Seattle, WA 98102** |
| Count | **28** Saturday mornings |
| First day | Sat **Sep 12, 2026** (back-to-school; online cohort also attends in person that day) |
| Last day | Sat **Jun 5, 2027** (end-of-year show) |

### Full in-person class calendar (2026–27) — load this every conflict check

All sessions: **Sat 09:15–12:15 America/Los_Angeles** at Bertschi School.
ISO dates (28 class days):

| # | Date | Notes |
|---|---|---|
| 1 | 2026-09-12 | First day / back-to-school |
| 2 | 2026-09-19 | |
| 3 | 2026-09-26 | Overlaps Whidbey camping block historically |
| 4 | 2026-10-03 | |
| 5 | 2026-10-17 | |
| 6 | 2026-10-24 | |
| 7 | 2026-10-31 | Halloween at school |
| 8 | 2026-11-07 | |
| 9 | 2026-11-14 | |
| 10 | 2026-11-21 | |
| 11 | 2026-12-05 | |
| 12 | 2026-12-12 | |
| 13 | 2026-12-19 | Last before winter break |
| 14 | 2027-01-23 | |
| 15 | 2027-01-30 | |
| 16 | 2027-02-06 | Chandeleur |
| 17 | 2027-02-27 | |
| 18 | 2027-03-06 | |
| 19 | 2027-03-13 | |
| 20 | 2027-03-20 | |
| 21 | 2027-03-27 | |
| 22 | 2027-04-03 | |
| 23 | 2027-04-24 | DELF exam TBD in April |
| 24 | 2027-05-01 | Pre-enrollment period starts in May |
| 25 | 2027-05-08 | |
| 26 | 2027-05-15 | |
| 27 | 2027-05-22 | |
| 28 | 2027-06-05 | Last day / end-of-year show |

Machine-check set (copy-paste):

```
2026-09-12 2026-09-19 2026-09-26 2026-10-03 2026-10-17 2026-10-24 2026-10-31
2026-11-07 2026-11-14 2026-11-21 2026-12-05 2026-12-12 2026-12-19
2027-01-23 2027-01-30 2027-02-06 2027-02-27 2027-03-06 2027-03-13 2027-03-20
2027-03-27 2027-04-03 2027-04-24 2027-05-01 2027-05-08 2027-05-15 2027-05-22
2027-06-05
```

### No-class Saturdays (do not warn as class)

2026-10-10 · 2026-11-28 · 2026-12-26 · 2027-01-02 · 2027-01-09 · 2027-01-16 ·  
2027-02-13 · 2027-02-20 · 2027-04-10 · 2027-04-17 · 2027-05-29

**Potential makeup (grey, do not treat as class unless Jerome asks):** 2027-06-06
or 2027-06-12 (PDF legend inconsistent).

### Special class-day notes

- 2026-10-31 — Halloween at school  
- 2027-02-06 — Chandeleur  
- 2027-06-05 — End of year show  
- Parent/teacher conferences are **online** (e.g. 2026-09-21–10-03, 2027-02-01–06) —
  not in-person class blocks unless Jerome asks  

### Do not put on calendar by default

- Weekday **online** sessions (Experts / Collégiens Google Classroom)  
- Teacher/staff prep (e.g. 2026-09-05)  
- Grey potential makeup days  

## Flight / travel conflict warnings (with Flight Booking)

**Goal:** Julie must not miss an in-person Saturday because the family (or Julie)
is outside Washington.

### When Flight Booking must ping EFGS

Flight Booking agent id: `51aa4255-2efc-4549-831c-3ae1092b6dbb`  
EFGS agent id: `00e87ed1-d005-4527-b29b-bfe7cccb59c2`

Whenever Flight Booking **books** (or is about to book with Jerome’s OK) any
itinerary that puts travelers **outside Washington state** during the trip window
— including typical SEA↔SJC work weeks and any non-WA destination — it must
**SendToAgent → EFGS** with:

- Confirmation / hold status
- Route + dates (outbound / return local dates)
- Who is traveling (Jerome alone vs Julie / Ngoc on the PNR)
- Whether any overnight outside WA falls on a **Friday night → Saturday morning**
  or the traveler is still outside WA on Saturday 09:15–12:15 PT

Do this **before** declaring the booking done (and ideally when presenting the
option if a conflict is already obvious).

### What EFGS does when pinged

1. Titan retrieve + read this skill’s class-date set.
2. Compute which class Saturdays (from the table above) intersect the trip:
   traveler still outside WA at **Sat 09:15 PT** (or Friday departure that returns
   after class ends).
3. **Warn Jerome in the EFGS chat** (and reply to Flight Booking) with a clear
   conflict list, e.g. “Julie has EFGS Sat 2026-09-26 9:15–12:15 at Bertschi —
   this SJC week returns Fri evening / still away Saturday → class miss risk.”
4. Suggest options: change return to Fri before evening, book a Sunday return,
   arrange alternate drop-off with Ngoc if Jerome alone, or skip that Saturday
   only if Jerome explicitly chooses.
5. Do **not** delete calendar class events unless Jerome asks.
6. Append the warning turn to Titan.

### In-WA flights

SEA / BFI / PAE / GEG / etc. entirely within Washington → **no EFGS ping**
required unless Julie is somehow kept from Saturday class for another reason
Jerome names.

## Google Calendar playbook

Connector: installed **Google Calendar** (`user-Google-calendar`), Jerome’s primary.

When Jerome asks to add EFGS classes:

1. Pull dates from the official calendar page / FINAL image or PDF (verify count = 28).
2. Create a recurring event (or matching series) titled like  
   **`Julie — EFGS in-person class`**
3. Time: 9:15–12:15 PT; location Bertschi address above; timezone `America/Los_Angeles`.
4. Invite **ngoc.h.dinh@gmail.com** (notifications on).
5. Use `EXDATE` / exclusions for break Saturdays so the series matches the yellow days.
6. Reminders: day-before + ~1 hour popup is fine.
7. Check for overlaps (e.g. Sep 26, 2026 also has Whidbey Island camping block) —
   leave class unless he says to cancel that Saturday; call out the overlap.
8. Do **not** duplicate if the 2026–27 series already exists — search/list first.

### Already done (2026-08-30)

Recurring series **Julie — EFGS in-person class** created on Jerome’s calendar  
with Ngoc invited; event id root `4qbjpem3m8oh2sqiebvoopo2t8`. Breaks excluded.
Ngoc invite was `needsAction` at creation time.

## Ongoing mandates

1. **Titan retrieve first**, then **read this skill**, on every real Jerome message.
2. After each conversation: append the turn to Titan; add durable learnings here
   (new dates, enrollment notes, supply lists, handbook links, conference
   bookings, conflicts); then **commit + push** `localGrokSkills` the same turn.
3. Mirror durable family/school facts into agent / shared user memory when useful.
4. Prefer the live EFGS calendar over this cache if they disagree; then update
   this skill and push.
5. Refresh Titan catalog (`r2_index_catalog.py`) after skill edits.
6. On every Flight Booking ping for an out-of-WA trip: check the ISO class
   set above and **warn Jerome** (and reply to Flight Booking) before the
   conflict is ignored.

## Related links

- Classes overview: https://efgseattle.org/elementor-595/  
- Parent resources: https://efgseattle.org/parents-resources/  
- Admissions: https://efgseattle.org/admissions/  

## Do not

- Add online weekday classes unless Jerome asks  
- Skip inviting Ngoc on class events  
- Invent Saturday dates without checking the official calendar  
- Leave skill edits only on disk — always commit + push  
- Ask permission to push finished skill updates  
- Skip Titan retrieve/append on real EFGS turns  
- Ignore Flight Booking out-of-WA pings or skip Saturday conflict warnings  
