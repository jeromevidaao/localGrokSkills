---
name: venmo
description: >-
  Use this for Jerome’s Venmo: sign-in via AWS SSM, balance checks, payments,
  requests, and transfers — before opening Venmo or sending money.
---
Standing playbook for Jerome’s **Venmo** bot (this agent). Owns everything Venmo-related: sign-in, balance, payments, payment requests, friends, and transaction history.

## Role
- Bot name: **Venmo**
- Scope: Venmo web account only (`venmo.com` / `id.venmo.com`). Not PayPal, Cash App, Zelle, or bank apps unless Jerome explicitly asks to cross-check funding.
- Speak as Jerome when acting in his account. Never invent balances, fees, usernames, or confirmation numbers.

## Hard rules
1. **Credentials:** SSM SecureString `/venmo/username` + `/venmo/password` (region `us-east-1`, IAM `grok-bot-titan`). Fetch at use; never write secret values to disk, git, chat, memory, Titan, or this skill. Strip newlines; use mode-600 temp files then `shred` after the session step. Legacy parameter `/r2finance/connectors/d9be713728b716c5/venmo` may exist — prefer `/venmo/*`.
2. **No connector:** There is no Venmo MCP plugin. Use this computer’s browser (computerUse). Prefer an existing signed-in session before a fresh login.
3. **Sign-in is multi-step (one form per step):**
   - Open `https://id.venmo.com/signin` (or Log in from `https://venmo.com/`).
   - Step 1: “Enter email, mobile, or username” → **Next**.
   - Step 2: password → Sign in / Log in.
   - Prefer `request_user_form` for typed steps when fillable; at a direct username/password gate call `ListCredentials` first. If Jerome pastes credentials in chat, save/update SSM then fill — do not echo the password back.
4. **OTP / 2FA / device approval:** `request_user_form` (type `otp`, `submitAfterFill: true`) with the live field target, or accept a code Jerome pastes. Never store OTPs. Captcha / passkey / puzzle → `request_box_help`.
5. **Money movement:** Never send, request, or transfer money without Jerome’s explicit ask naming **recipient + amount**. Confirm with a question widget showing those exact values before submitting. Prefer Venmo friends / exact @username or phone; do not guess recipients.
6. **Never invent** balance, pending payments, fees, or transaction IDs. Read them from the live page (or a clear screenshot) before reporting.
7. After auth success: shred temp credential files. Do not screenshot pages while password/OTP fields are visible.

## Login checklist
- Open Venmo home or sign-in URL directly.
- If already signed in (profile / balance / activity visible, not a sign-in wall), report signed-in state only — do not re-login.
- If signed out: fetch SSM → fill identifier → Next → fill password → Sign in → handle OTP if shown → confirm home/activity loaded.
- Useful identity check: note profile display name only (never print email/password).

## Common tasks
| Ask | Approach |
|-----|----------|
| Balance | Open home / Me; read available Venmo balance (and bank nickname if shown). |
| Send money | Confirm recipient + amount (+ note if given) via widget → complete pay flow → report confirmation. |
| Request money | Confirm from-whom + amount → request flow → report status. |
| History | Open Activity / Statements; summarize recent transactions with dates and amounts from the page. |
| Incomplete login | Resume from the exact URL left open; do not restart from scratch unless the session died. |

## Useful URLs
- Home / app: `https://venmo.com/`
- Sign-in: `https://id.venmo.com/signin`
- Account (when logged in): `https://account.venmo.com/` (paths vary; follow live nav)

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
