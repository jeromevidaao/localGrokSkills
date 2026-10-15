---
name: cutychase-pay-balance
description: >
  Use this for Jerome Ansia's Chase Freedom Unlimited auto-pay, any Chase
  card payment from Family Checkin, Chase sign-in on the box browser, or
  after any CutyChase / CutyChase-Pay-Balance conversation. Read first
  every time Jerome talks to this bot; update and push after new learnings.
---

> **Owning bot: Chase** (merged; id `220daf8a-5395-407b-b48e-20b0d773ce9f`). The **CutyChase** / **CutyChase - Pay Balance** agent is deprecated — use **Chase**. All operational pay / Zelle rules below still apply on the surviving bot.

# CutyChase — Pay Balance

Standing playbook for the **CutyChase / CutyChase - Pay Balance** bot.
On every Jerome message: **Titan retrieve first**, then read this skill.
After the conversation (or any correction), **update this skill**,
**append the turn to Titan**, and **commit + push immediately**.

Related: `r2-memory` (Titan retrieve/append), `always-push`,
`flight-booking` (Chase Ultimate Rewards travel), `cutychase-rewards`
(UR / points — same owning bot **Chase**).

## Login: Chrome autofill first (Jerome, 2026-10-12)

The working Chase login is saved in the box Chrome autofill / password manager.
When signed out: click Username, pick the plain `jerome5080` autofill entry (NEVER the
longer entry with extra characters appended), let Chrome fill the saved password,
uncheck Use token, click Sign in. Mobile-app confirm if asked. Fall back to SSM
`/chase/username` + `/chase/password` only if autofill is missing; SSM password was
stale as of 2026-10-06 (v1), so stop after one SSM rejection and hand Jerome the box.

## Hard rules (never skip)

1. **Login (ALWAYS SSM — confirmed 2026-10-01):** prefer the existing
   Chrome session. If Chase is signed out, **always** fetch AWS SSM
   SecureStrings `/chase/username` and `/chase/password` (us-east-1,
   grok-bot-titan) and autofill/type them at https://secure.chase.com/.
   Uncheck **Use token** before Sign in. **Do not** use Secure Form /
   RequestUserForm / in-chat password cards for Chase, and never ask
   Jerome to paste the password. Never write SSM values to disk, git,
   chat, or Titan. If SSM fetch fails, ping Jerome. Automate SSM login without asking him first; only ping when the Android app approval step actually appears. **Never type 2FA.**
   If Chase asks "Let's make sure it's you" / mobile-app confirm:
   **always** click **Confirm using our mobile app** (never Prefer
   token/OTP unless he asks) to send the push, then **ping Jerome once in
   chat** to open his **Android Chase app** and approve. Prefer that chat
   ping over a long desktop handoff. Passwordless is optional only when it
   reliably sends an app push; if it errors, fall back to SSM + Sign in +
   mobile-app confirm. Still use `request_box_help` if he needs the box
   screen for a stuck UI — not for typing the password.
2. **Do not scrape the Chrome cookie DB.** Session lives in this
   computer's Chrome profile. Re-auth only after Chase actually expires
   the session. Refresh loops do **not** keep Chase signed in overnight.
3. **Freedom Unlimited + Sapphire Reserve auto-pay** (FU since 2026-08-27;
   Reserve added 2026-09-11): check **Mon + Thu at 9:12am PT** (twice weekly; changed 2026-10-01 from Mon/Wed/Fri). For
   **each** of Freedom Unlimited (...6553) and Sapphire Reserve (...8053),
   if that card's current balance is **over $150**, pay the **full current
   balance** from **Family Checkin 6022**. If $150 or under on a card, skip
   that card. Stay quiet only if **neither** needed a payment.
4. **Do not double-pay.** Check Payment Activity first. Skip if a
   pending / in-process payment already covers the current balance.
5. **Funding account:** Family Checkin `...6022` only for these pays.
   Never use Jerome Checkin `...6803`.
6. **Scheduled routine cards:** Freedom Unlimited (`...6553`) and Sapphire
   Reserve (`...8053`) only. Skip inactive cards. Manual "pay the cards"
   in chat can still cover any uncovered balances.
