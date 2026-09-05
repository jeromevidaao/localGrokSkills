#!/usr/bin/env python3
"""Fast skill-load health check. Warns; exits 0 so SessionStart never blocks.

Empty bundled dirs (no SKILL.md) make the TUI say "Read N skill · M failed".
This script unions those paths (plus deprecated aliases) into
~/.grok/config.toml [skills] ignore so discovery skips them.

CI uses check_skills.py (hard-fail) for user skills.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_skill import bundled_missing_skill_md, list_skills  # noqa: E402

GROK_HOME = Path(os.environ.get("GROK_HOME", Path.home() / ".grok")).expanduser()
CONFIG_TOML = GROK_HOME / "config.toml"

# Deprecated user skill whose description used to point at a non-skill directory
# (~/.cleaningbutton/r2-memory). Hide it so the TUI never auto-invokes it.
DEPRECATED_IGNORE = ["~/.grok/skills/ai-context"]


def required_ignore_paths(missing: list[str] | None = None) -> list[str]:
    names = bundled_missing_skill_md() if missing is None else missing
    paths = [f"~/.grok/bundled/skills/{n}" for n in names]
    paths.extend(DEPRECATED_IGNORE)
    # stable unique, keep first-seen order
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _parse_quoted_list(blob: str) -> list[str]:
    return re.findall(r'"([^"]*)"', blob)


def upsert_skills_ignore(config_text: str, required: list[str]) -> tuple[str, list[str]]:
    """Union `required` into [skills] ignore. Returns (new_text, newly_added)."""
    required = list(dict.fromkeys(required))
    skills_m = re.search(r"(?m)^\[skills\][ \t]*\n", config_text)
    if not skills_m:
        block = _format_ignore(required)
        addition = "\n[skills]\n" + block + "\n"
        text = config_text if config_text.endswith("\n") or not config_text else config_text + "\n"
        return text + addition, required

    after = skills_m.end()
    next_table = re.search(r"(?m)^\[", config_text[after:])
    sect_end = after + next_table.start() if next_table else len(config_text)
    section = config_text[after:sect_end]

    ignore_m = re.search(
        r"(?ms)^ignore\s*=\s*(\[[^\]]*?\])",
        section,
    )
    if not ignore_m:
        block = _format_ignore(required)
        new_section = block + "\n" + section
        added = required
    else:
        existing = _parse_quoted_list(ignore_m.group(1))
        existing_set = set(existing)
        added = [p for p in required if p not in existing_set]
        merged = existing + added
        block = _format_ignore(merged)
        new_section = section[: ignore_m.start()] + block + section[ignore_m.end() :]
        # keep a trailing newline if we ate one from the original assignment
        if not new_section.endswith("\n"):
            new_section += "\n"

    new_text = config_text[:after] + new_section + config_text[sect_end:]
    return new_text, added


def _format_ignore(paths: list[str]) -> str:
    if not paths:
        return "ignore = []"
    inner = ",\n".join(f'  "{p}"' for p in paths)
    return f"ignore = [\n{inner},\n]"


def sync_config_ignore(required: list[str], config_path: Path = CONFIG_TOML) -> list[str]:
    """Write required ignore paths into config.toml. Returns newly added paths."""
    if not config_path.is_file():
        return []
    original = config_path.read_text(encoding="utf-8")
    updated, added = upsert_skills_ignore(original, required)
    if added:
        config_path.write_text(updated, encoding="utf-8")
    return added


def main() -> int:
    rows = list_skills()
    user_n = sum(1 for r in rows if r["kind"] == "user")
    bundled_n = sum(1 for r in rows if r["kind"] == "bundled")
    missing = bundled_missing_skill_md()
    required = required_ignore_paths(missing)
    print(f"skills loadable: {len(rows)} (user={user_n} bundled={bundled_n})")
    if missing:
        print(
            "empty bundled dirs (no SKILL.md): " + ", ".join(missing)
        )
    try:
        added = sync_config_ignore(required)
    except OSError as exc:
        print(f"WARN could not update {CONFIG_TOML}: {exc}")
        return 0
    if added:
        print("updated ~/.grok/config.toml [skills] ignore: " + ", ".join(added))
    else:
        print("[skills] ignore already covers empty bundled dirs + deprecated aliases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
