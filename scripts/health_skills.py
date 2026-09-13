#!/usr/bin/env python3
"""Fast skill-load health check. Warns; exits 0 so SessionStart never blocks.

Empty bundled dirs (no SKILL.md) make the TUI say "Read N skill · M failed".
This script:

1. Writes a tiny placeholder SKILL.md into those bundled dirs so a scan
   cannot fail even if ignore is skipped.
2. Unions those paths (tilde + absolute) plus deprecated aliases into
   ~/.grok/config.toml [skills] ignore, and their names into disabled.
3. Symlinks bundled skills into ~/localGrokSkills/skills (gitignored) so
   ~/.grok/skills/<bundled-name>/SKILL.md resolves. Agents that assume the
   user-skills path (e.g. long-running-background-tasks) no longer 1-fail.

CI uses check_skills.py (hard-fail) for user skills.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_skill import BUNDLED_SKILLS, USER_SKILLS, bundled_missing_skill_md, list_skills  # noqa: E402

GROK_HOME = Path(os.environ.get("GROK_HOME", Path.home() / ".grok")).expanduser()
CONFIG_TOML = GROK_HOME / "config.toml"

# Deprecated user skill whose description used to point at a non-skill directory
# (~/.cleaningbutton/r2-memory). Hide it so the TUI never auto-invokes it.
DEPRECATED_IGNORE = ["~/.grok/skills/ai-context"]
DEPRECATED_NAMES = ["ai-context"]

PLACEHOLDER_SKILL = """\
---
name: {name}
description: Internal Grok library (not a user skill). Hidden via [skills] ignore.
user-invocable: false
disable-model-invocation: true
---

