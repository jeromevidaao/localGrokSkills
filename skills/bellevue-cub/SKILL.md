---
name: bellevue-cub
description: >
  Use this whenever Bellevue Cub books, checks, or talks about Bellevue Club
  for the Ansia family (Jerome tennis, Julie Club youth programs). Bellevue
  Club ONLY — never EFGS, Gorin, chess, Vietnamese, or Cherry Crest. Read at
  the start of every Jerome conversation; update + push after anything new.
---

# Bellevue Cub (Jerome Ansia)

**STATUS (2026-09-27):** Standing Sunday book = **6:00–7:15 PM indoor (ITC)** — **instead of** 10:30 AM. Window = **exact +7 same weekday at 7:45 PT**. Lambda `bellevueClubTennis-sunday-1800`: fire **Sun 7:40 PT**, wait to 7:45, payload `targetWeekday=sun` + `targetStart=06:00 PM`. **Sunday earlier-slot waterfall (any Sunday book, standing or arm):** if primary start is `no_open_slot` / ITC `not_open`, race earlier Sunday indoor 75-min starts closest-first (e.g. 6:00 PM → **4:45 PM** → 3:30 PM → … → 6:45 AM); never later. Sat/weekday unchanged. SES shows actual booked start. First target **Sun Oct 4**; first fire **Sun Sep 27 7:40** (that morning 6PM was USTA-blocked; waterfall would have taken 4:45 if deployed). `sunday-745` (Sun 10:30) is **DISABLED**. Keep `saturday-745` (Sat 10:30). Always indoor unless Jerome says outdoor. Browser auto-book PAUSED. Tennis Ops Sunday card is 6:00–7:15 PM via sunday-1800.

**Advance arms** (any weekday, one-off): skill `bellevue-court-arms`. Live list is Tennis / Swim → Advance books on the website and Android. Armed 2026-09-25: **Wed Oct 14 2026 6:00–7:15 PM indoor**, fires **Wed Oct 7 2026 7:40 a.m. PT** (`bellevueClubTennis-arm-20261014-1800`). Confirm with `get-schedule`; the row disappears after it fires.


Standing playbook for the **Bellevue Cub** Grok Bot. On every Jerome
message: **Titan retrieve first**, then read this skill. After the conversation,
**update this skill**, **append the turn to Titan**, and **commit + push
immediately** (always-push).

Related: `r2-memory` (Titan retrieve/append), `always-push`.

Repo: `jeromevidaao/localGrokSkills` — path `skills/bellevue-cub/SKILL.md`.
On the box: `/workspace/localGrokSkills` (`~/.grok/skills` → `skills/`).


## Scope (hard — never break)

**Bellevue Club only.** This bot answers only about Bellevue Club: member
portal, indoor/outdoor tennis courts, Club athletics/aquatics/tennis youth
programs Julie or Jerome can register for at Bellevue Club, fees, cancel
rules, and Club calendar holds tied to those bookings.

**Out of scope — do not answer; hand off or stay silent on substance:**
EFGS/French school, Gorin / CourtReserve tennis, Excel With Chess / Cherry
Crest PTSA, Vietnamese lessons (Cô Ly), school calendars, flights, or any
non–Bellevue Club activity. If Jerome asks a broad “Julie’s classes” question
here, answer **only** the Bellevue Club slice (or say she has none at the Club
that match), and do **not** list outside activities.

**Julie at Bellevue Club (as of 2026-09-25):**
- Enrolled now: **Youth 2** group swim (Fundamental Water Skills), **30 min**,
  Thu 4:30–5:00 (Session 1, through Oct 29) — **not** “>30 minutes” yet.
- **Armed plan (Session 2):** Youth aquatics registration opens
  **Wed Oct 21 2026 at 9:00 AM PT**. Plan is both Thursday classes,
  **4:30–5:00** and **5:00–5:30**. When the poll sees registration open,
  FCM says “Julie has 30+30 mins class so 60 mins of swim class in total”.
  Shown as Planned · Armed on cleaningbutton.com `#!/tennis-ops` and
  R2android Tennis / Swim. Daily trigger: `bellevueClubTennis` payload
  `swimRegistrationPoll` at 8:55 AM PT, waits until 9:00, then
  `act=swim_registration_poll` (FCM `swim_registration_open`).
  Club form enroll is not a POST in the client yet — the open ping is the
  alarm to finish both registrations if the portal does not auto-enroll.