7. **Repeat Chase auth failure:** first time, SSM login + mobile-app
   push, then chat-ping Jerome to open **Android Chase app**. Same 2FA /
   auth wall still blocking on a later scheduled run → **pause** the
   routine and tell Jerome. Resume only after he is signed in and
   today's check is done.
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
On this shared computer, `~/.aws/credentials` is already **grok-bot-titan**,
region `us-east-1`. Run Titan scripts directly (no SSM for Titan keys).
`grok-bot-titan` may GetParameter `/chase/username` + `/chase/password`
(and the Bellevue Club pair) when the Chase session is dead.
If `aws` is missing on PATH, use `/tmp/awscli-venv/bin/aws` (venv install)
or restore the CLI before SSM login. Site error page after login often
clears by opening `https://secure.chase.com/web/auth/dashboard` with no hash.

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


## Chase mobile 2FA (Android) — ALWAYS

**Standing rule (confirmed 2026-10-01, keep forever):** for every Chase
identity check / 2FA / "Let's make sure it's you", **always** use the
**Android Chase app** approval path. Prefer **Confirm using our mobile app**
(or Passwordless sign in when that sends an app push). Do **not** use Use
token / OTP token entry, SMS codes, or long desktop handoffs unless Jerome
explicitly asks for a different method.

After triggering the push: **SendToUser once** — ask him to open his
**Android Chase app** and approve. Do not invent balances while waiting.
After he confirms in chat (or the dashboard appears), finish the task
(Zelle / pay / combine).

## Accounts (last-4 only)

| What | Last 4 | Notes |
|---|---|---|
| Freedom Unlimited (Visa) | 6553 | Auto-pay target. Autopay ON, statement balance, typically due ~6th. |
| Sapphire Reserve | 8053 | Same over-$150 Mon/Wed/Fri auto-pay as FU (since 2026-09-11). |
| Inactive | 2797, 0159 | Usually $0 / closed — skip. |
| Family Checkin | 6022 | Pay-from for card pays. ACH for Portland ME property tax is SSM `/chase/common-account-number` + `/chase/common-routing-number` (API `maine_property_tax_pay`). Never paste full account/routing in chat or git. |
| Jerome Checkin | 6803 | Do not use for these pays. |
| Chase username (prefilled) | jerome5080 | SSM `/chase/username`. Password is SSM `/chase/password` only. |

## Routine

- Name: **Freedom Unlimited + Reserve over-$150 pay**
- Folder: `freedom-unlimited-over-150-pay`
- Cron (America/Los_Angeles): `12 9 * * 1,4`  # Mon+Thu
- Per card (FU + Reserve): quiet skip if balance ≤ $150 or already covered.
- Quiet overall only if neither card was paid.
- After any successful payment(s): tell Jerome once — each amount,
  from-account, confirmation number, date, pending/posted.

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
Do not hammer the site. Keep the Chrome profile. When Chase actually
boots the session, fetch SSM and sign in; hand the box only for 2FA /
mobile-app confirm.

Known miss: 2026-08-28 9:12am slot skipped because the box host
restarted for an idle auto-update around 9:16am PT (caught up ~9:22).
2026-09-04 Friday run **failed** `[resource_exhausted]` — no payment
attempted that morning.

## Zelle — Miss Cleo / cleaning

Saved recipient: **Cleo - Cleaners Bellevue** (CLEONES FONSECA DE MELO), phone
ending **5137**. Prefer this recipient when he says Miss Cleo / Cleo cleaning
Zelle. Confirm on review before Send money. Fund from Family Checkin (...6022).

Latest: 2026-10-11 **$150** memo **Cleaning**, Funded, conf **JPM99czktbk9** (Zelle form defaulted to Jerome Checkin 6803 — always switch to 6022). Prior: 2026-10-01 **$150** from Family Checkin (...6022), memo **Cleaning**,
Funded, conf **JPM99cyergv5**. Prior 2026-09-24 **$150** memo **Cleaning today**,
Funded, conf **JPM99cxlf0ox**. Earlier same day activity also showed Delivered
**JPM99CXKBVGC** $150 from Jerome Checkin (...6803) memo “cleaning last week”
(separate; do not treat as today’s cleaning). 2026-09-10: **$150** memo
**Cleaning**, conf **JPM99cw3helz** (Funded).

## Zelle — Ted / monthly rent

Saved recipient: **Ted (Landlord)**. Monthly rent **$4,350** from Family Checkin
(...6022), memo **Rent**. Grok Bot routine **Monthly rent Zelle to Ted** fires
on the 24th at 2:06 PM PT and must get Jerome’s explicit chat approval before
Send money. 2026-09-24: **$4,350** Delivered, conf **30944244050**.

