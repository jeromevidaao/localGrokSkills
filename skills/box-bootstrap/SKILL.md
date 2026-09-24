---
name: box-bootstrap
description: >
  After Update Grok Bot's Computer, restore AWS CLI, grok CLI, localGrokSkills
  symlink, and PATH. Use when CLIs vanished post-update, box bootstrap, or
  "reinstall aws/grok on the shared computer".
---

# Box bootstrap (post–Update Computer)

## When

[Update Grok Bot's Computer](grokbot://app/v1/settings?id=update-computer) keeps
**files and logins** but **does not** keep installed software (apt/npm/pip, CLIs).
Never tell Jerome to use Reset Computer.

## One command

```bash
bash ~/.grok/skills/box-bootstrap/scripts/bootstrap_box_clis.sh
```

Idempotent: safe to re-run; mostly no-op when already healthy.

## What it restores

| Piece | Method |
|---|---|
| `PATH` | `~/.local/bin` + `~/.grok/bin` (session + `~/.bashrc`) |
| AWS CLI | User venv `~/.local/awscli-venv` + symlink `~/.local/bin/aws` (pip `awscli`, matches this box) |
| AWS profile | Reuse `~/.aws` if STS works; ensure profile **`grok-bot-titan`** (account `834917996497`, `us-east-1`); SSM `/grok/titan-iam-access-key-id` + `/grok/titan-iam-secret-access-key` **only** if no valid identity |
| grok CLI | `curl -fsSL https://x.ai/cli/install.sh \| bash` or `grok update` |
| Skills | Clone/pull `jeromevidaao/localGrokSkills` → `/workspace/localGrokSkills`; `install.sh` so `~/.grok/skills` → `…/skills` |
| `gh` | Checks auth; if missing, notes `gh auth login` (no invented tokens) |

Secrets never printed. Credentials file mode 600.

## Chicken-egg

Update **keeps** `~/.aws` and `~/.grok`. Script reinstalls **binaries first**, then
reuses existing creds. SSM fetch needs a working identity — if both CLI and
`~/.aws` are gone, restore credentials manually, then re-run. Prefer Update
over Reset.

## Checklist

Script ends with PASS/FAIL for `aws --version`, `aws sts`, `grok --version`,
skills symlink, and `gh` auth.

## Related

- Skill `grok-cli-only` (Titan retrieve → grok headless → append)
- `/home/box/reference/debugging-the-box.md` (Update vs Reset)
- `/home/box/reference/post-update-bootstrap.md` (short pointer)
