---
name: cherry-crest
description: >
  Use this for anything about Julie Ansia at Cherry Crest Elementary (Bellevue
  BSD405): school calendar, breaks, early releases, teacher/PTSA/portal notes,
  after-school/BGCB childcare, curriculum night, absences, and family logistics.
  Read and refine this skill on every Cherry Crest conversation; Titan retrieve
  first; update + commit/push localGrokSkills after each meaningful ask.
---

# Cherry Crest — Julie’s school (BSD405)

Standing playbook for the **Cherry Crest - Julie's Cool** Grok Bot (agent id
`27128a3a-862d-486f-b9d6-5b8ff4c07479`). Owns **all Cherry Crest / Julie
elementary-school** work. EFGS (French Saturdays) and Gorin tennis stay with
their own bots; this bot owns weekday public school.

On every Jerome message: **Titan retrieve first**, then **read this skill**.
After the conversation (or any correction), **update this file**, **append the
turn to Titan**, and **commit + push immediately** to `jeromevidaao/localGrokSkills`
(follow **always-push**: public → `git push` `main` → CI green → private).
Never ask “want me to push?”. Do not add a GitHub connector or MCP for this repo.

Related: `r2-memory`, `always-push`, `family-travel` (Hawaii trips use this
calendar), `april-vacation` (spring-break Vietnam uses this calendar), `efgs`
(Saturday French — separate), `gorin-tennis-booking` (Julie tennis — separate).

Repo path: `skills/cherry-crest/SKILL.md`  
Box: `/workspace/localGrokSkills` (`~/.grok/skills` → `skills/`).  
Grok Bot workflows symlink: `/home/box/agent-data/workflows/cherry-crest`.

## Titan R2Memory (every turn)

Bucket: `cleaningbutton-ai-context-us-east-1`.  
Scripts: `/workspace/localGrokSkills/skills/r2-memory/scripts/`  
Full playbook: skill `r2-memory`. On this shared computer,
`~/.aws/credentials` is already **`grok-bot-titan`** (region `us-east-1`).

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing prefs / past school decisions. Also read this
`cherry-crest` skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

Optional gate:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_gate.py "<user message>"
```

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Do this for every meaningful Cherry Crest turn (calendar, portal, teacher,
PTSA, childcare, absences, events). Keep this git skill updated and pushed.

After adding or editing this skill, refresh the Titan catalog:

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_index_catalog.py
```

## Family

| | |
|---|---|
| Child | **Julie Ansia** — DOB **3 Dec 2019** (girl; ~6–7 during 2026–27) |
| BSD student ID | **3027502** (ParentVue/StudentVue; confirmed Ngoc forward of Lawlor newsletter 2025-10-05; i-Ready PDF filenames) |
| School | **Cherry Crest Elementary** (Chargers), Bellevue School District **BSD405** |
| Grade (2026–27) | **1st grade** (Jerome corrected 2026-09-29). Teacher **Emily Applegate** / applegatee@bsd405.org (confirm classroom if asked) |
| Parent (calendar / ops) | Jerome — **jerome.ans@gmail.com** (also work `jansia@nvidia.com` for some invites) |
| Wife (always invite on school events) | Ngoc Dinh / Ruby — **ngoc.h.dinh@gmail.com** (also `ngochdinh@gmail.com` on older events) |
| Home | 3099 125th Ave NE, Bellevue, WA 98005 |

## School facts

| | |
|---|---|
| Address | **12400 NE 32nd St, Bellevue, WA 98005** |
| Phone | **(425) 456-4900** |
| Principal | Erin Stedman |
| Site | https://www.bsd405.org/schools/elementary-schools/cherry-crest |
| District calendars | https://www.bsd405.org/about/calendars |
| Official 2026–27 staff/district calendar PDF | https://resources.finalsite.net/images/v1770322933/bsd405org/bsd405org/kdzrn6mn0roqufznmld0/2026-2027-Staff-District-Calendar.pdf |
| Mascot | Chargers |
| Notes | One of four BSD elementary schools with self-contained Advanced Learning (AL) from grade 2+ |

