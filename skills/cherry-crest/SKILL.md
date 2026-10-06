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

Related: `julie-homework` (CogAT practice PDFs via the grok CLI), `r2-memory`, `always-push`, `family-travel` (Hawaii trips use this
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

### Upcoming / recent (updated 2026-10-06)

| When | What | Calendar |
|---|---|---|
| Tue **22 Sep 2026** | **Picture Day** (Lifetouch code `EVTQMBF7Q`) | Past; already on calendar |
| Thu **1 Oct 2026** 5:30–6:30 PM | **Curriculum Night / Open House** | Event id `of940159knkrl4mc7lgvrb6ra8`; Ngoc accepted; Jerome declined |
| Mon **5–Fri 9 Oct 2026** | **Walk & Roll to School** week (Bellevue SchoolPool) | Event id `4k5k3okvte2m21nfml9q39s8ig` (from Oct Charger Beat) |
| Tue **6 Oct 2026** 3:30–4:00 PM | **AL testing applied ✓** (conf **26122**; original deadline marker) | Event id `dh14sous5qvtggcthhhm02ahgo`; submitted 2026-09-29 |
| Tue **6 Oct 2026** 6:00–7:30 PM | **PTSA General Meeting** (cafeteria, with Mrs. Stedman) | Event id `hj6703m2hne75qg14g5r398os0` |
| Fri **9 Oct 2026** | **No school** (non-student / emergency makeup day) | Event id `hbu3it2epmnb1k574oc3mah1j0` |
| Wed **21 Oct → 16 Dec 2026** 12:15–1:15 PM | Excel With Chess (skip Nov 11, Nov 18) | Series `5iel04rkhcolc3pm7e2no94gj1` |
| Wed **21 Oct 2026** 6:30–8:30 PM | **Bridle Trail Community Meeting** (cafeteria) | Event id `kverit2m55mmpe6obf2ck3a3f0` |
| Fri **30 Oct 2026** 5:30–7:30 PM | **PTSA School Dance** (time assumed evening family) | Event id `srh713v05ek8vct1ful4hus9cs` |
| Wed **5 Nov 2026** | **PTSA Giving Month raffle cutoff** | Event id `pqtfc5qsn2t3i5ed6q0bjv48uo` |
| Fri **6 Nov 2026** 9:00–10:00 AM | **Principal Coffee** (Teams) | Event id `do2klc16eg7jko79rmq1bssnfg` |
| Wed **11 Nov 2026** | **Veterans Day — no school** | Event id `2dvdv5uj3803eh3h435grher2g` |
| Fri **13 Nov 2026** 5:30–7:30 PM | **PTSA Family Engineering Night** (time assumed) | Event id `s5u5o8e3982misbh8echfrc85g` |
| Mon **16–Fri 20 Nov 2026** | **Conferences week — 12:15 dismissal** | Event id `c2t0q7743iccu66j9jd2lrqrl4` |
| Thu–Fri **26–27 Nov 2026** | **Thanksgiving break — no school** | Event id `s4tsuqqgkgsu3scbtt9oa2guro` |

**2026-10-05 ~9:43 AM PT:** October Charger Beat (Erin Stedman / ParentVue, Smore https://app.smore.com/n/n62vj) fully calendared — Walk & Roll, PTSA General Meeting, no-school Oct 9, Bridle Trail, School Dance, Giving Month cutoff, Principal Coffee Nov 6, Veterans Day, Family Engineering Night, conferences week, Thanksgiving. Kickball skipped.

**2026-10-06 ~9:16 AM PT** manual scan: Gmail after:2026/10/03 found Erin Stedman **Cherry Crest October Newsletter** (Mon Oct 5, msg `1a10cf16269efa8d`, Smore https://app.smore.com/n/n62vj). Dated events were **ALREADY created 2026-10-05 (~4:43 PM UTC)**: Walk & Roll Oct 5–9 (`4k5k3okvte2m21nfml9q39s8ig`), PTSA General Meeting Oct 6 6–7:30pm (`hj6703m2hne75qg14g5r398os0`), No school Oct 9 (`hbu3it2epmnb1k574oc3mah1j0`), Bridle Trail Oct 21 6:30–8:30 (`kverit2m55mmpe6obf2ck3a3f0`), PTSA Dance Oct 30 5:30–7:30 assumed (`srh713v05ek8vct1ful4hus9cs`), Giving Month raffle cutoff Nov 5 (`pqtfc5qsn2t3i5ed6q0bjv48uo`), Principal Coffee Nov 6 9–10am (`do2klc16eg7jko79rmq1bssnfg`), Veterans Day Nov 11 (`2dvdv5uj3803eh3h435grher2g`), Family Engineering Night Nov 13 5:30–7:30 assumed (`s5u5o8e3982misbh8echfrc85g`), Conferences week Nov 16–20 (`c2t0q7743iccu66j9jd2lrqrl4`), Thanksgiving Nov 26–27 (`s4tsuqqgkgsu3scbtt9oa2guro`). Also existing: AL Oct 6 (`dh14sous5qvtggcthhhm02ahgo`), Excel With Chess series. This run created **0** new events. Skipped: kickball (family preference), Grok empty-scan notify, practice-packet self-emails Oct 3, no Applegate/Ngoc school forwards, no Charger Chatter separate from October newsletter. Weekday school-mail routine remains **OFF** (Jerome cancelled 2026-10-03). Keep quiet-on-empty for future automated runs; this was a manual GOAL with required summary.

**2026-10-02 ~9:14 AM PT calendar scan:** Gmail after:2026/09/29 — Applegate Clever (info only), Ngoc BGC ops, AL receipt already on calendar. **0 new**.

**2026-10-03 scan:** Applegate Clever (info only), Ngoc personal invites skipped. Zero new events. Kickball still skipped.

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
7. Last scan **2026-10-06 ~9:16 AM PT** (manual GOAL): Erin Stedman Cherry Crest October Newsletter Mon Oct 5 (msg `1a10cf16269efa8d`, Smore https://app.smore.com/n/n62vj) — all dated events already created 2026-10-05 (~4:43 PM UTC) with ids listed under Upcoming/recent. Also existing: AL Oct 6, Excel With Chess. **0 new**. Skipped: kickball (family preference), Grok empty-scan notify, practice-packet self-emails Oct 3, no Applegate/Ngoc school forwards, no separate Charger Chatter. Weekday school-mail routine remains **OFF** (Jerome cancelled 2026-10-03). Quiet-on-empty for future automated runs; this manual pass required a summary.
8. **Quiet on empty** still applies when there is also no new Classroom Newsletter packet (see below). A packet that was emailed is a real result: tell Jerome. Do not stay silent after sending one.

## Classroom Newsletter practice packets (standing, from 2026-10-03)

Jerome asked (via Grok Bot, 2026-10-03) that each **Classroom Newsletter** from **Emily Applegate** (`applegatee@bsd405.org`) become about **10 pages** of short, fun practice for Julie and be **emailed as a PDF** to **jerome.ans@gmail.com** and **ngoc.h.dinh@gmail.com**.

This bot owns that from the next newsletter onward. The weekday **Cherry Crest school-mail → calendar** routine (9:10 AM PT) is the only hook. Grok Bot dropped their separate weekday check on 2026-10-03. The **2026-10-03 CogAT packet** (below) is the baseline the next packet must improve on. Do not rebuild it and do not resend it. The Sept 11 heart-word / addition PDF is rejected. Do **not** resend `/workspace/julie-applegate-2026-09-11-dense.pdf`.

**Each new packet must be better than the last** (Jerome, 2026-10-03): reuse and reinforce exercises from earlier packets, and fold in learning gaps Jerome names as he notices them. Do not start from scratch each week.

**Question format Jerome wants** (corrected 2026-10-03, after he rejected the heart-word / addition worksheet instructions as bad): practice must be friendly to a 6-year-old and use the **same question format as Bellevue CogAT**, not a reading worksheet.

BSD CogAT for grade 1 is **Form 7 or 8, Level 8**, computer-based, picture items, audio-led. Source: https://www.bsd405.org/academics/advanced-learning/tests and the district sample PDF (CogAT Forms 7 and 8, Levels 5/6–8). For grades K–2 BSD does **not** use Sentence Completion. Do not use word analogies or sentence completion.

Each page is one of these formats, with several big picture items (not a blank page, not tiny print):

- Picture Analogies: two pictures that go together, then choose the pair that goes together the same way.
- Picture Classification: three pictures that are alike, then choose the one that belongs.
- Number Analogies: a 2×2 picture grid of amounts, bottom-right missing.
- Number Puzzles: two trains; choose what makes the second train carry the same number as the first.
- Number Series: bead strings in a pattern; choose the string that comes next.
- Figure Matrices: a 2×2 grid of shapes, bottom-right missing.
- Paper Folding: paper folded and punched; choose what it looks like opened. Keep it to one fold.
- Figure Classification: three shapes that are alike, then choose the one that belongs.

One short line at the top is enough (“Which pair matches?”). Pictures can use objects from that week’s newsletter, but the question shape stays CogAT. Original drawings only. Do not copy Riverside’s sample art.

**No name line. No date line.**

When a newsletter is new (not the Sept 11 issue, and not already packeted):

1. Read the full Classroom Newsletter (body and any attached PDF). Also read this skill's packet log and any learning gaps Jerome has named.
2. Build about 10 pages in the CogAT formats above, friendly to a 6-year-old: large outline pictures, almost no reading, one format per page, several items so the page is not empty. Better than the last packet, and use any named gap. Do not go back to heart-word grids, sound-it-out rows, sentence copy lines, or a big addition block. No name. No date.
3. **Print rule (Jerome, 2026-10-03):** every practice PDF is **black and white only** and light on ink, even with the denser pages. No large solid black areas (no filled bars, big silhouettes, or heavy borders). **No colored fills and no gray table fills.** Use outline grids, dotted lines, and small text. Do not ship a color or ink-heavy page.
4. Make a PDF and email it to both parents. This send is standing approval from Jerome (2026-10-03): send the packet, do not leave it as a draft-only card. Subject should name the newsletter date, e.g. `Julie practice — Classroom Newsletter <date>`.
5. Do not send a second packet for the same newsletter. After each send, record in this skill: newsletter date, what each page practiced, and what to reinforce next time.
6. When Jerome names a learning gap, add it to the **Learning gaps** list below the same day, and use it on the next packet. Remove or mark a gap only when he says she has it, or after it has been practiced and he does not bring it up again.
7. Quiet-on-empty does **not** cover a sent packet. Tell Jerome the packet went out (date, page count, both recipients) and name which earlier skills you reused and which gaps you folded in.

### Learning gaps (Jerome names these)

None recorded yet (2026-10-03).

### Packets sent

| Packet | When | Notes |
|---|---|---|
| Sept 11, 2026 Classroom Newsletter (heart-word / addition) | Rejected | File `/workspace/julie-applegate-2026-09-11-dense.pdf`. Jerome rejected this format. **Do not resend.** |
| **CogAT practice Oct 3, 2026** | Emailed **2026-10-03 4:32 PM PT** | `/workspace/julie-cogat-practice-2026-10-03.pdf` (10 letter pages, ~77 KB). From **jerome.ans@gmail.com** to **jerome.ans@gmail.com** and **ngoc.h.dinh@gmail.com**. Subject: `Julie practice — CogAT Oct 3`. Gmail message id `1a1041cdb7191a00`, thread `1a1041cc0832941c`. **Do not resend.** This is the baseline. |

### 2026-10-03 CogAT packet — what each page practiced

Black-and-white outlines only. No name line. No date line. No sentence completion, no word analogies, no heart words, no addition.

| Page | Format | What Julie practiced |
|---|---|---|
| 1 | Picture analogies | Stem is one pair; choices are pairs. Big sun → small sun (answer: big ball → small ball). Cloud → umbrella (answer: sun → hat). |
| 2 | Picture analogies | Same pair shape. Tree → leaf (answer: flower → leaf). Small fish → big fish (answer: small moon → big moon). |
| 3 | Picture classification | Three alike, then four choices. Animals (cat, bird, fish → dog). Sky (sun, cloud, moon → star). Clothes (hat, sock, boot → shirt). |
| 4 | Number analogies | 2×2 amounts, bottom-right missing. Add one (2→3 circles/triangles; 1→2 hearts/diamonds). Take away half (4→2 dots/squares). |
| 5 | Number puzzles | Two trains. Make the totals match (2+1 vs 1+?; 3+1 vs 2+?; 2+2 vs 3+?). |
| 6 | Number series | Outline bead strings only. Count up by one; same count, new shape; add one square each time. |
| 7 | Figure matrices | 2×2 shapes, bottom-right missing. Big → small; flip upside down; right-hand shape stays a heart. |
| 8–9 | Paper folding | One fold, one hole. Pick the opened paper (holes mirror across the fold). |
| 10 | Figure classification | Three triangles → a triangle. Three round shapes → an oval. Three pointy shapes → a triangle. |

Next packet: reuse big/small and “which group” in a slightly harder form. Still no name, no date, no heart-word page, no addition page.

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
- Classroom Newsletter from Applegate → ~10-page CogAT-format practice PDF for a 6-year-old (picture analogies, classification, number analogies, number puzzles, number series, figure matrices, paper folding, figure classification), black and white, no name or date, emailed to Jerome and Ngoc (Sept 11 2026 heart-word packet was rejected as the wrong format)
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
