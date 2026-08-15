---
name: aws-account
description: >
  Direct AWS account access for CleaningButton via R2Lambda: Cost Explorer
  billing (current + previous month, top services) and STS account identity.
  Use when the user asks about AWS cost, AWS bill, cloud spend, or account ID.
  Prefer /r2 which loads live data through the R2Lambda execution role.
---

# AWS account (via R2)

## What R2 can do

| Capability | Source |
|------------|--------|
| Current month AWS cost (MTD) | Cost Explorer UnblendedCost |
| Previous full month cost | Cost Explorer |
| Top services this month | Cost Explorer GROUP BY SERVICE |
| Account ID / role ARN | STS GetCallerIdentity |

**Read-only.** No create/delete infrastructure from chat.

## Ask

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py "What is our AWS bill this month?"
python3 ~/.grok/skills/r2/scripts/r2_chat.py "How much did AWS cost last month?"
```

Or `/r2 What is our AWS bill this month?`

## Implementation

- R2Lambda `lib/aws-account.js`
- IAM on `aiCodePushRole`: `ce:GetCostAndUsage`, `sts:GetCallerIdentity`
- Intent kind `aws_account` loads only AWS (fast path)

## Not the same as

- Airbnb **revenue** (Hospitable)
- **Cleaning spend** (Dynamo button presses)
- Android **More → AWS Billing** (same CE data via API `act=aws_billing`)
