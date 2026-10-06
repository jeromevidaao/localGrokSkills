---
name: schwab
description: >
  Use this for Jerome Ansia's Charles Schwab brokerage and banking: sign-in,
  balances, positions, transfers, and account ops on Schwab. Read first every
  time Jerome talks to the Charles Schwab bot; update and push after new
  learnings. Outbound ACATS/share moves to Vanguard are started by the
  Vanguard bot, not from Schwab Transfer & Pay.
---

# Charles Schwab — brokerage & banking

Standing playbook for the **Charles Schwab** bot. On every Jerome message:
**Titan retrieve first**, then read this skill. After meaningful turns:
**update this skill**, **append to Titan**, and **commit + push**
(`always-push`).

Related: `r2-memory`, `always-push`, Vanguard bot (inbound ACATS / in-kind
moves from Schwab).

## Hard rules

1. **Credentials:** AWS SSM SecureString (us-east-1, IAM `grok-bot-titan`)
   `/schwab/username` and `/schwab/password`. Fetch at use only. Never ask
   Jerome to paste a password in chat. Never write secret values to disk, git,
   chat, memory, Titan, screenshots, or this skill — path names only. If a
   path is missing, say which path and stop. Strip newlines; use mode-600
   temps then shred.
2. **Sign-in:** Prefer existing Chrome session. Else
   `https://client.schwab.com/Areas/Access/Login` (or schwab.com → Log in).
   Prefer in-chat forms / box handoff over chat paste. Never type 2FA codes
   yourself (`request_user_form` for OTP).
3. **Trust device:** When shown “Trust this device”, choose **Yes, trust this
   device** → Continue (Jerome preference for this box).
4. **No outbound ACATS in Schwab UI:** Transfer & Pay has cash/wire/inbound
   “Move Account to Schwab” only. Broker-to-broker share moves to Vanguard
   start at Vanguard (`investor.vanguard.com/account-transfer`). Pass Schwab
   account number and position details to the **Vanguard** bot.
5. **Always-push** skill edits same turn. Titan retrieve → append every real ask.

## Accounts

| What | Value | Notes |
|---|---|---|
| Brokerage account number | **75590650** | Confirmed by Jerome 2026-09-29 |
| Login ID | SSM `/schwab/username` | Also known in ops as `jeromeans` (verify via SSM) |
| Password | SSM `/schwab/password` | Never store in this file |

## Positions / transfers (known)

- **2026-09-29:** Jerome reported **40 shares NVDA** in account 75590650 for
  partial in-kind ACATS to Vanguard. Cost basis not verified in UI (login
  failures during that session). Approximate account total seen earlier when
  signed in: ~$8,961 (2026-09-24).
- Phone on file used in password-reset flow: ends **3958** (646-204-3958 given
  for reset identity).

## Browser notes

- Positions / Transfer Funds may show temporary Schwab “unavailable” errors —
  retry later; do not invent holdings.
- Prefer computerUse; no screenshots while password/OTP visible.
- Close unused Chrome tabs when Chief of staff asks.

## Titan

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "question"
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "..." --assistant "..."
```

Canonical copy: `/workspace/localGrokSkills/skills/schwab/SKILL.md` — keep
Grok Bot `workflows/schwab` in sync.

## Do not

- Paste Schwab password / OTP in chat, git, or Titan
- Start outbound ACATS from Schwab Transfer & Pay (use Vanguard bot)
- Leave learnings only in chat
