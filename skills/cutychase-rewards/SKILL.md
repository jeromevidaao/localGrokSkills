---
name: cutychase-rewards
description: >
  Use this whenever working Chase Ultimate Rewards for Jerome (combine points,
  Chase Travel portal pricing/booking with UR points, Freedom Unlimited →
  Sapphire Reserve sweeps), or after any Chase rewards conversation when this
  playbook should be refined. Every turn: Titan retrieve first, then this skill;
  append to Titan after; update + commit + push after new asks.
---

> **Owning bot: Chase Bank & Rewards** (merged). This playbook is owned by **Chase Bank & Rewards** (id `220daf8a-5395-407b-b48e-20b0d773ce9f`); former CutyChase - Pay Balance is deprecated/merged into the same bot. All UR / points / Chase Travel rules below still apply.

# CutyChase - Rewards (Chase Ultimate Rewards)

Standing playbook for the **CutyChase - Rewards** bot. On every Jerome
message: **Titan retrieve first**, then read this skill. After the turn,
**append to Titan**. After Jerome asks for something new or corrects a flow,
**update this file** in `localGrokSkills`, then **commit + push immediately**
(follow **always-push**). Do not leave learnings only in chat.

Related: `r2-memory` (Titan retrieve/append), `always-push`, `flight-booking`
(full legal name, airline book + calendar) when the task moves from pricing to
purchasing a ticket.

## Hard rules

1. **Never touch household / other-owner cards.** DINH Chase ending **1407** and
   similar household member wallets must not be sources or destinations for
   combines or points ops.
2. **Cards (Jerome):**
   - Sapphire Reserve **...8053** — primary UR wallet / combine destination
   - Freedom Unlimited **...6553** — combine source (sweep onto Reserve)
   - Inactive ...0159 / ...2797 — usually 0 pts; ignore unless they gain balance
3. **Auth:** if signed out, fetch SSM `/chase/username` and `/chase/password`
   (SecureString) and type them. Never write those values to disk, git, chat,
   or Titan. **Never type 2FA** or paste card secrets in chat — use
   `request_box_help` for mobile-app confirm. Username may stay remembered
   (`jerome5080`).
4. **Purchase gate:** stop before charging Chase Travel or transferring UR to an
   airline. Get Jerome’s **explicit OK** in chat before paying or irreversible
   transfers (Alaska miles transfers do not come back).
5. **Always commit + push this skill** after edits (always-push: public → push
   `main` → CI green → private). Never ask “want me to push?”.
6. **Refine after every conversation:** if Jerome taught something new, patch
   this `SKILL.md` same turn, push, and mirror durable facts into agent memory.
7. **Titan R2Memory (read + write):** every time Jerome talks to this bot,
   **retrieve first**, then **append/update after the turn** so Titan stays current.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Full playbook: skill `r2-memory`.

## Titan R2Memory (every turn)

Scripts: `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`).

On this shared Grok Bot computer, AWS is already configured as IAM user
**`grok-bot-titan`** (`~/.aws/credentials`, region `us-east-1`). Do **not** fetch
SSM keys or paste secrets — retrieve/append should just work.

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Use hits for standing Chase/UR prefs and past decisions. Then read this skill.
Skip only pure chitchat (`hi` / `ok` / `thanks`).

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

Also update this `SKILL.md` + push when the turn taught something durable.

## Chase SSM login (when signed out)

SSM SecureStrings (us-east-1), readable by IAM **`grok-bot-titan`**:

| Param | Purpose |
|---|---|
| `/chase/username` | Chase online username |
| `/chase/password` | Chase online password |

Never write those values into git, chat, Titan, screenshot captions, or this skill.
Fetch at use only.

```bash
aws ssm get-parameter --name /chase/username --with-decryption \
  --query Parameter.Value --output text --region us-east-1
aws ssm get-parameter --name /chase/password --with-decryption \
  --query Parameter.Value --output text --region us-east-1
```

Playbook:

1. Fetch both params. Optional: write `CHASE_USER` / `CHASE_PASS` to a mode-`600`
   temp file for the desktop agent, then **delete** the file after login.
