---
name: box-bootstrap
description: >
  AUTO-RUN when aws, grok, PATH, or ~/.grok/skills is missing/broken on the shared
  box (including after Update Grok Bot's Computer). Restores AWS CLI, grok CLI,
  localGrokSkills symlink, and PATH. Also use for explicit "bootstrap the box" asks.
---

# Box bootstrap (auto when tooling is missing)

## Standing rule (Jerome — HARD)

**Do not ask Jerome before restoring.** If any of these fail on the shared Linux box,
**immediately** run the bootstrap script (idempotent), then continue the original task:

- `aws` missing from PATH, or `aws --version` fails
- `grok` missing from PATH, or `grok --version` fails
- `~/.local/bin` / `~/.grok/bin` not on PATH when those binaries live there
- `~/.grok/skills` missing, not a symlink, or not pointing at `localGrokSkills/skills`
- `aws sts get-caller-identity` fails after a fresh Update Computer (try bootstrap once; if still failing, report chicken-egg)

Triggers include: post–[Update Grok Bot's Computer](grokbot://app/v1/settings?id=update-computer),
command-not-found, AccessDenied that looks like no CLI, or Titan/r2-memory scripts
unreachable because skills link is broken.

Never tell Jerome to use **Reset Computer**. Prefer Update + this bootstrap.

Mention in chat only briefly if you actually ran it (“restored CLIs via box-bootstrap”).

## One command

```bash
bash ~/.grok/skills/box-bootstrap/scripts/bootstrap_box_clis.sh
```

If `~/.grok/skills` is broken and that path is gone, use the workspace copy:

```bash
bash /workspace/localGrokSkills/skills/box-bootstrap/scripts/bootstrap_box_clis.sh
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

- Skill `grok-cli-only` (auto-bootstrap + Titan retrieve → grok headless → append)
- `/home/box/reference/debugging-the-box.md` (Update vs Reset)
- `/home/box/reference/post-update-bootstrap.md` (short pointer)
