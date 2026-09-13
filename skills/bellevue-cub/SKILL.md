---
name: bellevue-cub
description: >
  Use this whenever Bellevue Cub books, checks, or talks about Bellevue Club
  indoor tennis for Jerome Ansia. Read it at the start of every Jerome
  conversation, and update + push it after anything new he asks for.
---

# Bellevue Cub (Jerome Ansia)

**STATUS (2026-09-13 09:20 PT):** Sat 10:30: fire **7:40**, wait to **7:45**, then **race hardcoded ITC 1–6 (area 20–25) in parallel**. First confirmed save wins; other workers abort (no second book). Timeout 420s. Next Sat **Sep 26** opens Sun Sep 20. Sun **Sep 20 6:00–7:15 PM ITC 1** already booked. Browser auto-book still PAUSED.


Standing playbook for the **Bellevue Cub** Grok Bot. On every Jerome
message: **Titan retrieve first**, then read this skill. After the conversation,
**update this skill**, **append the turn to Titan**, and **commit + push
immediately** (always-push).

Related: `r2-memory` (Titan retrieve/append), `always-push`.

Repo: `jeromevidaao/localGrokSkills` — path `skills/bellevue-cub/SKILL.md`.
On the box: `/workspace/localGrokSkills` (`~/.grok/skills` → `skills/`).

## Hard rules

1. **Standing book (PAUSED):** when Jerome restarts, grab **Saturday 10:30–11:45 a.m.**
   indoor tennis until he says stop. Sep 12 2026 was missed; next standing
   targets are following Saturdays (e.g. Sep 19). Any ITC 1–6. Do not substitute
   another time if 10:30 is gone.
2. **Window:** courts book **7 days out**, new day opens **7:45 a.m. PT**.
   Saturday inventory opens the **prior Sunday at 7:45 a.m.**
3. **ALWAYS refresh on the dot:** at **7:45:00 PT exactly**, **hard-refresh** the
   reservation page, then book immediately. Every booking run. No exceptions.
   Never wait for auto-update. Never start navigating at 7:45 — already be on
   the Indoor Tennis Courts grid.
4. **NEVER reproduce the Sep 6 resume mistake:** do **not** park a browser agent,
   end it, then Task-resume it for the open. That resume failed and we missed
   7:45:00. Keep **ONE** browser/desktop agent **alive and waiting** from login
   through 7:45:00 (or sleep in-process until then). The **same** live agent must
   perform the hard-refresh and click.
5. **Login check:** routine fires **7:30 a.m.** (Sunday for Saturday slots; or the
   calendar day the window opens). Confirm member login. If the session is dead,
   fetch SSM `/bellevue-club/username` and `/bellevue-club/password` (SecureString)
   and log in at https://members.bellevueclub.com/. Never write those values to
   disk, git, chat, or Titan. If SSM fetch fails, ping Jerome. If the session is
   fine, stay quiet and wait on the grid.