Internal Grok library folder. Not invocable. Placeholder so TUI skill
discovery does not fail with "Read N skill · M failed".
"""

GITIGNORE_HEADER = """\
# Bundled skill aliases created by scripts/health_skills.py.
# Do not commit these symlinks — CI has no ~/.grok/bundled tree.
"""


def required_ignore_paths(missing: list[str] | None = None) -> list[str]:
    names = bundled_missing_skill_md() if missing is None else missing
    paths: list[str] = []
    for n in names:
        paths.append(f"~/.grok/bundled/skills/{n}")
        paths.append(str((GROK_HOME / "bundled" / "skills" / n).expanduser().resolve()))
    paths.extend(DEPRECATED_IGNORE)
    ai = (Path.home() / ".grok" / "skills" / "ai-context").resolve()
    paths.append(str(ai))
    # stable unique, keep first-seen order
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def required_disabled_names(missing: list[str] | None = None) -> list[str]:
    names = bundled_missing_skill_md() if missing is None else list(missing)
    for n in DEPRECATED_NAMES:
        if n not in names:
            names.append(n)
    return names


def _parse_quoted_list(blob: str) -> list[str]:
    return re.findall(r'"([^"]*)"', blob)


def _format_list(key: str, values: list[str]) -> str:
    if not values:
        return f"{key} = []"
    inner = ",\n".join(f'  "{v}"' for v in values)
    return f"{key} = [\n{inner},\n]"


def upsert_skills_list(config_text: str, key: str, required: list[str]) -> tuple[str, list[str]]:
    """Union `required` into [skills] <key>. Returns (new_text, newly_added)."""
    required = list(dict.fromkeys(required))
    skills_m = re.search(r"(?m)^\[skills\][ \t]*\n", config_text)
    if not skills_m:
        block = _format_list(key, required)
        addition = "\n[skills]\n" + block + "\n"
        text = config_text if config_text.endswith("\n") or not config_text else config_text + "\n"
        return text + addition, required

    after = skills_m.end()
    next_table = re.search(r"(?m)^\[", config_text[after:])
    sect_end = after + next_table.start() if next_table else len(config_text)
    section = config_text[after:sect_end]

    ignore_m = re.search(
        rf"(?ms)^{key}\s*=\s*(\[[^\]]*?\])",
        section,
    )
    if not ignore_m:
        block = _format_list(key, required)
        new_section = block + "\n" + section
        added = required
    else:
        existing = _parse_quoted_list(ignore_m.group(1))
        existing_set = set(existing)
        added = [p for p in required if p not in existing_set]
        merged = existing + added
        block = _format_list(key, merged)
        new_section = section[: ignore_m.start()] + block + section[ignore_m.end() :]
        if not new_section.endswith("\n"):
            new_section += "\n"

    new_text = config_text[:after] + new_section + config_text[sect_end:]
    return new_text, added


def upsert_skills_ignore(config_text: str, required: list[str]) -> tuple[str, list[str]]:
    return upsert_skills_list(config_text, "ignore", required)


def upsert_skills_disabled(config_text: str, required: list[str]) -> tuple[str, list[str]]:
    return upsert_skills_list(config_text, "disabled", required)


def _format_ignore(paths: list[str]) -> str:
    return _format_list("ignore", paths)


def sync_config_ignore(required: list[str], config_path: Path = CONFIG_TOML) -> list[str]:
    """Write required ignore paths into config.toml. Returns newly added paths."""
    if not config_path.is_file():
        return []
    original = config_path.read_text(encoding="utf-8")
    updated, added = upsert_skills_ignore(original, required)
    if added:
        config_path.write_text(updated, encoding="utf-8")
    return added


def sync_config_disabled(required: list[str], config_path: Path = CONFIG_TOML) -> list[str]:
    if not config_path.is_file():
        return []
    original = config_path.read_text(encoding="utf-8")
    updated, added = upsert_skills_disabled(original, required)
    if added:
        config_path.write_text(updated, encoding="utf-8")
    return added


def ensure_bundled_placeholders(missing: list[str] | None = None) -> list[str]:
    """Write a loadable SKILL.md into empty bundled dirs. Returns names written."""
    names = bundled_missing_skill_md() if missing is None else missing
    written: list[str] = []
    for n in names:
        d = BUNDLED_SKILLS / n
        if not d.is_dir():
            continue
        md = d / "SKILL.md"
        if md.is_file():
            continue
        try:
            md.write_text(PLACEHOLDER_SKILL.format(name=n), encoding="utf-8")
            written.append(n)
        except OSError:
            continue
    return written


# Library folders that must never be aliased into ~/.grok/skills (TUI would
# then load them as user skills even when [skills] ignore lists the bundled path).
NEVER_ALIAS = {"shared", "remove-wall-of-text"} | set(DEPRECATED_NAMES)


def bundled_alias_names(skip: set[str] | None = None) -> list[str]:
    """Bundled skills that have SKILL.md and are not ignored placeholders."""
    skip_names = set(skip or []) | NEVER_ALIAS
    names: list[str] = []
    if not BUNDLED_SKILLS.is_dir():
        return names
    for d in sorted(p for p in BUNDLED_SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if d.name in skip_names:
            continue
        if (d / "SKILL.md").is_file():
            names.append(d.name)
    return names


def ensure_bundled_aliases(user_skills: Path = USER_SKILLS) -> list[str]:
    """Symlink bundled skills into the user skills tree (gitignored).

    Makes ~/.grok/skills/<name>/SKILL.md work for bundled skills so a Read
    of that path does not fail.
    """
    created: list[str] = []
    if not user_skills.is_dir() or not BUNDLED_SKILLS.is_dir():
        return created
    for junk in NEVER_ALIAS:
        dest = user_skills / junk
        if dest.is_symlink():
            try:
                dest.unlink()
            except OSError:
                pass
    names = bundled_alias_names()
    gitignore_names: list[str] = []
    for name in names:
        bundled_dir = BUNDLED_SKILLS / name
        dest = user_skills / name
        gitignore_names.append(name)
        if dest.exists() and not dest.is_symlink():
            continue
        target = str(bundled_dir.resolve())
        if dest.is_symlink():
            try:
                current = os.readlink(dest)
            except OSError:
                current = ""
            if current == target:
                continue
            dest.unlink()
        try:
            dest.symlink_to(target)
            created.append(name)
        except OSError:
            continue
    write_skills_gitignore(user_skills, gitignore_names)
    return created


def write_skills_gitignore(user_skills: Path, names: list[str]) -> None:
    gi = user_skills / ".gitignore"
    body = GITIGNORE_HEADER + "".join(f"{n}\n" for n in names)
    try:
        existing = gi.read_text(encoding="utf-8") if gi.is_file() else ""
        if existing != body:
            gi.write_text(body, encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    rows = list_skills()
    user_n = sum(1 for r in rows if r["kind"] == "user")
    bundled_n = sum(1 for r in rows if r["kind"] == "bundled")
    missing = bundled_missing_skill_md()
    print(f"skills loadable: {len(rows)} (user={user_n} bundled={bundled_n})")
    if missing:
        print("empty bundled dirs (no SKILL.md): " + ", ".join(missing))
    try:
        stubs = ensure_bundled_placeholders(missing)
        if stubs:
            print("wrote placeholder SKILL.md: " + ", ".join(stubs))
        aliases = ensure_bundled_aliases()
        if aliases:
            print("aliased bundled skills into ~/.grok/skills: " + ", ".join(aliases))
        else:
            print("bundled skill aliases already in ~/.grok/skills")
        required = required_ignore_paths(missing)
        added = sync_config_ignore(required)
        if added:
            print("updated ~/.grok/config.toml [skills] ignore: " + ", ".join(added))
        else:
            print("[skills] ignore already covers empty bundled dirs + deprecated aliases")
        disabled_added = sync_config_disabled(required_disabled_names(missing))
        if disabled_added:
            print("updated ~/.grok/config.toml [skills] disabled: " + ", ".join(disabled_added))
    except OSError as exc:
        print(f"WARN could not update skill health: {exc}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
