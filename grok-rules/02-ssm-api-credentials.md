# API credentials from AWS SSM only

Standing (2026-08-15). Third-party API secrets are **not** stored on disk, in skill files, or on GitHub.

- Fetch at use time: `aws ssm get-parameter --name … --with-decryption` (or the SDK equivalent).
- Never commit tokens, passwords, PATs, or poll secrets. Never put them on a CLI flag (shell history). Never paste them into chat or R2Memory.
- Do not write a local `.env` / token file for HomeExchange, Hospitable, or Kumo.

| Integration | SSM |
|---|---|
| Grok API (harness eval + Lambda) | `/grok/api-key` |
| HomeExchange API | `/homeexchange/bearer-token` |
| HomeExchange login (refresh Lambda only) | `/homeexchange/credentials` |
| Hospitable PAT | `/hospitable/bearer-token` |
| KumoCloud | `/kumocloud/email`, `/kumocloud/password` |

HomeExchange live calls: skill **`home-exchange`** / `he_api.py`.