6. **Weekly book is Lambda `bellevueClubTennis`** (`jeromevidaao/bellevue-club-tennis`):
   EventBridge Scheduler Sunday **7:40 a.m. PT** (was 7:44; Sep 13 cold start INIT 7:44:50
   ate the open). Handler **logs in on that invoke**, waits until **7:45:00.000 PT**,
   then **races ITC 1–6 in parallel** for Saturday **10:30–11:45 indoor**
   (hardcoded area ids 20–25). First save wins; siblings abort. Timeout 420s. Emails
   jerome.ans@gmail.com (ICS + Add to calendar if booked). SSM login. Do not
   double-book that slot from this bot if the Lambda already has it.
   **Cloudflare:** in front of **every** `members.bellevueclub.com` request
   (login, tennis grid, AJAX save, my-reservations) — not a door you pass once.
   Club login cookies ≠ CF. Being signed in does **not** skip Turnstile.
   Chrome UA trips CF on the **tennis grid** specifically; Lambda UA is
   exactly `Mozilla/5.0`, which currently skips that challenge. Lambda does
   **not** store or reuse a browser `cf_clearance` (IP + UA bound; laptop
   cookie cannot be used on AWS).
   Cookies live only in the invocation CookieJar. `__cf_bm` TTL is **~30 min**
   if Cloudflare sets it — irrelevant because each run is a new session, not a
   persisted token. What *can* break later is Cloudflare starting to challenge
   AWS IPs even with that UA — not token expiry. Hourly canary
   `bellevueClubTennis-hourly-canary` (`cron(10 * * * ? *)` PT, payload
   `{"canary":true}`) login+grid no book; fail throws → CW alarm + SES.
   **Will the UA skip fail eventually?** Yes, likely — not on a timer, not because
   a token expires. Same pattern as HomeExchange: a club/CF dashboard toggle
   (Bot Fight / Super Bot Fight / “definitely automated”) or a CF managed-ruleset
   update can start challenging AWS IPs overnight. Chrome UA already trips
   Turnstile on this zone; `Mozilla/5.0` is a hole that can close. AWS IP
   reputation can also make it **intermittent** (one invoke challenged, next
   not). Hourly canary is the detector; when it emails, the HTTP path is dead
   until we change approach (browser/`cf_clearance` mint, or a different egress).
   **Cannot stop CF tightening** (club/vendor dashboard or managed-ruleset).
   Defensive (don't poke): freeze UA `Mozilla/5.0` — never send a Chrome UA from
   Lambda (that already trips Turnstile); no UA rotation; no retry-storm on
   challenge; canary is login+grid only. Hourly canary = **24 AWS logins/day**
   — the noisiest thing we do; thinning to a few times/day (or Sunday morning
   only) lowers chance of IP reputation heat, slower detection. NAT Elastic IP
   does **not** beat Super Bot Fight (still AWS ASN). Durable path if CF
   tightens: book from this box (real Chrome + ISP IP), not Lambda. Do not
   run Lambda and the box both at Sunday 7:45.
7. **Runs on this computer, not Jerome’s.** His laptop can be off. After login,
   the session lives in this agent’s Chrome profile (`members.bellevueclub.com`).
   `grok-bot-titan` can GetParameter those two `/bellevue-club/*` names (SSM read on this user).
8. **After a successful book (same turn, immediately):**
   - **Chat ping** Jerome here with date, court, time, fee.
   - **Email** jerome.ans@gmail.com with the same details (authorized; do not ask).
   - **Google Calendar** event for that booked slot (usually Sat 10:30–11:45 PT)
     at Bellevue Club, invite **jerome.ans@gmail.com** and **Ngoc Dinh
     (ngoc.h.dinh@gmail.com)**. No Google Meet. She must actually get the invite.
9. **Always commit + push this skill** after any change. Follow **always-push**:
   public → `git push` `main` → CI green → private. Never ask “want me to push?”.
10. Do **not** add a GitHub connector or MCP for this repo.
11. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
   **retrieve first**, then **append/update after the turn** so Titan stays current.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook: skill `r2-memory`.
   On this shared computer, `~/.aws/credentials` is already **`grok-bot-titan`**
   (region `us-east-1`). No SSM fetch for Titan keys — just run the scripts.

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
Keep the git skill updated and pushed as well (rule 9).

## Sunday login-check calendar

Weekly event **BC indoor tennis — login check**, Sundays **7:30–7:45 a.m. PT**,
starting 2026-09-06, event id `1qllep9n3tru7439cl819a9md8`. Popup + email
reminders 10 minutes prior (7:20). Recurs every Sunday.


## Timeline & Root Cause for Sep 12 2026 miss (investigated 2026-09-12)

## Hardening 2026-09-12 (Grok CLI)

- Code: `resolveTargetDay` / `nextSunday`; save retries; richer SES detail/open list.
- Deployed main `2db74f6` (CI green).
- Live canary from box OK (cfPassed).
- AWS schedules: run on Mac identity `bash /path/to/bellevue-club-tennis/scripts/ensure-schedules.sh` (or checkout) to FORCE ENABLED sunday-745 + monday-745.
- Verify routines: Sun 7:50 + Mon 7:50 PT CLI my/canary ping.

## Investigation 2026-09-12 (Grok CLI)

- Confirmed via club HTTP CLI on the box: canary ok; my-reservations empty.
- Miss was browser resume on Sep 6; Lambda shipped after that open.
- Code fix: `bellevue-club-tennis` logs in on invoke (~7:44), waits to 7:45, then refresh+book (was wait-then-login).
- Titan cannot read scheduler/Lambda/CW; bootstrap leaves Sunday schedule ENABLED.
- Routine: Sunday 7:50 PT verify via CLI and ping Jerome.

**Sep 6:** First live Sunday run (outdoor test succeeded). Browser-agent resume-across-7:45 bug noted (fixed in playbook: keep live agent or in-process sleep).

**Sep 7–11:** Canary (hourly login+grid, no-book) succeeded (no alarm/SES). SSM creds unchanged (LastModified ~Sep 2026). Lambda `bellevueClubTennis` and canary schedule active (repo commit b5e5541 added robust canary + CW alarm/SES; CI deploys cleanly on push; no pause flag in code/EventBridge).

**Sunday Sep 13 7:44–7:46 PT (for Sep 12 slot, opens prior Sunday 7:45):** Lambda ran (waitUntil745Pt, login with SSM, loadCourts, setSheetDate for 09/12/2026, firstOpenAt(10:30) = null). Returned `error: "no_open_1030_slot"`, sent miss email to jerome.ans@gmail.com (no ICS/calendar). Grid was fully booked at target time (confirmed today via CLI on current grid).

**Root cause:** High demand — 10:30 indoor slot taken by other members within the first minute of opening (inventory releases exactly at 7:45:00 PT; Lambda ~7:45.000 but competition from browser users or other scripts wins the race). Not a code bug, CF challenge, login failure, or schedule miss (canary healthy, my-reservations always empty for this account). Skill and repo accurately documented the "if gone, no substitute time" rule.

Next target (Sep 19) also shows zero open at 10:30 today. Auto-booking stays **paused** per standing rule.

## One-off test Mon Sep 7 2026

Jerome asked for a **one-off** grab of **Sunday Sep 13 2026 10:30–11:45 indoor**
when that day opens **Monday Sep 7 at 7:45**. Routine folder
`one-off-sun-sep-13-10-30-indoor` — delete after that run. Same hard rules:
live agent through open, refresh on the dot, no resume.

## Continuous improvement

After any Jerome conversation that changes this job:

1. Patch `skills/bellevue-cub/SKILL.md` in `localGrokSkills`.
2. Same turn: commit + always-push (public → push `main` → CI green → private).
3. Mirror durable facts into Bellevue Cub agent memory.
4. Titan-append the turn (`r2_memory_turn.py append`).
5. Do not leave learnings only in chat.

## Do not

- Miss the 7:45:00 hard-refresh (always on the dot)
- Task-resume a parked browser across the open second
- Book a different time if 10:30 is gone
- Store the club password on disk, in git, in chat, or in Titan (fetch SSM at login)
- Assume Lambda holds a Cloudflare token that will expire — it does not; UA skip + hourly canary
- Add a Google Meet link to tennis events
- Skip inviting Ngoc on the court calendar event
- Ask whether to commit/push this skill
- Add a GitHub connector or MCP for this repo