- For **>30 min/week** Club options to register: (1) second Youth 2 group
  slot when available (Session 2 Youth reg **Oct 21 2026 9:00 a.m.**);
  (2) **private swim** via portal Private Swim Lessons / aquatics@bellevueclub.com;
  (3) Fall–Spring youth tennis/camps from member Camps & Classes brochure +
  Youth calendar — verify live durations >30 before recommending.
- Catalog: member PDF `BC-Youth-Fall-Spring-Brochure.pdf` and Issuu Youth Guide
  pages 2–3 (swim). Register: members.bellevueclub.com → Youth calendar.
- Never invent Gorin/EFGS/chess/Vietnamese as Club options.

**Julie swim Google Calendar links (2026-09-25):** Tennis / Swim Thursday dates open the existing Calendar event. DynamoDB `tennisOpsGcalEvents` pk `julie-swim-thu-1630` stores series event id `st7hcs00q4qkhst4fl1ekd20d4`, calendar id `jerome.ans@m` (the suffix in the working eventedit URL), local start `16:30` America/Los_Angeles. Each date’s instance id is `{eventId}_{UTC start}` (Oct 1 2026 4:30 PM PT → `…_20261001T233000Z`). `tennis_ops_status` puts the eventedit URL on `swim.gcalByDate`. A moved instance can be overridden with an `instances` map on that item.

## Hard rules

1. **Always indoor unless Jerome says outdoor.** Book **Indoor Tennis Courts**
   (ITC 1–6) only. Never book outdoor as a fallback, alternate, or “something
   is open.” If an outdoor reservation appears without him asking, **cancel it**.
   Standing target: **every Sunday 6:00–7:15 p.m.** indoor. Skip any date Jerome
   says skip (e.g. Sep 27 2026 6PM). Do not substitute another time if 6:00 is gone.

2. **Window:** courts book **exactly 7 days out** (same weekday +7), new day
   opens **7:45 a.m. PT**. Not 8 days / not “7+1”. Named slot → open = that
   datetime minus 7 days at 7:45 PT; EventBridge fires ~5 min early (7:40),
   handler waits to 7:45:00. Sunday 6PM inventory opens the **prior Sunday 7:45**.
   Saturday inventory opens the **prior Sunday 7:45**.

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
   then **races ITC 1–6 in parallel** for the configured slot (standing: Sunday **6:00–7:15 indoor**; Sat 10:30 if `saturday-745` is enabled)
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
   - **Google Calendar** event for that booked slot (standing Sun 6:00–7:15 PT; or Sat 10:30 if that path booked)
     at Bellevue Club, invite **jerome.ans@gmail.com** and **Ngoc Dinh
     (ngoc.h.dinh@gmail.com)**. No Google Meet. She must actually get the invite.
     If Jerome already created the event from the Lambda email button, do not
     duplicate it: add Ngoc to that event with `addedAttendees` if she is
     missing (Jerome 2026-10-09: every Bellevue tennis invite includes her).
9. **Always commit + push this skill** after any change. Follow **always-push**:
   public → `git push` `main` → CI green → private. Never ask “want me to push?”.
10. Do **not** add a GitHub connector or MCP for this repo.
11. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
   **retrieve first**, then **append/update after the turn** so Titan stays current.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook: skill `r2-memory`.
   On this shared computer, `~/.aws/credentials` is already **`grok-bot-titan`**
   (region `us-east-1`). No SSM fetch for Titan keys — just run the scripts.


## Schedule math (work backward)

Jerome names the **court day + start time** (e.g. Sunday 6:00 PM indoor). Work backward:

