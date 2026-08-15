#!/usr/bin/env python3
"""CI: every skill has SKILL.md + description; Python compiles; no obvious secrets."""
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


def main() -> int:
    errors: list[str] = []
    if not SKILLS.is_dir():
        print("FAIL: skills/ missing")
        return 1

    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not dirs:
        print("FAIL: no skills")
        return 1

    for d in dirs:
        md = d / "SKILL.md"
        if not md.is_file():
            errors.append(f"{d.name}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        if "description:" not in text:
            errors.append(f"{d.name}: SKILL.md missing description")
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

    if errors:
        print("FAIL")
        for item in errors:
            print(f" - {item}")
        return 1

    print(f"OK {len(dirs)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
