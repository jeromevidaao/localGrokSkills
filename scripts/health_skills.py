#!/usr/bin/env python3
"""Fast skill-load health check. Warns; exits 0 so SessionStart never blocks.

Catches the class of failure: empty bundled dirs, missing SKILL.md, unreadable
frontmatter. CI uses check_skills.py (hard-fail) for user skills.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_skill import bundled_missing_skill_md, list_skills  # noqa: E402


def main() -> int:
    rows = list_skills()
    user_n = sum(1 for r in rows if r["kind"] == "user")
    bundled_n = sum(1 for r in rows if r["kind"] == "bundled")
    missing = bundled_missing_skill_md()
    print(f"skills loadable: {len(rows)} (user={user_n} bundled={bundled_n})")
    if missing:
        print(
            f"WARN bundled dirs with no SKILL.md (TUI may say a skill failed to load): "
            f"{', '.join(missing)}"
        )
        print("Ignore them in ~/.grok/config.toml [skills] ignore, or add a SKILL.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
