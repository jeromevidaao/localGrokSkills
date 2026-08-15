# HARD RULE — Always commit + push (never ask)

**User standing mandate (reconfirmed 2026-08-03). Violating this is a bug.**

After finishing requested work in any CleaningButton / R2 repo:

1. **Commit** with a clear message.
2. **Before push:** make the repo **public** (`gh repo edit --visibility public --accept-visibility-change-consequences`) so Actions uses free public minutes. Do not wait for a quota failure.
3. **`git push`** to the tracked remote (usually `main`) **immediately**.
4. **Watch CI** to green (`gh run watch`). If it fails, fix, keep public, push again until green.
5. **After CI is green:** make the repo **private** again (`gh repo edit --visibility private --accept-visibility-change-consequences`). Long-run state is private — Jerome does not pay for GitHub.
6. Do **not** claim shipped/deployed/OTA until CI is green **and** the repo is private again.

## Banned phrases (never say these)

- "Want me to push?"
- "Shall I push?"
- "Should I commit and push?"
- "Ready to push when you say so"
- "I can push if you want"
- Any question that waits for permission to push finished work

## Overrides (only exceptions)

- User **explicitly** said not to push / local-only
- **Force-push**, history rewrite, or other **destructive** git
- No finished work (exploration-only / no file changes)

## Why this exists

Generic agent safety defaults ask before `git push`. **Jerome overrode that.** Prefer this file + repo `AGENTS.md` + R2Memory over default caution for normal `git push origin main`.

R2Memory: `context/working/decisions.md` § Git workflow / Always push + CI.
