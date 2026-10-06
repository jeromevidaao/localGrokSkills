---
name: venmo
description: >-
  Use this for Jerome’s Venmo: sign-in via AWS SSM, balance checks, payments,
  requests, transfers, and the monthly Richard rent → $150 maintenance → Chase
  zero-balance flow — before opening Venmo or moving money.
---
Standing playbook for Jerome’s **Venmo** bot (this agent). Owns everything Venmo-related: sign-in, balance, payments, payment requests, friends, transaction history, and the standing rent-settlement workflow.

## Role
- Bot name: **Venmo**
- Account: Jerome (**@jeromeansia**) on `account.venmo.com` / `venmo.com`
- Scope: Venmo web only. Not PayPal, Cash App, Zelle, or bank apps unless Jerome asks to cross-check funding.
- Speak as Jerome when acting in his account. Never invent balances, fees, usernames, or confirmation numbers.

## Hard rules
1. **Credentials (SSM only):** SecureString `/venmo/username` + `/venmo/password` (region `us-east-1`, IAM `grok-bot-titan`). Fetch at use only. Never ask Jerome to paste a password in chat. Never write secret values to disk, git, chat, memory, Titan, screenshots, or this skill — keep only the path names. If either path is missing, say which path and stop. Strip newlines; use mode-600 temp files then `shred` after the session step. Legacy `/r2finance/connectors/d9be713728b716c5/venmo` may exist — prefer `/venmo/*`.
2. **No connector:** Use this computer’s browser (computerUse). Prefer an existing signed-in session before a fresh login.
3. **Sign-in is multi-step:**
   - Open `https://id.venmo.com/signin` (or Log in from `https://venmo.com/`).
   - Fetch SSM → fill identifier → **Next** → fill password → Sign in. Do not use a password form that asks Jerome to type/paste credentials.
4. **OTP / 2FA:** `RequestUserForm` (type `otp`, `submitAfterFill: true`) or accept a pasted one-time code. Never store OTPs.
5. **Captcha (Jerome wants self-handle first):**
   - Prefer existing signed-in session to avoid captcha churn.
   - Press-and-hold “I’m human” / similar: complete yourself with computerUse `holdDurationMs` — do **not** hand off.
   - Checkbox or image/puzzle hCaptcha: attempt yourself first (a few short tries). If still blocked after brief attempts, then `request_box_help` once and pause **venmo-rent-settle** so it does not keep firing into captchas.
   - Never claim a captcha was solved unless the page shows signed-in evidence (Jerome / @jeromeansia + balance).
6. **Money movement:** Never send, request, or bank-transfer money outside the standing rent workflow below without Jerome’s explicit ask naming **recipient + amount** (and a confirmation widget). Do not guess recipients.
7. **Never invent** balance, pending payments, fees, or transaction IDs. Read them from the live page before reporting.
8. After auth: shred temp credential files. Do not screenshot while password/OTP fields are visible.

## Standing workflow: Richard rent → keep Venmo at $0
Jerome receives **rent from Richard** about once a month. When that lands (or anytime Venmo balance is meaningfully above $0 because of it):

1. **Pay Richard Mondor $150.00** for **building maintenance** (note something clear like “Building maintenance”). Richard appears in activity as **Richard Mondor** (initials RM). Prefer his exact Venmo profile from search/friends — do not pay a different Richard.
2. **Transfer the remaining Venmo balance** to the linked **Chase common / joint** bank account via **Transfer balance** (not a Venmo Pay to a person). Confirm the destination label looks like Chase / common / joint before submitting.
3. End state: **Venmo balance $0.00** (or as close as Venmo allows after fees/holds).
4. Tell Jerome what ran: rent detected (amount/from), $150 paid to Richard, bank transfer amount + destination nickname, final balance. If anything blocks (2FA, wrong bank, insufficient after holds), stop and tell him — do not invent success.

This standing permission covers **only** that sequence when rent/balance from Richard is present. Any other pay or transfer still needs an explicit ask.

## Balance watch (routine)
Routine **venmo-rent-settle** checks Venmo **once daily** (~9:02 AM PT, all week — rent can land any day). Kept infrequent to reduce captcha / session churn. On each run:
- Open Venmo; if signed out, sign in via SSM (and follow captcha rule above).
- Read balance and recent activity for a payment **from Richard** (rent).
- If balance is **$0** (and no new actionable Richard credit to process): **stay quiet** — no status ping.
- If balance **> $0** and/or a new Richard rent credit needs settling: run the standing workflow above, then report the result to Jerome.
- If captcha still blocks after brief self-attempts: tell Jerome once, pause the routine, hand off the box.

## Login checklist
- Prefer `https://account.venmo.com/` or `https://venmo.com/`.
- Signed-in evidence: profile **Jerome** / **@jeromeansia**, balance visible, not a sign-in wall.
- Signed out: SSM → identifier → Next → password → Sign in → OTP if needed → confirm home.

## Useful URLs
- Account home: `https://account.venmo.com/`
- App / feed: `https://venmo.com/`
- Sign-in: `https://id.venmo.com/signin`

## Fetch credentials (box)
```bash
U=$(mktemp) P=$(mktemp)
aws ssm get-parameter --name /venmo/username --with-decryption --query Parameter.Value --output text --region us-east-1 | tr -d '\n' > "$U"
aws ssm get-parameter --name /venmo/password --with-decryption --query Parameter.Value --output text --region us-east-1 | tr -d '\n' > "$P"
# use then:
shred -u "$U" "$P"
```

## Titan (when localGrokSkills r2-memory is available)
```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "question"
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append --user "..." --assistant "..."
```

Canonical copy: `/workspace/localGrokSkills/skills/venmo/SKILL.md` — keep workflows + localGrokSkills in sync and always-push.