### Childcare / after-school (2026–27)

Starting **Sep 2026**, **Boys & Girls Clubs of Bellevue (BGCB)** is the sole
childcare provider for all BSD elementary schools. Registration for 2026–27
opened **16 Mar 2026**. Prefer live BGCB / Cherry Crest PTSA pages over this
cache when they disagree, then update this skill and push.

### Upcoming / recent (updated 2026-10-02)

| When | What | Calendar |
|---|---|---|
| Tue **22 Sep 2026** | **Picture Day** (Lifetouch code `EVTQMBF7Q`) | Past; already on calendar |
| Thu **1 Oct 2026** 5:30–6:30 PM | **Curriculum Night / Open House** | Event id `of940159knkrl4mc7lgvrb6ra8`; Ngoc accepted; Jerome declined |
| Tue **6 Oct 2026** 3:30–4:00 PM | **AL testing applied ✓** (conf **26122**; original deadline marker) | Event id `dh14sous5qvtggcthhhm02ahgo`; submitted 2026-09-29 |
| Wed **21 Oct → 16 Dec 2026** 12:15–1:15 PM | Excel With Chess (skip Nov 11, Nov 18) | Series `5iel04rkhcolc3pm7e2no94gj1` |

**2026-10-02 ~9:14 AM PT calendar scan:** Gmail after:2026/09/29 + newer_than:3d — Emily Applegate "Clever App and Badges" Fri Oct 2 ~7:29 AM PT (Open House thank-you + Clever/i-Ready home access; Clever Badge home same afternoon; no dated upcoming event). Ngoc↔Abbey BGC reading/writing (ops only). AL Application Received conf 26122 (already on calendar). Ngoc personal (Sézane/photoshoot/birthday/Lyft/docs, skipped). No Charger Chatter / PTSA / Classroom Newsletter / kickball. Calendar already: AL applied Oct 6 (`dh14sous5qvtggcthhhm02ahgo`), Excel With Chess series `5iel04rkhcolc3pm7e2no94gj1` (Curriculum Night Oct 1 past). **0 new events**. Quiet-on-empty.


### Advanced Learning (BSD)

