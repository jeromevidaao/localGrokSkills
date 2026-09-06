# API credentials from AWS SSM only

Standing (2026-08-15). Third-party API secrets are **not** stored on disk, in skill files, or on GitHub.

- Fetch at use time: `aws ssm get-parameter --name … --with-decryption` (or the SDK equivalent).
- Never commit tokens, passwords, PATs, or poll secrets. Never put them on a CLI flag (shell history). Never paste them into chat or R2Memory.
- Do not write a local `.env` / token file for HomeExchange, Hospitable, Kumo, or Bellevue Club.

| Integration | SSM |
|---|---|
| Grok API (harness eval + Lambda) | `/grok/api-key` |
| Grok Bot Titan IAM | `/grok/titan-iam-access-key-id`, `/grok/titan-iam-secret-access-key` |
| HomeExchange API | `/homeexchange/bearer-token` |
| HomeExchange login (refresh Lambda only) | `/homeexchange/credentials` |
| Hospitable PAT | `/hospitable/bearer-token` |
| KumoCloud | `/kumocloud/email`, `/kumocloud/password` |
| Bellevue Club | `/bellevue-club/username`, `/bellevue-club/password` |

Grok Bot Titan user `grok-bot-titan` / policy `GrokBotTitanAccess`: S3 `context/*` read+write on `cleaningbutton-ai-context-us-east-1` + Bedrock Titan embed. No SSM, Hospitable, or Lambda.

HomeExchange live calls: skill **`home-exchange`** / `he_api.py`.
