#!/usr/bin/env python3
"""
Embed the compact skill + topic catalog into Titan conversation chat_catalog.

Short cards only — never the full SKILL.md body. Rebuilds the index in place
so INDEX_MAX eviction cannot drop the catalog.

  python3 r2_index_catalog.py
  python3 r2_index_catalog.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path.home() / "localGrokSkills" / "scripts"))

from resolve_skill import list_skills  # noqa: E402
from r2_titan_lib import (  # noqa: E402
    CATALOG_CONV,
    local_root,
    now_iso,
    replace_catalog_index,
)
from topic_catalog import TOPICS, catalog_source_hash  # noqa: E402


def _frontmatter_description(text: str) -> str:
    if not text.startswith("---"):
        return text.split("\n", 1)[0][:400]
    end = text.find("\n---", 3)
    if end < 0:
        return text[:400]
    block = text[3:end]
    if "description:" not in block:
        return ""
    after = block.split("description:", 1)[1]
    lines = []
    for line in after.splitlines():
        if line.startswith("name:") or line.startswith("metadata:"):
            break
        lines.append(line.strip().lstrip(">").strip())
    return " ".join(x for x in lines if x)[:500]


def skill_source_hash() -> str:
    parts = [catalog_source_hash()]
    for row in list_skills(kind="user"):
        p = Path(row["path"])
        try:
            body = p.read_text(encoding="utf-8")[:2000]
            parts.append(f"{row['name']}|{p.stat().st_mtime_ns}|{body}")
        except OSError:
            parts.append(row["name"])
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def stamp_path() -> Path:
    p = local_root() / "context" / "chat-archive" / CATALOG_CONV
    p.mkdir(parents=True, exist_ok=True)
    return p / "stamp.json"


def load_stamp() -> dict:
    path = stamp_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_stamp(doc: dict) -> None:
    stamp_path().write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def build_cards() -> list[dict]:
    cards: list[dict] = []
    for row in list_skills(kind="user"):
        try:
            desc = _frontmatter_description(Path(row["path"]).read_text(encoding="utf-8"))
        except OSError:
            desc = ""
        text = (
            f"SKILL CARD\nname: {row['name']}\npath: {row['path']}\n"
            f"kind: user\nload: read this path only when the topic matches — do not load every skill.\n"
            f"description: {desc}"
        )
        cards.append({"id": f"skill_{row['name']}", "text": text})

    for t in TOPICS:
        text = (
            f"TOPIC CARD\nid: {t['id']}\nretrieve: YES\n"
            f"load_skills: {', '.join(t['skills'])}\n"
            f"when: {t['when']}\n"
            f"title: {t['title']}\n"
            "Use r2_retrieve / memory gate; then read only those SKILL.md files."
        )
        cards.append({"id": f"topic_{t['id']}", "text": text})
    return cards


def catalog_is_stale() -> bool:
    stamp = load_stamp()
    return stamp.get("hash") != skill_source_hash()


def refresh_catalog(*, force: bool = False, dry_run: bool = False) -> dict:
    digest = skill_source_hash()
    if not force and not catalog_is_stale():
        return {"wrote": False, "reason": "fresh", "hash": digest, "cards": 0}
    cards = build_cards()
    if dry_run:
        return {"wrote": False, "reason": "dry_run", "hash": digest, "cards": len(cards)}
    out = replace_catalog_index(cards)
    save_stamp({"hash": digest, "at": now_iso(), "cards": len(cards), "conversationId": CATALOG_CONV})
    out["hash"] = digest
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Embed skill+topic catalog into chat_catalog")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = refresh_catalog(force=args.force, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(
            f"catalog wrote={out.get('wrote')} reason={out.get('reason')} "
            f"cards={out.get('cards')} hash={out.get('hash')}"
        )
        if out.get("errors"):
            print("errors:", out["errors"], file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