## Debit card replacement

Jerome Checkin (...6803) has Disney Debit (...1688). On 2026-09-09 he ordered a
replacement (damaged) via Chase: no fee, 5–7 business days to
3099 125TH AVE NE, Bellevue, WA 98005-1655; card number unchanged; keep using
old card until activate. Do **not** order for Family Checkin (...6022) unless
he asks for the common/family account.

## Manual "pay the cards" (chat)

When Jerome says pay the cards (plural), check every credit card, skip
$0 and anything already covered, pay uncovered current balances from
Family Checkin 6022, same submit path. Report per-card last-4, amount,
confirmation.

## Known blocker: browser agent won't enter the password (2026-10-05)

2026-10-05 Mon 9:12 run: Chase signed out. Finance showed FU (...6553)
current $1,492.43 and Reserve (...8053) $308.19, no payments since the
Oct 1 pays, so both needed paying. SSM fetch worked. Staging the password
on the X clipboard (xclip) for the browser subagent to paste: attempt 1
pasted and Chase bounced to `partnerSignout` / "We've signed you out";
attempt 2 the paste landed in the Username field (password visible on
screen; screenshot deleted); attempt 3 the browser subagent refused to
paste credentials at all. Nothing paid. Lesson: if pasting, Tab from
Username and confirm Password focus first; but expect the browser agent
to refuse, so ask Jerome to sign in on the box (request_box_help) and then
run the pay. Clear the clipboard (`pkill xclip`) after any attempt.

## Known blocker: SSM password rejected (2026-10-06)

2026-10-06: two careful SSM attempts (paste verified in Password field, Use token
unchecked) both returned "We can't find that username and password." Username
`jerome5080` correct; `/chase/password` (13 chars, no whitespace) likely stale.
Stop after 2 rejections to avoid lockout; hand the box to Jerome and ask him to
update `/chase/password` in SSM. Jerome signed in on the box 2026-10-07 evening.
Also: a bad Chrome autofill entry (username with extra characters appended) exists
under Username; never select it, and ask Jerome to delete it.

## Latest one-time pays

2026-10-15 Thu 9:12 routine (Chrome autofill jerome5080 login, no identity check; first Sign in bounced to chase.com logout, retry worked): Reserve (...8053) $303.64 current balance conf 9795919701 Pending Oct 15 from Family Checkin 6022. FU (...6553) $748.59 skipped, already covered by an Oct 15 pending $748.59 payment not made by this routine. Finance feed lagged (showed FU $623.59, Reserve $191.24), so always use live Chase balances.

2026-10-12 (Jerome signed in on box; Family Checkin 6022, Pending, Oct 12): FU (...6553) $1,261.28 conf 9786650212; Reserve (...8053) $1,050.72 conf 9786652925. UR combine 11,908 FU->Reserve hit a mobile-app identity check at combine-points/review.

2026-10-07 evening (manual "do it again" after Jerome signed in on box): FU (...6553) $245.00 conf 9774677223 Pending, date Oct 08 (form defaults to next day after midnight ET), from Family Checkin 6022; an Oct 7 $2,286.85 payment had already posted. Reserve (...8053) $72.38 skipped (<= $150).

2026-10-01 (manual after Cleo Zelle; Family Checkin 6022, Pending):
- Freedom Unlimited (...6553) $325.00 conf 9756243967
- Sapphire Reserve (...8053) $106.99 conf 9756242372

## Continuous improvement

After each payment, auth handoff, or correction:

1. Patch `skills/cutychase-pay-balance/SKILL.md` in
   `/workspace/localGrokSkills` (repo `jeromevidaao/localGrokSkills`).
2. Immediately commit + push (always-push). Never leave learnings only
   in chat or only on disk.
3. Mirror durable facts into this bot's agent memory **and Titan**
   (`r2_memory_turn.py append`).

## Do not

- Paste Chase password / 2FA in chat, git, disk, or Titan (fetch SSM at login)
- Scrape Chrome cookies / Login Data
- Pay from Jerome Checkin 6803
- Pay inactive cards (...2797, ...0159) on the scheduled routine
- Double-pay a covered balance
- Invent a balance when signed out
- Leave the routine firing on a repeated auth wall — pause it
