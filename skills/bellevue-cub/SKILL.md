---
name: bellevue-cub
description: >
  Use this whenever Bellevue Cub books, checks, or talks about Bellevue Club
  indoor tennis for Jerome Ansia. Read it at the start of every Jerome
  conversation, and update + push it after anything new he asks for.
---

# Bellevue Cub (Jerome Ansia)

Standing playbook for the **Bellevue Cub** Grok Bot. On every Jerome
message: **Titan retrieve first**, then read this skill. After the conversation,
**update this skill**, **append the turn to Titan**, and **commit + push
immediately** (always-push).

Related: `r2-memory` (Titan retrieve/append), `always-push`.

Repo: `jeromevidaao/localGrokSkills` — path `skills/bellevue-cub/SKILL.md`.
On the box: `/workspace/localGrokSkills` (`~/.grok/skills` → `skills/`).

## Hard rules

1. **Standing book:** keep grabbing **Saturday 10:30–11:45 a.m.** indoor tennis
   at Bellevue Club until Jerome says stop. First Saturday is **2026-09-12**.
   Any indoor court (ITC 1–6) is fine. Do not substitute another time if 10:30
   is gone.
2. **Window:** courts book **7 days out**, new day opens **7:45 a.m. PT**.
   Saturday inventory therefore opens the **prior Sunday at 7:45 a.m.**
3. **Sunday timing:** routine `saturday-10-30-indoor-tennis` fires **7:30 a.m.
   Sundays**. First: confirm member login. If the session is dead, **ping Jerome
   immediately** and hand the desktop for sign-in (never type his password).
   If login is fine, stay quiet and wait. At **7:45:00 exactly**, hard-refresh
   the reservation page, then book 10:30 on the first open indoor court.
4. **Runs on this computer, not Jerome’s.** His laptop can be off. Login lives
   in this agent’s Chrome profile (`members.bellevueclub.com`).
5. **After a successful book:** Google Calendar event Saturday 10:30–11:45 PT,
   location Bellevue Club, invite **jerome.ans@gmail.com** and **Ngoc Dinh
   (ngoc.h.dinh@gmail.com)**. No Google Meet. Then message Jerome with date,
   court, time, fee, and that Ngoc was invited.
6. **Always commit + push this skill** after any change. Follow **always-push**:
   public → `git push` `main` → CI green → private. Never ask “want me to push?”.
7. Do **not** add a GitHub connector or MCP for this repo.
8. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
   **retrieve first**, then **append/update after the turn** so Titan stays current.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook: skill `r2-memory`.

## People

| Who | Email |
|---|---|
| Jerome Ansia (member, billed) | jerome.ans@gmail.com |
| Ngoc Dinh (wife, also Ruby) | ngoc.h.dinh@gmail.com |

Booking For on the club form: **Ansia, Jerome**.

## Club facts

- Portal: https://members.bellevueclub.com/
- Indoor grid: https://members.bellevueclub.com/group/pages/tennis-court-reservations
  (dropdown **Indoor Tennis Courts**)
- Confirm: https://members.bellevueclub.com/group/pages/my-reservations
- Athletic Fee Schedule (effective Jan 1, 2026): indoor **$18.50** / 75 min
  (split among players, plus tax); outdoor $12.50; pickleball outdoor $9;
  ball machine $28.50/hr (includes court); adult guest pass $23; child 12 and
  under $18.
- Slots are **75 minutes**. Starts rotate :00 / :15 / :30 / :45.
  Weekdays: first 5:30 a.m., last start 8:30 p.m. (ends 9:45).
  Saturday: first 6:45 a.m., last start 8:30 p.m.
  Sunday: first 6:45 a.m., last start 7:15 p.m.
- **Cancel policy:** member site (as of Sep 2026) has no published cutoff or
  late-cancel/no-show fee. FAQ only: cancel via Reservations → My Reservations.
  Athletic Services: 425.688.3177 / athleticservices@bellevueclub.com.
  Do not invent a 24-hour rule.

## How the grid actually works

- Date tabs: 7 days (today through today+6). Tab highlight can lag — verify
  the day with a screenshot. The date textbox alone does **not** reload the grid.
- Open cells: `td.data-col.slot.open` (white + small calendar icon). Inner div
  has **zero height** — click the **center of the `td`**, not the icon.
- 10:30 a.m. is row `t4`. Columns c0–c5 = ITC 1–6.
- Clicking an open cell opens a **full-page form** (not a modal) with a **red
  2-minute countdown**. If it hits zero, back to the grid. Hit **Save** fast.
- Defaults: Reservation Type = Court Reservation; From = slot start; For = 75;
  Booking For = Ansia, Jerome. Leave those. Never click Back unless aborting.
  No price/payment step — it bills the member account.
- After Save, confirm on My Reservations before treating it as booked.
- Do not double-book if that Saturday 10:30 is already on the account.


## Titan R2Memory (every turn)

Scripts live at `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`).

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing prefs / past tennis decisions. Also read this
`bellevue-cub` skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Do this for every meaningful tennis turn (book, login check, cancel, preference).
Keep the git skill updated and pushed as well (rule 6).

## Sunday login-check calendar

Weekly event **BC indoor tennis — login check**, Sundays **7:30–7:45 a.m. PT**,
starting 2026-09-06, event id `1qllep9n3tru7439cl819a9md8`. Popup + email
reminders 10 minutes prior (7:20). Recurs every Sunday.

## Continuous improvement

After any Jerome conversation that changes this job:

1. Patch `skills/bellevue-cub/SKILL.md` in `localGrokSkills`.
2. Same turn: commit + always-push (public → push `main` → CI green → private).
3. Mirror durable facts into Bellevue Cub agent memory.
4. Titan-append the turn (`r2_memory_turn.py append`).
5. Do not leave learnings only in chat.

## Do not

- Book a different time if 10:30 is gone
- Type Jerome’s club password
- Add a Google Meet link to tennis events
- Skip inviting Ngoc on the Saturday court event
- Ask whether to commit/push this skill
- Add a GitHub connector or MCP for this repo
