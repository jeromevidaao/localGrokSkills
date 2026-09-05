# Skill resolve + R2Memory (always on)

Grok sees every skill **name + description**. Do **not** load every `SKILL.md`.

## Prevent skill-load failures

- Use the **Absolute path** from the Available Skills list when present.
- Otherwise resolve: `python3 ~/localGrokSkills/scripts/resolve_skill.py <name>`
- Never assume `~/.grok/skills/<name>/SKILL.md`. Bundled skills live in `~/.grok/bundled/skills/`.
- Empty bundled dirs (no `SKILL.md`) break TUI load (status `Read N skill · M failed`). SessionStart `health_skills.py` unions them into `~/.grok/config.toml` `[skills] ignore` (includes `shared` and `remove-wall-of-text`). Deprecated alias `ai-context` is ignored the same way — use **r2-memory**.

## Every real question uses memory

1. `python3 ~/.grok/skills/r2-memory/scripts/r2_memory_gate.py "<user message>"`
2. If `MUST_RETRIEVE`: use the hits. Load **only** the printed `skills=` (resolve path first).
3. After the answer: `r2_memory_turn.py append` so the next question is smarter.

Skip retrieve only for chitchat. Topic table: `r2_memory_gate.py --topics`.

Titan is the search layer for past Q&A, standing prefs, and the skill/topic catalog. Full skill bodies stay on disk until a topic matches.
