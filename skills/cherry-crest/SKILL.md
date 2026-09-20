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
| School | **Cherry Crest Elementary** (Chargers), Bellevue School District **BSD405** |
| Grade (2026–27) | Likely **1st** (confirm with Jerome / portal — do not invent teacher or classroom) |
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

### Upcoming (as of skill create 2026-09-20)

| When | What |
|---|---|
| Thu **1 Oct 2026** 5:30–6:30 PM | **Cherry Crest Elementary Curriculum Night** |
| Sep–Oct 2026 | District curriculum nights across schools |

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
