---
name: amazon
description: >-
  Use this for Jerome’s Amazon shopping: sign-in via AWS SSM,
  search/compare/reorder, cart and checkout handoff, or order tracking.
---
Standing playbook for Jerome’s Amazon bot. Prefer the managed `shopping` skill for cart/checkout rules; this skill covers Amazon-specific auth and account paths.

## Hard rules
1. Credentials: SSM SecureString `/amazon/username` + `/amazon/password` (us-east-1, IAM `grok-bot-titan`). Fetch at use; never write values to disk/git/chat/memory/Titan. Strip newlines; use mode-600 temp files then shred after the session step.
2. Site: `https://www.amazon.com/` (Amazon Shopping). Prefer an existing signed-in Chrome session on this computer before a fresh login.
3. Sign-in flow (multi-step): open Amazon → Account & Lists / Sign in → email/phone (`#ap_email` or equivalent) → Continue → password (`#ap_password`) → Sign in. One step at a time. Prefer existing session; do not re-login if already Hello, [name].
4. OTP / 2FA: when Amazon asks for a verification code, use `request_user_form` (type `otp`, `submitAfterFill: true`) with the live field target, or accept the code Jerome pastes in chat. Never store OTPs.
5. Captcha / puzzle / passkey / device approval: `request_box_help` with one clear instruction. Do not screenshot secret fields.
6. Shopping: follow the managed `shopping` skill — search/compare shortlist, confirm pick, cart screenshot, address confirm, final total widget before any place-order handoff. Ignore Subscribe & Save / protection-plan upsells unless asked.
7. Reorders: start from Your Orders / Buy Again, not a fresh search, when Jerome says “usual” or “again”.
8. Never invent price, rating, delivery date, or order number. Never place an order without an explicit buy ask and a confirmation widget with the exact total.

## Login checklist
- Open `https://www.amazon.com/` directly.
- If the nav shows a signed-in greeting (not “Hello, sign in”), treat as logged in; report the greeting name only (no email/password).
- If signed out: fetch SSM creds → fill email → Continue → fill password → Sign in → handle OTP if prompted → confirm greeting.
- After success: shred temp credential files.

## Useful URLs
- Home: `https://www.amazon.com/`
- Orders: `https://www.amazon.com/gp/css/order-history`
- Buy Again: `https://www.amazon.com/gp/buyagain`
- Cart: `https://www.amazon.com/gp/cart/view.html`
- Search: `https://www.amazon.com/s?k=<urlencoded query>`

## Titan (when localGrokSkills r2-memory is available)
```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "question"
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append --user "..." --assistant "..."
```

Canonical copy (when present): `/workspace/localGrokSkills/skills/amazon/SKILL.md` — keep both in sync and always-push.
