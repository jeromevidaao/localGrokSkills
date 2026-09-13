---
name: mychart-medical
description: >
  Use this whenever Jerome Ansia asks about MyChart, Overlake messages, test
  results, appointments, or medical portal login. Read first on every MyChart
  conversation; update and push after new learnings.
---

# MyChart — Medical (Overlake)

Standing playbook for the **MyChart - Medical** Grok Bot.
On every Jerome message: **Titan retrieve first**, then read this skill.
After the conversation (or any correction), **update this skill**,
**append the turn to Titan**, and **commit + push immediately**.

Related: `r2-memory` (Titan retrieve/append), `always-push`.

Repo: `jeromevidaao/localGrokSkills` — path `skills/mychart-medical/SKILL.md`.
On the box: `/workspace/localGrokSkills` (`~/.grok/skills` → `skills/`).

## Portal

| Item | Value |
|------|--------|
| Health system | Overlake Hospital Medical Center (Bellevue, WA) |
| Login URL | https://mychart.overlakehospital.org/MyChart/Authentication/Login |
| Home / messages deep link | https://mychart.overlakehospital.org/MyChart//inside.asp?mode=messages&mbox=1 |
| Alert email | donotreply@overlakehospital.org |
| Patient | Jerome Ansia |

## Session longevity

Jerome wants the Overlake MyChart session kept for the **longest** the portal allows.

1. Prefer the persistent box Chrome profile (do not use a temporary/incognito/private window).
2. On login, enable any **Stay signed in** / **Remember me** / **Keep me logged in** checkbox if present.
3. Do not clear site cookies, site data, or Chrome profile for `mychart.overlakehospital.org` unless Jerome asks or login is broken.
4. Avoid logging out after a task — leave the session open so the next run reuses it.
5. If MyChart forces re-auth, re-login with SSM (or in-chat form) and again opt into the longest-lived session option.

## Hard rules

1. **Login credentials:** prefer an existing signed-in Chrome session on this computer.
   If signed out, fetch SSM SecureString params:
   - `/mychart/username`
   - `/mychart/password`
   Never write those values to disk, git, chat, or Titan.
   If SSM params are missing, open the login page and use `request_user_form`
   (auth) so Jerome types once into the live page — never ask him to paste
   credentials in chat. After a successful form login, tell him to store the
   pair in SSM under those paths (`GrokBotTitanAccess` v6 can PutParameter).
2. **Never screenshot password fields** after a secret fill. Use structured
   snapshots only; then click Sign in via the browser subagent.
3. **2FA / passkey / captcha:** hand the box with `request_box_help` — do not
   ask Jerome to paste codes in chat unless using `request_user_form` for OTP
   with a live target.
4. **PHI care:** when relaying messages or results to Jerome in chat, quote
   accurately and briefly. Do not post MyChart content to other agents, Slack,
   email, or group rooms unless he explicitly asks.
5. **Always commit + push this skill:** any edit under
   `skills/mychart-medical/` → always-push (public → `git push` `main` → CI
   green → private). Never ask "want me to push?".
6. **Titan R2Memory:** retrieve before answering; append after the turn.
   Bucket: `cleaningbutton-ai-context-us-east-1`. Scripts:
   `/workspace/localGrokSkills/skills/r2-memory/scripts/`.

## Common tasks

### Read new messages / test-result alerts

1. Open MyChart (session or login as above).
2. Go to Messages (menu or
   `https://mychart.overlakehospital.org/MyChart//inside.asp?mode=messages&mbox=1`).
3. Open the newest unread item.
4. Report to Jerome: sender/date, subject, full body summary, any action needed
   (call provider, reply in MyChart, appointment).
5. For "new test result" emails: open the linked result in Results (not only
   the email body) and report the result name, date, and values/comments
   shown — note if provider review is still pending.

### Appointments / labs / refill

Follow the same login path, then use the matching MyChart menu. Prefer deep
links when known; otherwise navigate from the signed-in home.

## SSM status (keep current)

- **Live paths:** `/mychart/username` and `/mychart/password` (SecureString).
  Confirmed present 2026-09-10 for Overlake MyChart.
- Fetch at use time: `aws ssm get-parameter --name … --with-decryption`.
  Never write values to disk, git, chat, or Titan.


## Learnings log

- **2026-09-10:** First run. Jerome wants Overlake MyChart messages/results
  pulled for him; skill lives in `localGrokSkills`; keep improving after each
  real session. Email sample was a test-result alert (Oct 13, 2025) pointing
  at Overlake Messages.
- **2026-09-10:** Jerome: keep MyChart session saved for the longest the portal allows (Stay signed in + persistent Chrome profile; never log out after a task).
- **2026-09-10:** Jerome confirmed Overlake login is `/mychart/username` + `/mychart/password` in SSM.

