---
name: always-push
description: >
  Standing Jerome mandate: after finishing requested work always commit and git push
  (usually main), watch CI green, never ask "want me to push?". Use on any shipping,
  deploy, commit, push, CI, OTA, or end-of-task for CleaningButton/R2 repos.
---

# Always commit + push (never ask)

## Rule

When work the user asked for is done:

1. `git commit` (clear message)
2. **Before push:** `gh repo edit --visibility public --accept-visibility-change-consequences` (proactive — do not wait for quota to fail)
3. `git push` to tracked remote (`main`) **without asking**
4. `gh run watch` until green (fix + keep public + push until green)
5. **After green:** `gh repo edit --visibility private --accept-visibility-change-consequences`
6. Only then say shipped / OTA / deployed

Jerome does not pay for GitHub. Public minutes run CI; repos stay private at rest.

## Never say

- Want me to push?
- Shall I push / commit?
- Ready to push when you say so
- I can push if you want

## Exceptions

- User explicitly said local-only / do not push
- Force-push, history rewrite, branch delete, shared-state destroy → **do ask**

## Related

- `~/.grok/rules/00-always-commit-push.md`
- `~/.grok/rules/01-local-grok-skills.md`
- Stop hook `~/.grok/hooks/always-commit-push.json`
- User skills repo `~/localGrokSkills` (`jeromevidaao/localGrokSkills`) — SessionStart pulls, Stop auto-commits
- R2Memory decisions.md pinned section
