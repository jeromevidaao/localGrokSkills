#!/usr/bin/env python3
"""Resolve a Grok skill name to its SKILL.md.

User skills:  ~/localGrokSkills/skills/<name>/SKILL.md  (== ~/.grok/skills)
Bundled:      ~/.grok/bundled/skills/<name>/SKILL.md

Never guess ~/.grok/skills/<name> — bundled skills are not there.
User skills win on name collision.

  python3 resolve_skill.py r2-memory
  python3 resolve_skill.py skill-design-principles
  python3 resolve_skill.py --list
  python3 resolve_skill.py --json hospitable
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

USER_SKILLS = Path.home() / "localGrokSkills" / "skills"
BUNDLED_SKILLS = Path.home() / ".grok" / "bundled" / "skills"


def skill_roots() -> list[tuple[str, Path]]:
    return [("user", USER_SKILLS), ("bundled", BUNDLED_SKILLS)]


def resolve(name: str) -> dict[str, str] | None:
    n = (name or "").strip().strip("/")
    if not n or "/" in n or n in (".", ".."):
        return None
    for kind, root in skill_roots():
        path = root / n / "SKILL.md"
        if path.is_file():
            return {"name": n, "path": str(path.resolve()), "kind": kind, "root": str(root)}
    return None


def list_skills(*, kind: str | None = None) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for k, root in skill_roots():
        if kind and k != kind:
            continue
        if not root.is_dir():
            continue
        for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
            md = d / "SKILL.md"
            if not md.is_file():
                continue
            if d.name in found and found[d.name]["kind"] == "user":
                continue
            found[d.name] = {
                "name": d.name,
                "path": str(md.resolve()),
                "kind": k,
                "root": str(root),
            }
    return [found[k] for k in sorted(found)]


def bundled_missing_skill_md() -> list[str]:
    """Top-level bundled dirs that look like skills but have no SKILL.md."""
    skip = {"shared"}
    missing: list[str] = []
    if not BUNDLED_SKILLS.is_dir():
        return missing
    for d in sorted(p for p in BUNDLED_SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if d.name in skip:
            continue
        if not (d / "SKILL.md").is_file():
            missing.append(d.name)
    return missing


def main() -> int:
    p = argparse.ArgumentParser(description="Resolve Grok skill name → SKILL.md path")
    p.add_argument("name", nargs="?", help="Skill name (e.g. r2-memory)")
    p.add_argument("--list", action="store_true", help="List loadable skills")
    p.add_argument("--json", action="store_true")
    p.add_argument("--kind", choices=("user", "bundled"), default=None)
    args = p.parse_args()

    if args.list or not args.name:
        rows = list_skills(kind=args.kind)
        missing = bundled_missing_skill_md() if args.kind != "user" else []
        if args.json:
            print(json.dumps({"skills": rows, "bundledMissingSkillMd": missing}, indent=2))
        else:
            for r in rows:
                print(f"{r['name']:28} {r['kind']:8} {r['path']}")
            if missing:
                print(f"# WARN bundled dirs with no SKILL.md: {', '.join(missing)}", file=sys.stderr)
        if args.name:
            return 0
        if not args.list and not args.name:
            p.print_help()
            return 2
        return 0

    hit = resolve(args.name)
    if not hit:
        print(f"NOT_FOUND {args.name}", file=sys.stderr)
        print(
            "Search roots: ~/localGrokSkills/skills and ~/.grok/bundled/skills",
            file=sys.stderr,
        )
        return 1
    if args.json:
        print(json.dumps(hit, indent=2))
    else:
        print(hit["path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
