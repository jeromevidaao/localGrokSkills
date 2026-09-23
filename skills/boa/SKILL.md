---
name: boa
description: >
  Use this for Jerome Ansia's Bank of America online banking: sign-in, 2FA,
  Preferred Rewards / card rewards lookup, paying credit card balances from the
  common account, or the Mon/Wed/Fri BoA pay routine. Read first every time
  Jerome talks to the BoA bot; update and push after new learnings.
---

# BoA — Bank of America banking & rewards

Standing playbook for the **BoA** bot. On every Jerome message: **Titan
retrieve first**, then read this skill. After the conversation (or any
correction), **update this skill**, **append the turn to Titan**, and
**commit + push immediately**.

Related: `r2-memory` (Titan retrieve/append), `always-push`,
CutyChase pay-balance / rewards (Chase is a different bank — do not mix
credentials or funding accounts).

## Hard rules (never skip)

1. **Login credentials:** AWS SSM SecureString (us-east-1)
   `/boa/username` and `/boa/password`. Fetch at use only. Never write
   those values to disk, git, chat, Titan, or this skill. Stage into
   mode-`600` temp files for the desktop agent if needed, then **shred**.
   Strip trailing newlines from `aws ssm get-parameter` output.
2. **Sign-in URL:** start at `https://www.bankofamerica.com/` Online Banking
   User ID (`#oid`) + Password (`#pass`), then Log in
   (`#secure-signin-submit`). Prefer an existing signed-in Chrome session
   on this computer when still valid.
3. **2FA:** BoA sends an authorization code by **text** (or phone call) to
   the masked number ending **3958**. Keep **Text message** selected →
   **Next** → enter code on `#ahAuthcodeValidateOTP` → select **Yes,
   remember this device** → Continue. Prefer an in-chat OTP form
   (`request_user_form`) over asking him to paste codes in chat. Do not
   invent codes. After a generic “unable to complete your request” error,
   start a **fresh** homepage login (do not keep hammering the failed
   session).
4. **Funding account:** pay card balances from the **common / joint
   checking** account already linked at BoA. Never pick a personal-only
   account when the common account is available.
5. **Payments:** when Jerome says pay the balance / pay the cards, pay
   **current or statement balance in full** (whichever the site presents
   as paying off that cycle) for each card with a nonzero amount due.
   Check for pending payments first; do not double-pay. Report last-4,
   amount, funding account, confirmation.
6. **Rewards:** read-only unless he explicitly asks to redeem. Summarize
   balances, Preferred Rewards tier if shown, and redemption options
   (travel, statement credit, gift cards, BankAmeriDeals). Stop before
   any irreversible redeem/transfer.
7. **Scheduled routine:** **BoA pay card balance** — folder
   `boa-pay-card-balance`, cron `07 8 * * 1,3,5` America/Los_Angeles
   (Mon/Wed/Fri **8:07 AM PT**). Each run: SSM sign-in if needed, pay
   card balances in full from the common account, tell Jerome what went
   out (or that nothing was due). Pause the routine on repeated auth
   walls and tell him.
8. **Always commit + push this skill:** any edit to `skills/boa/` must
   be committed and pushed to `jeromevidaao/localGrokSkills` the same
   turn — **always-push** (public → `git push` `main` → CI green →
   private). Never ask “want me to push?”.
9. **Titan R2Memory (read + write):** every meaningful BoA turn,
   retrieve first, append after. Bucket:
   `cleaningbutton-ai-context-us-east-1`. Full playbook: skill
   `r2-memory`.

## Titan R2Memory (every turn)

Scripts: `/workspace/localGrokSkills/skills/r2-memory/scripts/`
(also `~/.grok/skills/r2-memory/scripts/`).
On this shared computer, AWS is already **grok-bot-titan**, region
`us-east-1`.

### Before answering (retrieve)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "your question"
```

Then read this skill. Skip only pure chitchat (`hi` / `ok` / `thanks`).

### After the turn (append)

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "what he said" --assistant "what you answered"
```

## SSM login playbook

| Param | Purpose |
|---|---|
| `/boa/username` | Online Banking User ID |
| `/boa/password` | Online Banking password |

```bash
umask 077
aws ssm get-parameter --name /boa/username --with-decryption \
  --query Parameter.Value --output text --region us-east-1 | tr -d '\r\n' > /workspace/.boa_u
aws ssm get-parameter --name /boa/password --with-decryption \
  --query Parameter.Value --output text --region us-east-1 | tr -d '\r\n' > /workspace/.boa_p
chmod 600 /workspace/.boa_u /workspace/.boa_p
# desktop agent types from files, then:
rm -f /workspace/.boa_u /workspace/.boa_p
```

Verified **2026-09-23**: SSM login reached Accounts Overview after SMS
2FA to *3958 and “remember this device”.

## Browser notes

- After wrong-password or hard errors, navigate back to
  `https://www.bankofamerica.com/` for a clean form rather than retrying
  a broken secure.bankofamerica.com auth hash URL.
- Prefer **computerUse** for fills and clicks; do not screenshot while
  password or OTP may be visible.
- Prefer existing session; re-auth only when BoA actually signed you out.

## Accounts (last-4 only)

| What | Last 4 | Notes |
|---|---|---|
| Atmos Rewards Ascent Visa Signature | 5741 | Primary BoA card seen 2026-09-23; Atmos Rewards wallet |
| Common / joint checking | (pay-from) | Fund all card pays from this common account; pay UI may label it "common chase" |

## Atmos Rewards (Ascent …5741)

Verified **2026-09-23**:
- Available: **88,547** Atmos points
- Status: Atmos Member; 5,961 status pts YTD; 4,039 to next 10K; 14,039 to Silver
- Redemption shown: Alaska award flights (`alaskaair.com` award search), Atmos Rewards Unlocked experiences (`unlocked.atmosrewards.com`) — buy-now and auctions by point bands
- Not shown in UI that day: cash-back, statement credit, gift cards
- Do not redeem without an explicit ask

## Latest payment

2026-09-23: paid Atmos Ascent …5741 **$4,209.78** current balance from common checking, confirmation `vb4sllga1`. Statement-balance recurring left unchanged.

## Continuous improvement

After each login, payment, rewards lookup, or correction:

1. Patch `skills/boa/SKILL.md` in `/workspace/localGrokSkills`.
2. Commit + push (always-push) the same turn.
3. Mirror durable facts into this bot’s agent memory **and Titan**.

## Do not

- Paste BoA password / OTP in chat, git, disk, or Titan (fetch SSM at login)
- Fund card pays from a non-common account when common is available
- Redeem rewards without an explicit ask
- Double-pay a covered balance
- Leave the Mon/Wed/Fri routine firing on a repeated auth wall — pause it
- Leave skill learnings only in chat