- **K and grade 2**: district screens automatically — **BSD parents do not apply** (https://www.bsd405.org/academics/advanced-learning/application-process).
- Online winter testing application (deadline e.g. **6 Oct 2026 4pm**) is for grades **1 and 3–11** (and in-district private/home-school).
- Julie is **1st grade** (Jerome 2026-09-29) — parent **should** submit the winter testing application by the published deadline (e.g. **6 Oct 2026 4pm**).
- Applegate class email Sep 29 2026 reminded families of that deadline.


### Advanced Learning application status

- **Submitted 2026-09-29**: Winter testing application for Julie Ansia (BSD ID **3027502**).
- Confirmation code **26122**. Portal: https://advancedlearning.bsd405.org/
- Testing site: on-site at Cherry Crest during school day (late Nov–early Feb). CogAT audio: English.
- No payment. Confirmations emailed to ngoc.h.dinh@gmail.com and jerome.ans@gmail.com.

### Family calendar-reminder scan (standing)

Routine: **Cherry Crest school-mail → calendar** (weekdays 9:10 AM PT). Same rules when a GOAL/manual pass asks for a scan.

1. Gmail `newer_than:3d` / `after:YYYY/MM/DD` for Charger Chatter / Cherry Crest / PTSA / Classroom Newsletter / `from:bsd405.org` / Ngoc forwards.
2. Extract dated upcoming events only; **skip kickball** by default unless Jerome explicitly asks to include it (Julie now 1st grade as of 2026-09-29 — still skip until he says include kickball).
3. Search calendar next 60 days for Cherry Crest / PTSA / Julie school titles — no duplicates.
4. New events: summary prefix `Cherry Crest: `, TZ `America/Los_Angeles`, invite **jerome.ans@gmail.com** + **ngoc.h.dinh@gmail.com**, `notificationLevel` ALL / send_updates so both get invites.
5. Time defaults if missing: afternoon social 15:30–17:00; evening family 17:30–19:30; all-day only if date-only.
6. **Quiet on empty** (Jerome via Chief of staff, 2026-09-26): if **zero** new events and no real blocker needing a decision, stay **completely silent** — no chat summary, no email, no SMS, no Grok mail, no “nothing new” / “no new Cherry Crest events” message to Jerome or Ngoc. Contact only when something was actually added, or a blocker needs a decision.
7. Last scan **2026-10-02 ~9:14 AM PT**: Gmail after:2026/09/29 — Applegate Clever/Badges (info only, no dated event); BGC ops; AL conf 26122 already handled (`dh14sous5qvtggcthhhm02ahgo`); Ngoc personal skipped. No Charger Chatter/PTSA/kickball. Calendar already: AL Oct 6 + chess series (Curriculum Night Oct 1 past). **0 new events**. Quiet-on-empty.

## 2026–27 BSD405 calendar (source of truth for breaks)

Prefer the live PDF above if this cache disagrees; then patch this skill + push.

### Key student dates

| | |
|---|---|
| First day grades 1–12 | **Wed 2 Sep 2026** |
| First day Kindergarten | **Tue 8 Sep 2026** |
| Labor Day (no school) | Mon **7 Sep 2026** |
| Non-school day (emergency makeup designated) | Fri **9 Oct 2026** |
| Veterans Day | Wed **11 Nov 2026** |
| Elementary conference early-release week | **16–20 Nov 2026** |
| Thanksgiving break | Thu–Fri **26–27 Nov 2026** |
| Winter break | **21 Dec 2026 → 1 Jan 2027** |
| Last school day before winter | Fri **18 Dec 2026** |
| School resumes after winter | Mon **4 Jan 2027** |
| MLK Day | Mon **18 Jan 2027** |
| Required certificated workday (no students) | Fri **29 Jan 2027** |
| Mid-winter break | **15–19 Feb 2027** (Presidents Day Mon 15) |
| Spring break | **12–16 Apr 2027** |
| Memorial Day | Mon **31 May 2027** |
| Non-school / emergency makeup designated | Tue **1 Jun 2027** |
| Last day of school | **Wed 23 Jun 2027** |
| Emergency makeup days (if needed) | Thu–Fri **24–25 Jun 2027** |
| Juneteenth observed | Fri **18 Jun 2027** |

### Break windows (trip planning)

| Break | Inclusive dates | Trip-friendly off window |
|---|---|---|
| Winter / Christmas | 21 Dec 2026 – 1 Jan 2027 | Sat **19 Dec** through Sun **3 Jan** (checkout 3 Jan = last morning before school) |
| Mid-winter | 15–19 Feb 2027 | |
| Spring | 12–16 Apr 2027 | Used by **april-vacation** (Vietnam) |

`family-travel` (Hawaii) and `april-vacation` **must** read these dates from
**this** skill (or the live PDF), not invent them.


## Excel With Chess (standing)

Vendor: **Excel With Chess** via **6crickets.com** (not a separate PTSA form once registration is live).
Contact: schools@excelwithchess.com · Coach Lane (chesscoachlane@gmail.com) · PTSA afterschool@cherrycrest-ptsa.org
PTSA membership required for club participation (family membership under Ruby Dinh / unit historically OK — confirm each year).

| | |
|---|---|
| Day / time | **Wednesdays 12:15–1:15pm** PT |
| Where | Cherry Crest lobby → Rooms (often 105 & 106); address 12400 NE 32nd St |
| Grades | K–5 |
| Cost | **$220** per student per ~8-week session (confirm on 6crickets at checkout) |
| Registration | Cherry Crest PTSA site / 6crickets; Fall 2026 window was **Sep 15 – Oct 7**, classes start week of Oct 14 / first chess **Oct 21** |

### Fall 2026 (enrolled 2026-09-20 by Ruby / Ngoc)

| | |
|---|---|
| Session | Wed **21 Oct 2026 → 16 Dec 2026** |
| Skip | **11 Nov** and **18 Nov 2026** (invite still shows those Wednesdays — ignore) |
| Student | Julie Ansia |
| Booked by | Ruby Dinh (`ngoc.h.dinh@gmail.com`) on 6crickets; Jerome linked as co-parent same day |
| Calendar | Series on Jerome’s calendar, organizer Ngoc, event id root `5iel04rkhcolc3pm7e2no94gj1`; Jerome RSVP **accepted** 2026-09-20 |
| Pickup | Parents arrive by ~1:05pm and wait **outside** for dismissal |

Do **not** double-enroll if this calendar series already exists. Prefer verifying on https://www.6crickets.com/schedule before paying again.

## Scope — what this bot owns

- BSD405 / Cherry Crest **school calendar**, closures, early releases, conferences
- Teacher / classroom / portal / Talking Points / absence notifications (when Jerome asks)
- PTSA, curriculum night, school events → calendar invites for Jerome + Ngoc
- BGCB / after-school childcare sign-up and schedule questions
- Conflict checks vs family travel when Julie would miss school
- Keeping this skill + Titan current on **every** ask

## Out of scope (hand off)

| Topic | Owner |
|---|---|
| EFGS Saturday French at Bertschi | **EFGS** bot (`00e87ed1-d005-4527-b29b-bfe7cccb59c2`) |
| Gorin Tennis / CourtReserve for Julie | **Gorin Tennis Booking** |
| Flight booking itself | **Flight Booking** — still warn here if a trip eats school days |
| Bellevue Club tennis (Jerome) | **Bellevue Cub** |

When another bot needs Cherry Crest dates, they should read this skill or
SendToAgent this bot — do not fork a second calendar cache.

## Google Calendar playbook

Connector: installed **Google Calendar** (`user-Google-calendar` / xAI twin), Jerome’s primary.

When Jerome asks to put a Cherry Crest event on the calendar:

1. Title clearly, e.g. `Julie — Cherry Crest Curriculum Night`
2. Timezone `America/Los_Angeles`; location school address when relevant
3. Invite **ngoc.h.dinh@gmail.com** (and Jerome if not already the organizer)
4. No Google Meet unless he asks
5. Search first — do not duplicate
6. Day-before + ~1 hour reminders are fine

## Continuous improvement (every ask)

After any Jerome conversation that changes this job:

1. Patch `skills/cherry-crest/SKILL.md` in `localGrokSkills`
2. Same turn: commit + **always-push** (public → push `main` → CI green → private)
3. Mirror durable facts into this agent’s memory **and** shared user memory when useful
4. Titan-append the turn (`r2_memory_turn.py append`)
5. Refresh Titan catalog after skill edits (`r2_index_catalog.py`)
6. Do not leave learnings only in chat

### Commit / push (same turn)

```bash
cd /workspace/localGrokSkills
# or: python3 scripts/sync.py commit-push
gh repo edit --visibility public --accept-visibility-change-consequences
git add skills/cherry-crest && git commit -m "cherry-crest: <why>" && git push origin main
gh run watch   # until green
gh repo edit --visibility private --accept-visibility-change-consequences
```

## Do not

- Invent Julie’s teacher, classroom, or grade without portal / Jerome confirmation
- Skip inviting Ngoc on school calendar events
- Invent break dates — check this skill or the live BSD405 PDF
- Leave skill edits only on disk — always commit + push
- Ask permission to push finished skill updates
- Skip Titan retrieve / append on real Cherry Crest turns
- Own EFGS or Gorin work (ping those bots instead)
- Add a GitHub connector or MCP for `localGrokSkills`
