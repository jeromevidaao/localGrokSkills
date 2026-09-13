#!/usr/bin/env python3
"""CI: every user skill has a loadable SKILL.md; Python compiles; no secrets."""
from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}"
    r"|BEGIN (RSA |OPENSSH )?PRIVATE KEY"
    r"|sk-[A-Za-z0-9]{20,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|gho_[A-Za-z0-9]{20,}"
)
SKIP_SUFFIXES = {".yaml", ".yml", ".lock"}
NAME_RE = re.compile(r"^name:\s*['\"]?([a-z0-9][a-z0-9-]{0,62})['\"]?\s*$", re.M)

sys.path.insert(0, str(ROOT / "scripts"))
from resolve_skill import bundled_missing_skill_md, resolve  # noqa: E402


def parse_name(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    block = text[3:end]
    m = NAME_RE.search(block)
    return m.group(1) if m else None


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not SKILLS.is_dir():
        print("FAIL: skills/ missing")
        return 1

    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))
    user_dirs = [d for d in dirs if not d.is_symlink()]
    if not user_dirs:
        print("FAIL: no skills")
        return 1

    for d in user_dirs:
        md = d / "SKILL.md"
        if not md.is_file():
            errors.append(f"{d.name}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        if "description:" not in text:
            errors.append(f"{d.name}: SKILL.md missing description")
        name = parse_name(text)
        if not name:
            errors.append(f"{d.name}: SKILL.md missing/invalid name frontmatter")
        elif name != d.name:
            errors.append(f"{d.name}: frontmatter name={name!r} != directory")
        hit = resolve(d.name)
        if not hit:
            errors.append(f"{d.name}: resolve_skill.py cannot find SKILL.md")
        elif not Path(hit["path"]).is_file():
            errors.append(f"{d.name}: resolved path missing: {hit['path']}")
        if SECRET.search(text):
            errors.append(f"{d.name}: possible secret in SKILL.md")

    for py in SKILLS.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{py.relative_to(ROOT)}: {exc}")

    for path in SKILLS.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if "__pycache__" in path.parts:
            continue
        try:
            blob = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if SECRET.search(blob):
            errors.append(f"{path.relative_to(ROOT)}: possible secret")

    for name in bundled_missing_skill_md():
        warnings.append(f"bundled/{name}: no SKILL.md (TUI may fail to load this skill)")

    if warnings:
        print("WARN")
        for item in warnings:
            print(f" - {item}")

    if errors:
        print("FAIL")
        for item in errors:
            print(f" - {item}")
        return 1

    print(f"OK {len(user_dirs)} user skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
