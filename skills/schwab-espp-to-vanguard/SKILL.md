---
name: schwab-espp-to-vanguard
description: >-
  Use this when moving NVDA ESPP/RSU shares from Schwab Equity Awards (Equity
  Award Center) to Vanguard: EAC-to-brokerage share transfer, proof documents
  Vanguard needs for an in-kind ACATS, and the Schwab/Vanguard bot handoff.
---
# Schwab Equity Awards → Vanguard (in-kind)

Owned by the **Charles Schwab** bot (Schwab side) and **Vanguard** bot (Vanguard side). Read with the `schwab` skill. Titan retrieve first; append + always-push after.

## Key facts (learned 2026-10-07)
- ESPP/vested shares live in the **Equity Award Center (EAC)**, NOT in the linked brokerage account. Brokerage **Individual …650 (75590650)** shows $0 until shares are moved.
- An ACATS against 75590650 finds nothing unless shares were first moved EAC → brokerage.
- Schwab Transfer & Pay has **no outbound ACATS**. Vanguard pulls it from `investor.vanguard.com/account-transfer`.
- Unvested RSUs cannot move; only owned/vested shares.

## Steps
1. **Sign in** (`schwab` skill): Login ID is pre-filled. Password is in SSM `/schwab/password` (us-east-1). Browser helpers will not type passwords, and the Secure Form fails on client.schwab.com (host unknown), so use **request_box_help** for login. If the user gives a new password, overwrite SSM with `aws ssm put-parameter --overwrite --type SecureString` (never echo it).
2. **Check where shares are:** Accounts > Equity Awards shows owned shares, unvested awards, and cash; Accounts > Positions (Individual …650) shows brokerage holdings.
3. **Move EAC → brokerage:** Equity Awards > **Transfer Shares**. Source is the owned ESPP lots, the quantity is all owned shares, and the destination is the linked Schwab brokerage …650 (internal option, not DTC/outside broker). Stop at review, show the user every detail, and submit only after an explicit yes.
4. **Wait for settlement**, then confirm the shares show in Positions for …650.
5. **Proof docs for Vanguard** (save under `/workspace/vanguard-acats/`, read-only, never send):
   - Monthly statement: Accounts > Statements & Tax Forms. Pick the account, tick ALL doc types, Last 10 years. A new brokerage may have none yet. EAC shows only trade confirms.
   - Equity Awards page via Ctrl+P > Save as PDF after clicking **View Account Number**, which shows the full number unmasked on every page, plus holdings and date. No owner name.
   - ESPP Purchase Confirmation PDF has name, address, and shares, but no account number.
   - Account Details > **Generate a Balance Letter** (no mail/send) fails when the balance is $0, so run it after step 4.
   - Fallback: Schwab Stock Plan Services 800-654-2593 for a statement.
6. **Hand off to Vanguard bot** with the file paths, the full account number, the share count, and what each doc shows or lacks (name / type / number / holdings / date).

## Browser notes
- Schwab pages often time out for browser tools; direct screen clicks work.
- Do not resume a blocked computerUse; dispatch a new narrow task.
- One Schwab tab; close extras.

## Do not
- Submit any transfer without the user's explicit yes on the review details.
- Paste/echo passwords; screenshot with password visible.
- Start outbound ACATS from Schwab.
