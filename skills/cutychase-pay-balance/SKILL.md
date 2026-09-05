---
name: cutychase-pay-balance
description: >
  Use this for Jerome Ansia's Chase Freedom Unlimited auto-pay, any Chase
  card payment from Family Checkin, Chase sign-in on the box browser, or
  after any CutyChase / CutyChase-Pay-Balance conversation. Read first
  every time Jerome talks to this bot; update and push after new learnings.
---

# CutyChase — Pay Balance

Standing playbook for the **CutyChase / CutyChase - Pay Balance** bot.
On every Jerome message: **Titan retrieve first**, then read this skill.
After the conversation (or any correction), **update this skill**,
**append the turn to Titan**, and **commit + push immediately**.

Related: `r2-memory` (Titan retrieve/append), `always-push`,
`flight-booking` (Chase Ultimate Rewards travel), CutyChase -
Rewards teammate (points combine — separate bot).

## Hard rules (never skip)

1. **Never type Chase password or 2FA.** Hand the box with
   `request_box_help` (reason `auth`, domain `chase.com`). If Chase asks
   "Let's make sure it's you" / mobile-app confirm, hand the box again
   for that step. Do not ask Jerome to paste credentials in chat.
2. **Do not scrape the Chrome cookie DB.** Session lives in this
   computer's Chrome profile. Re-auth only after Chase actually expires
   the session. Refresh loops do **not** keep Chase signed in overnight.
3. **Freedom Unlimited auto-pay** is standing authorization (2026-08-27):
   check **Mon / Wed / Fri at 9:12am PT**; if current balance is **over
   $150**, pay the **full current balance** from **Family Checkin 6022**.
   If $150 or under, **stay quiet**.
4. **Do not double-pay.** Check Payment Activity first. Skip if a
   pending / in-process payment already covers the current balance.
5. **Funding account:** Family Checkin `...6022` only for these pays.
   Never use Jerome Checkin `...6803`.
6. **Scheduled routine card is FU only** (`...6553`). Do not pay Sapphire
   Reserve or inactive cards on the cron unless Jerome explicitly says
   "pay the cards" (plural) in chat.
7. **Repeat Chase auth failure:** first time, hand the box. Same auth
   wall on a later run → **pause** the routine and tell Jerome to sign
   back in. Resume only after he is signed in and today's check is done.
8. **Always commit + push this skill:** any edit to
   `skills/cutychase-pay-balance/` must be committed and pushed to
   `jeromevidaao/localGrokSkills` the same turn — **always-push**
   (public → `git push` `main` → CI green → private). Never ask
   "want me to push?".
9. **Titan R2Memory (read + write):** every time Jerome talks to this
   bot, **retrieve first**, then **append/update after the turn** so
   Titan stays current. Bucket: `cleaningbutton-ai-context-us-east-1`.
   Full playbook: skill `r2-memory`.


## Titan R2Memory (every turn)

Scripts live at `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`).
Bucket: `cleaningbutton-ai-context-us-east-1`.

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing pay prefs / past Chase decisions. Also read this
`cutychase-pay-balance` skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Do this for every meaningful Chase-pay turn (check, pay, auth handoff,
preference). Keep the git skill updated and pushed as well (rule 8).

## Accounts (last-4 only)

| What | Last 4 | Notes |
|---|---|---|
| Freedom Unlimited (Visa) | 6553 | Auto-pay target. Autopay ON, statement balance, typically due ~6th. |
| Sapphire Reserve | 8053 | Pay only when Jerome says pay the cards (plural). |
| Inactive | 2797, 0159 | Usually $0 / closed — skip. |
| Family Checkin | 6022 | Pay-from for card pays. |
| Jerome Checkin | 6803 | Do not use for these pays. |
| Chase username (prefilled) | jerome5080 | Recognition only — never type the password. |

## Routine

- Name: **Freedom Unlimited over-$150 pay**
- Folder: `freedom-unlimited-over-150-pay`
- Cron (America/Los_Angeles): `12 9 * * 1,3,5`
- Quiet if balance ≤ $150 or already covered by pending payment.
- After a successful extra payment: tell Jerome once — amount, from-account,
  confirmation number, date, pending/posted.

## Chase browser playbook

1. Prefer the existing signed-in Chrome session on
   `https://secure.chase.com/web/auth/dashboard`.
2. If the hash login URL stays **white** after sign-in, navigate to
   `https://secure.chase.com/web/auth/dashboard` **without the hash**
   and wait ~10s for the SPA. Do not re-type credentials.
3. Shadow-DOM **mds-radio-group** / Schedule payment buttons often need
   a shadow-ref click; coordinate clicks can miss.
4. Payment form:
   - Select **Current balance** (not statement / min / other) when paying
     the over-$150 rule.
   - Pay from **Family Checkin 6022**.
   - Date = today.
   - Click **Schedule payment**, then confirm (**Pay it** / "Does
     everything look OK?").
5. Confirmation text looks like: "You've scheduled a $X payment to
   Freedom Unlimited (...6553)" plus a confirmation number and Pending.
6. Autopay for the **statement** balance (often $0 mid-cycle) does **not**
   cover a new current balance. Mid-cycle extra payment is still required
   when current > $150.
7. Close unused / crashed Chrome tabs when asked (shared box RAM). Leave
   Chrome closed when idle; cookies stay in the profile. Do not kill
   other agents' browsers.

## Session / logout reality

Chase kills sessions on purpose, including overnight. A ping every few
minutes can stretch an idle timeout; it will not beat a hard logout.
Do not hammer the site. Best path: keep the Chrome profile, hand the
box when Chase actually boots the session.

Known miss: 2026-08-28 9:12am slot skipped because the box host
restarted for an idle auto-update around 9:16am PT (caught up ~9:22).
2026-09-04 Friday run **failed** `[resource_exhausted]` — no payment
attempted that morning.

## Manual "pay the cards" (chat)

When Jerome says pay the cards (plural), check every credit card, skip
$0 and anything already covered, pay uncovered current balances from
Family Checkin 6022, same submit path. Report per-card last-4, amount,
confirmation.

## Continuous improvement

After each payment, auth handoff, or correction:

1. Patch `skills/cutychase-pay-balance/SKILL.md` in
   `/workspace/localGrokSkills` (repo `jeromevidaao/localGrokSkills`).
2. Immediately commit + push (always-push). Never leave learnings only
   in chat or only on disk.
3. Mirror durable facts into this bot's agent memory **and Titan**
   (`r2_memory_turn.py append`).

## Do not

- Type or ask for Chase password / 2FA in chat
- Scrape Chrome cookies / Login Data
- Pay from Jerome Checkin 6803
- Pay Sapphire / inactive cards on the scheduled routine
- Double-pay a covered balance
- Invent a balance when signed out
- Leave the routine firing on a repeated auth wall — pause it
