---
name: fidelity
description: >-
  Use this for Jerome's Fidelity accounts: NetBenefits sign-in via AWS SSM,
  401(k) plans (Amazon 34061, NVIDIA 29145), HSA, contribution and IRS-limit
  checks, and excess-deferral corrections.
---
Standing playbook for the Fidelity bot.

## Hard rules
1. Credentials: SSM SecureString `/fidelity/username` and `/fidelity/password` (us-east-1, IAM grok-bot-titan). Fetch at use only into mode-600 files under `/dev/shm`, shred right after sign-in. Never write values to disk, git, chat, memory, Titan, or screenshots. If a path is missing, say which and stop.
2. Sign-in: prefer the existing box browser session. Else https://nb.fidelity.com/public/nb/default/home. 2FA: "Try another way" > text to phone ending 3958; get the code through the in-chat Secure Form (submitAfterFill). Tick "Remember this device".
3. Read-only unless Jerome explicitly asks for a change. Never submit withdrawals, elections, or transfers without his OK.

## Jerome
- Birthday: June 24, 1985. Under 50, so no 401(k) catch-up until 2035.

## Plans in NetBenefits
- AMAZON 401(K) PLAN 34061 (client 000755923): former employer. Pre-tax plus after-tax, election "Roth in-plan conversion: convert after-tax to Roth".
- NVIDIA 401(K) PLAN 29145 (client 000732754): current employer since ~Sept 2026. Also NVIDIA HSA and an Amazon Stock Plan entry.

## 2026 IRS limits
- 402(g) employee deferral: $24,500 across ALL employers' plans combined (pre-tax + Roth).
- Catch-up 50+: $8,000 (not applicable to Jerome).
- 415(c) annual additions: $72,000 per unrelated employer's plan (employee + after-tax + employer).

## History
- 2026-10-08: pre-tax deferrals $27,050 ($24,500 Amazon through May 5; $2,550 NVIDIA Sept). Excess $2,550. NVIDIA deferrals stopped Oct 1, 2026. Fix: excess-deferral refund (plus earnings) from the NVIDIA plan before April 15, 2027; excess is 2026 income, earnings 2027 income; related match likely forfeited.
- 2026-10-08: NVIDIA plan 29145 has no excess-deferral form or online option in NetBenefits; SPD says to tell the Plan Administrator about outside-plan deferrals and they will return the excess. Request by phone: Fidelity 1-800-835-5097 (SPD) or Benefit Center 800-890-4015, Mon-Fri 8:30am-8pm ET, or NetBenefits chat. SPD saved at /home/box/Downloads/NVIDIA_29145_SPD.pdf.
