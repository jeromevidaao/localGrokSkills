#!/usr/bin/env python3
"""No-AWS tests: skill resolve + when-to-retrieve topic map."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "r2-memory" / "scripts"))

from resolve_skill import bundled_missing_skill_md, resolve  # noqa: E402
from topic_catalog import needs_retrieval, skills_for_message, match_topics  # noqa: E402


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL {msg}")


def main() -> int:
    r2 = resolve("r2-memory")
    check(r2 is not None and r2["kind"] == "user", "resolve r2-memory")
    check(Path(r2["path"]).is_file(), "r2-memory path exists")

    bundled = resolve("skill-design-principles")
    check(bundled is not None and bundled["kind"] == "bundled", "resolve bundled skill")
    check(bundled["path"].endswith("bundled/skills/skill-design-principles/SKILL.md"), bundled["path"])

    check(resolve("this-skill-does-not-exist-xyz") is None, "missing skill")

    missing = bundled_missing_skill_md()
    check("remove-wall-of-text" in missing, f"empty bundled dir detected: {missing}")

    check(needs_retrieval("hi") is False, "chitchat skip")
    check(needs_retrieval("is unit 2 occupied?") is True, "occupancy retrieves")
    check(needs_retrieval("can they leave the car in the parking spot after checkout?") is True, "parking")
    check(needs_retrieval("HE destination search Manhattan") is True, "homeexchange")
    check(needs_retrieval("remember what we decided about push") is True, "memory language")
    check(needs_retrieval("Eval failed on CI required phrases") is True, "harness eval")

    occ = skills_for_message("is unit 2 occupied?")
    check("hospitable" in occ and "r2" in occ, f"occupancy skills {occ}")
    park = skills_for_message("Cassidy parking after checkout")
    check("guest-messaging-harness" in park, f"parking skills {park}")

    ids = [t["id"] for t in match_topics("always commit and push")]
    check("ship" in ids or "memory" in ids, f"push topics {ids}")

    print("OK test_skill_memory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
