# localGrokSkills

User Grok skills for Jerome. `~/.grok/skills` is a symlink here.

## HARD: Always commit + push (never ask)

After finishing requested work: **public → commit → `git push` `main` → CI green → private**.

Never ask “want me to push?”. Exceptions: user said not to, or force-push / destructive git.

Jerome does not pay for GitHub. Public minutes run CI; long-run state is private.

## After editing skills

If you change anything under `skills/`, `grok-hooks/`, `grok-rules/`, or `scripts/`, commit and push this repo. The SessionStart hook pulls; Stop / SessionEnd auto-commit dirty trees. Do not leave skill edits only on disk.

## New laptop

`gh repo clone jeromevidaao/localGrokSkills ~/localGrokSkills && ~/localGrokSkills/install.sh`
