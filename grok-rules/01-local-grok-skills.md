# localGrokSkills — portable user skills

User Grok skills live in `~/localGrokSkills` (GitHub `jeromevidaao/localGrokSkills`).
`~/.grok/skills` is a symlink to `~/localGrokSkills/skills`.

## Standing

- **Any skill / hook / rule update in this tree must be committed and pushed** (same always-push mandate: public → push → CI green → private).
- **SessionStart** hook pulls `main` (`scripts/sync.py pull`) so a new session has the latest.
- **Stop / SessionEnd** hook auto-commits a dirty tree (`scripts/sync.py commit-push`).
- New laptop: `gh repo clone jeromevidaao/localGrokSkills ~/localGrokSkills && ~/localGrokSkills/install.sh`

Do not leave skill edits only on this machine.
