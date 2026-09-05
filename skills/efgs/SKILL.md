---
name: efgs
description: >
  Use this for Julie’s EFGS (Education Française Greater Seattle) school calendar,
  in-person Saturday classes at Bertschi, Google Calendar sync, and inviting Ngoc.
  Also read and refine this skill on every EFGS conversation.
---

# EFGS (Julie — French school)

Standing playbook for the **EFGS** bot. On every Jerome message:
**Titan retrieve first**, then **read this skill**. After the conversation (or any
correction), **update this file**, **append the turn to Titan**, and **commit +
push immediately** to `jeromevidaao/localGrokSkills` (follow **always-push**:
public → `git push` `main` → CI green → private). Never ask “want me to push?”.
Do not add a GitHub connector or MCP for this repo.

Related: `r2-memory` (Titan retrieve/append), `always-push`.


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

### Yellow Saturdays on the official calendar (all class days)

Sep 12, 19, 26 · Oct 3, 17, 24, 31 · Nov 7, 14, 21 · Dec 5, 12, 19 ·  
Jan 23, 30 · Feb 6, 27 · Mar 6, 13, 20, 27 · Apr 3, 24 · May 1, 8, 15, 22 · Jun 5

### No-class Saturdays already excluded (red / break)

Oct 10 · Nov 28 (Thanksgiving) · Dec 26 · Jan 2 · Jan 9 (Bertschi closed) ·  
Jan 16 (MLK weekend) · Feb 13 · Feb 20 (mid-winter) · Apr 10 · Apr 17 (spring) ·  
May 29 (Memorial weekend)

**Potential makeup (grey, do not add unless Jerome asks):** Jun 6 or Jun 12, 2027
(PDF legend text inconsistent).

### Special class-day notes

- Oct 31, 2026 — Halloween at school  
- Feb 6, 2027 — Chandeleur  
- Jun 5, 2027 — End of year show  
- Parent/teacher conferences are **online** (e.g. Sep 21–Oct 3, Feb 1–6) — not
  in-person class blocks unless Jerome asks  

### Do not put on calendar by default

- Weekday **online** sessions (Experts / Collégiens Google Classroom)  
- Teacher/staff prep (e.g. Sep 5, 2026)  
- Grey potential makeup days  

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
