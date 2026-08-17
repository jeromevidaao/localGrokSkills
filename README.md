# localGrokSkills

Jerome’s **user Grok skills** (and the hooks/rules that keep them in sync). Portable across laptops.

Live path on this machine: `~/.grok/skills` → `~/localGrokSkills/skills`.

## What syncs

| Path in repo | Installed as |
|---|---|
| `skills/` | `~/.grok/skills` |
| `grok-rules/` | `~/.grok/rules/` |
| `grok-hooks/always-commit-push.json` | `~/.grok/hooks/always-commit-push.json` |
| generated hook | `~/.grok/hooks/local-grok-skills.json` |

Bundled Grok skills (`~/.grok/bundled/skills`) stay with the CLI. They are not in this repo.

## New laptop

```bash
# Grok CLI + gh, logged in as jeromevidaao
gh repo clone jeromevidaao/localGrokSkills ~/localGrokSkills
~/localGrokSkills/install.sh
```

Next Grok session:

- **SessionStart** — `git pull --ff-only` so skills are current
- **Stop / SessionEnd** — if anything under this repo is dirty, commit + public + push + wait CI + private

## Manual sync

```bash
python3 ~/localGrokSkills/scripts/sync.py pull
python3 ~/localGrokSkills/scripts/sync.py commit-push
python3 ~/localGrokSkills/scripts/check_skills.py
python3 ~/localGrokSkills/scripts/test_skill_memory.py
python3 ~/localGrokSkills/scripts/resolve_skill.py --list
```

## Edit a skill

Edit `~/.grok/skills/<name>/SKILL.md` (the symlink). Finish the turn — the Stop hook commits. Or run `sync.py commit-push` yourself. Same always-push mandate as every other Jerome repo.