2. Prefer **computerUse** for the password field if **browserUse** loops on keys.
   Keep the password **masked** (Hide). One clean fill + **Sign in**.
3. If **Confirm Your Identity** / mobile app: `request_box_help` — never invent codes.
4. Real success = `secure.chase.com` dashboard with accounts + header **Sign out**.
   A green **“You have successfully signed out.”** banner on `chase.com` is a
   **false positive** — sign in again and/or open
   `https://secure.chase.com/web/auth/dashboard` (no hash) and wait ~10s.
5. Avoid `partnerSignout` / `logoff` URLs; they wipe the session.

Verified **2026-09-06**: SSM login reached Accounts overview.

## Standing routine — Freedom → Reserve combine

Folder: `32e25744-7bc8-58bb-a51e-80d178e1d741` (Combine Freedom Unlimited points onto Reserve)  
Schedule: **Weekly Monday 9:28 AM America/Los_Angeles** (`CRON_TZ=America/Los_Angeles 28 9 * * 1`)  
Changed 2026-09-24 from 1st+16th ~9am to weekly Monday (Jerome via Chief of staff).

Each run:

1. Open Chase / Ultimate Rewards in box Chrome. If already in, continue.
   If logged out, fetch SSM and sign in; hand the box only for 2FA.
2. Combine Points: move **all available** Freedom Unlimited (...6553) pts onto
   Sapphire Reserve (...8053). Confirm when Chase asks.
3. If **0 available** points: **stay quiet** (do not message Jerome). Pending
   points cannot be combined until they post.
4. If points moved: tell Jerome amount, last-4s only, and new Reserve balance.
5. If identity verification / app push: hand box; continue after he hands back
   until Combine Points Success.
6. Do **not** transfer to airlines, hotels, or Pay with Points on this routine.
7. This bot (Chase Bank & Rewards) owns all Chase pay/Zelle/UR after merge;
   do not wake deprecated CutyChase - Pay Balance.

Live (non-routine) combines Jerome requests in chat: always report the result,
including zero available + pending if nothing moved.

## Chase Travel (UR portal) — what Jerome wants for “points”

When Jerome says fly / look for flights **with points** in this chat, default to
**Chase Ultimate Rewards Travel portal** (points or cash shown as either/or),
**not** Alaska Mileage Plan miles — unless he explicitly asks for Alaska miles
or Atmos awards.

Typical work-week pattern he cares about (align with `flight-booking`):

- Out: **Friday ~5pm SJC → SEA**, Alaska **nonstop** preferred
- Back: **Monday ~7am SEA → SJC**, Alaska **nonstop** preferred
- Example priced 2026-08-27 for Fri Sep 18 / Mon Sep 21:
  - AS 3391 SJC 5:13pm → SEA 7:28pm + AS 1341 SEA 7:08am → SJC 9:32am
  - Chase Travel Main: **$731 or 58,409 UR pts** (Points Boost applied)
  - Alaska miles for same pair was 60,000 + $12 (informational only unless asked)

Report UR points (+ cash alternate), nearby directs (e.g. 7:45pm out is often
cheaper), and Reserve balance. Stage only; wait for OK before booking.

## Browser / box notes

- Prefer **browserUse** for Chase navigation; use **computerUse** for SSM
  password fill if browserUse key-loops, or if the browser driver fails.
- Chase tabs can Aw Snap (error 9); reload or open a fresh `secure.chase.com`
  tab. If the driver is dead, restart this agent’s Chrome with **`box-chrome`**
  only (never raw chrome). Sessions may drop after restart → SSM login;
  hand the box only for 2FA.
- Shared box RAM: close unused tabs on **this** desktop only when asked; never
  kill other agents’ Chrome processes.

## Do not

- Combine from or onto DINH / ...1407
- Transfer UR → Alaska (or any partner) without explicit OK
- Book Chase Travel without explicit OK
- Message Jerome on the scheduled sweep when Freedom available balance is 0
- Paste Chase password / 2FA in chat, git, disk, or Titan (fetch SSM at login)
- Ask whether to commit/push skill updates
