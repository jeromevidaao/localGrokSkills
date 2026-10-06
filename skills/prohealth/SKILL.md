---
name: prohealth
description: >-
  Use this for Jerome’s ProHealth (prohealth.com) account: sign-in via AWS SSM,
  searching supplements, and always trying public coupon codes and keeping the
  best one before checkout.
---
Standing playbook for Jerome’s ProHealth bot. Prefer the managed `shopping` and `purchases` skills for cart and checkout rules; this skill covers ProHealth-specific auth and coupons.

## Hard rules
1. Credentials: SSM SecureString `/prohealth/username` and `/prohealth/password` (us-east-1, IAM `grok-bot-titan`). Fetch at use; never write values to disk, git, chat, memory, or Titan. Strip newlines; use mode-600 temp files, then shred them after the sign-in step.
2. Site: `https://www.prohealth.com/`. Prefer an existing signed-in browser session on this computer before a fresh login.
3. Sign-in: open the site, open Account / Sign in, fill the SSM username, then the password. One step at a time. Do not re-login if already signed in.
4. OTP / 2FA: ask the user for the code in the moment. Never store OTPs.
5. Captcha, puzzle, passkey, or device approval: hand the screen to the user with one clear instruction. Do not screenshot secret fields.
6. Before every order, search online for current public discount codes and try each real one on this cart. Keep only the best one, meaning the largest dollar savings. Do not invent a code. A crossed-out site price is not a coupon. If none apply, say so and continue only if the user still wants the order.
7. Shopping: search and compare, confirm the pick, show the cart, confirm the ship-to address, show the winning code, the discount, and the exact total, and get a yes before any place-order step. Ignore subscribe-and-save and upsells unless asked.
8. Never invent a price, rating, stock status, or order number. Never place an order without an explicit buy ask and a confirmation of the exact total.
9. Payment: use a saved card on the account when one is offered. If checkout shows an empty card form, stop and ask. Never write card numbers into chat.

## Coupon checklist
- Search the web for current prohealth.com coupon codes before adding payment.
- Try each real code on this cart. Rejected codes do not count.
- Compare the discounts and keep the single best code. Do not stack unless the site itself applies more than one.
- Report the winning code, the discount, the codes that were rejected, shipping, tax, and the total before placing the order.

## Login checklist
- Open `https://www.prohealth.com/` directly.
- If the header shows a signed-in account, treat that as logged in. Report only that it is signed in, not the email or password.
- If signed out: fetch SSM creds, fill username, fill password, sign in, handle OTP if prompted, confirm the account is signed in.
- After success: shred temp credential files.

## If SSM is empty
Do not ask the user to paste a password into chat. Tell them `/prohealth/username` and `/prohealth/password` are missing in us-east-1 and stop until those parameters exist.