1. Inventory for that slot opens **exactly 7 days earlier, same weekday, at 7:45:00 PT** (not 8 days / not “7+1” / not the prior Saturday for a Sunday evening).
2. EventBridge therefore fires that **same weekday at 7:40 PT** with Input `{ "targetWeekday": "<sun|sat>", "targetStart": "<club start>" }` (end = start + 75 min unless overridden). Handler waits until 7:45:00 then races ITC 1–6.
3. Weekend evening cells stay `restrict`/`override` until the open calendar day — do not treat a Saturday fire as unlocking Sunday 6PM (+1 nextSunday math is wrong for evening).
4. Standing schedules: `sunday-1800` (6PM, **the** Sunday book) and `saturday-745` (10:30). `sunday-745` (Sun 10:30) is DISABLED — 6PM replaced it.
5. Always **verify live** on the club grid if unsure about a new slot’s open day.

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
- **Cancel policy:** club confirmation emails (Sep 2026) say cancel via
  My Reservations. Cancel **< 6 hours** ahead and the court fee is still
  charged; no-show may be **$50**. Outdoor rainouts are auto-cancelled by
  the Athletic Desk. Athletic Services: 425.688.3177 /
  athleticservices@bellevueclub.com.

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
- AWS schedules: run on Mac identity `bash /path/to/bellevue-club-tennis/scripts/ensure-schedules.sh` (or checkout) to FORCE ENABLED sunday-1800 + saturday-745; keep sunday-745 and monday-745 DISABLED.
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

**Root cause:** High demand — 10:30 indoor slot taken by other members within the first minute of opening (inventory releases exactly at 7:45:00 PT; Lambda ~7:45.000 but competition from browser users or other scripts wins the race). Not a code bug, CF challenge, login failure, or schedule miss (canary healthy, my-reservations always empty for this account). At the time, skill/repo documented "if gone, no substitute time" (Saturday still; Sunday now has earlier waterfall as of 2026-09-27).

Next target (Sep 19) also shows zero open at 10:30 today. Auto-booking stays **paused** per standing rule.

## One-off test Mon Sep 7 2026

Jerome asked for a **one-off** grab of **Sunday Sep 13 2026 10:30–11:45 indoor**
when that day opens **Monday Sep 7 at 7:45**. Routine folder
`one-off-sun-sep-13-10-30-indoor` — delete after that run. Same hard rules:
live agent through open, refresh on the dot, no resume.

## Reliability hardening 2026-09-21

Additive Lambda improvements (do **not** change sunday-1800 `targetStart=06:00 PM`):
- HTTP transient retries (429/5xx/network); **never** retry Cloudflare challenges.
- Login retries (3x) per ITC session; skip retry on CF.
- `waitUntil745Pt` spin window (~400ms) + 6 min max (tolerates 7:39 skew).
- `{"warm":true}` mode + optional Sat/Sun **7:35 PT** warm schedules (ensure-schedules; needs Mac IAM to apply).
- Skip race if My Reservations already has the target slot (duplicate-fire guard).
- Richer miss email/detail: sessionsPrimed, failedLogins, parallel outcomes.
- `ensure-schedules.sh` asserts sunday-1800 Input stays `06:00 PM`.
- **2026-09-27 Sunday earlier waterfall:** on any Sunday court day, after primary `no_open_slot`, race earlier indoor starts (not later). No EventBridge change required.

**Verify routines (Grok Bot, 7:50 AM PT):**
- Bellevue Lambda Sunday book verify — cron `50 7 * * 0`: after Sunday ~7:45, confirm CloudWatch `tennisOpsLog` for next Sunday (+7) **06:00 PM** (sunday-1800). Flag sunday-745 or monday-745 if they re-enable. Ping Jerome.
- Bellevue Lambda Saturday book verify — cron `50 7 * * 6`: confirm next Saturday 10:30 book/miss. Do not invent outcomes.

Titan still AccessDenied on `scheduler:GetSchedule` / often logs — report gaps; apply schedules from Jerome Mac via `bash scripts/ensure-schedules.sh`.

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
- Book a **later** time than requested, or any substitute on **Saturday/weekday**. Sunday may walk **earlier** indoor starts only (Lambda waterfall). Do not invent outdoor or off-grid times.
- Store the club password on disk, in git, in chat, or in Titan (fetch SSM at login)
- Assume Lambda holds a Cloudflare token that will expire — it does not; UA skip + hourly canary
- Add a Google Meet link to tennis events
- Skip inviting Ngoc on the court calendar event
- Ask whether to commit/push this skill
- Add a GitHub connector or MCP for this repo
