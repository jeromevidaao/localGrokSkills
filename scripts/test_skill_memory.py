#!/usr/bin/env python3
"""No-AWS tests: skill resolve + when-to-retrieve topic map."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "r2-memory" / "scripts"))

from health_skills import (  # noqa: E402
    ensure_bundled_aliases,
    required_disabled_names,
    required_ignore_paths,
    upsert_skills_disabled,
    upsert_skills_ignore,
)
from resolve_skill import bundled_missing_skill_md, resolve  # noqa: E402
from topic_catalog import needs_retrieval, skills_for_message, match_topics  # noqa: E402


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL {msg}")


def main() -> int:
    r2 = resolve("r2-memory")
    check(r2 is not None and r2["kind"] == "user", "resolve r2-memory")
    check(Path(r2["path"]).is_file(), "r2-memory path exists")

    check(resolve("this-skill-does-not-exist-xyz") is None, "missing skill")

    missing = bundled_missing_skill_md()
    bundled_root = Path.home() / ".grok" / "bundled" / "skills"
    if bundled_root.is_dir():
        for n in ("remove-wall-of-text", "shared"):
            d = bundled_root / n
            if d.is_dir() and not (d / "SKILL.md").is_file():
                check(n in missing, f"empty bundled dir detected: {missing}")
        bundled = resolve("skill-design-principles")
        check(bundled is not None, "resolve skill-design-principles")
        real = str(Path(bundled["path"]).resolve())
        check(
            real.endswith("bundled/skills/skill-design-principles/SKILL.md"),
            real,
        )
    else:
        check(resolve("skill-design-principles") is None, "no bundled skills on CI")

    sample = '[cli]\ninstaller = "internal"\n\n[skills]\nignore = ["~/.grok/bundled/skills/remove-wall-of-text"]\npaths = []\n'
    updated, added = upsert_skills_ignore(
        sample,
        [
            "~/.grok/bundled/skills/remove-wall-of-text",
            "~/.grok/bundled/skills/shared",
            "~/.grok/skills/ai-context",
        ],
    )
    check("~/.grok/bundled/skills/shared" in added, f"ignore adds shared: {added}")
    check("~/.grok/skills/ai-context" in added, f"ignore adds ai-context: {added}")
    check("~/.grok/bundled/skills/shared" in updated, "updated toml has shared")
    again, added2 = upsert_skills_ignore(updated, ["~/.grok/bundled/skills/shared"])
    check(added2 == [], f"idempotent ignore: {added2}")
    check(again == updated, "second upsert is a no-op")

    dis_sample = '[skills]\ndisabled = []\nignore = []\n'
    dis_updated, dis_added = upsert_skills_disabled(
        dis_sample, ["shared", "remove-wall-of-text", "ai-context"]
    )
    check("shared" in dis_added, f"disabled adds shared: {dis_added}")
    check('disabled = [\n  "shared",' in dis_updated, dis_updated)

    # Placeholders make bundled_missing_skill_md() empty; ignore/disable must
    # still pin library dirs so a config rewrite cannot un-hide them.
    always_ignore = required_ignore_paths([])
    check(
        "~/.grok/bundled/skills/shared" in always_ignore,
        f"tilde shared stay ignored after placeholders: {always_ignore}",
    )
    check(
        "~/.grok/bundled/skills/remove-wall-of-text" in always_ignore,
        f"remove-wall-of-text stay ignored: {always_ignore}",
    )
    check("~/.grok/skills/ai-context" in always_ignore, f"ai-context stay ignored: {always_ignore}")
    always_disabled = required_disabled_names([])
    check("shared" in always_disabled, f"empty-missing still disables shared: {always_disabled}")
    check("remove-wall-of-text" in always_disabled, f"disable remove-wall-of-text: {always_disabled}")
    check("ai-context" in always_disabled, f"disable ai-context: {always_disabled}")

    if (Path.home() / ".grok" / "bundled" / "skills" / "long-running-background-tasks" / "SKILL.md").is_file():
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            fake_user = Path(td) / "skills"
            fake_user.mkdir()
            created = ensure_bundled_aliases(user_skills=fake_user)
            check(
                "long-running-background-tasks" in created,
                f"alias long-running-background-tasks: {created}",
            )
            alias = fake_user / "long-running-background-tasks" / "SKILL.md"
            check(alias.is_file(), f"alias SKILL.md missing: {alias}")
            gi = (fake_user / ".gitignore").read_text(encoding="utf-8")
            check("long-running-background-tasks" in gi, gi)

    check(needs_retrieval("hi") is False, "chitchat skip")
    check(needs_retrieval("is unit 2 occupied?") is True, "occupancy retrieves")
    check(needs_retrieval("can they leave the car in the parking spot after checkout?") is True, "parking")
    check(needs_retrieval("HE destination search Manhattan") is True, "homeexchange")
    check(needs_retrieval("Cherry Crest calendar Christmas Oahu") is True, "family travel")
    fam = skills_for_message("fly to Oahu over Cherry Crest winter break")
    check("family-travel" in fam and "home-exchange" in fam, f"family-travel skills {fam}")
    check(needs_retrieval("remember what we decided about push") is True, "memory language")
    check(needs_retrieval("Eval failed on CI required phrases") is True, "harness eval")

    occ = skills_for_message("is unit 2 occupied?")
    check("hospitable" in occ, f"occupancy skills {occ}")
    park = skills_for_message("Cassidy parking after checkout")
    check("guest-messaging-harness" in park, f"parking skills {park}")

    ids = [t["id"] for t in match_topics("always commit and push")]
    check("ship" in ids or "memory" in ids, f"push topics {ids}")

    print("OK test_skill_memory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
