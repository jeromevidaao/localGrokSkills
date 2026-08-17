#!/usr/bin/env python3
"""
Mandatory memory gate (improvement #1).

Run on every user message before answering CleaningButton questions.
If needs_retrieval matches (or --force), prints Titan hits that the agent
MUST use. Exit codes:
  0 — no retrieve required (or retrieve succeeded with hits)
  1 — retrieve required but empty/failed (still print notice)
  2 — usage error

Examples:
  python3 r2_memory_gate.py "always commit and push"
  python3 r2_memory_gate.py --force "unit 2 occupancy"
  python3 r2_memory_gate.py --json "save this in your memory"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from r2_titan_lib import memory_gate, needs_retrieval  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Mandatory R2Memory Titan gate")
    p.add_argument("message", nargs="*", help="User message")
    p.add_argument("--force", action="store_true", help="Always retrieve")
    p.add_argument("-k", "--top-k", type=int, default=6)
    p.add_argument("--json", action="store_true")
    p.add_argument("--topics", action="store_true", help="Print when-to-retrieve topic table and exit")
    args = p.parse_args()

    if args.topics:
        from topic_catalog import format_topics_table

        print(format_topics_table())
        return 0

    msg = " ".join(args.message).strip()
    if not msg:
        print("empty message", file=sys.stderr)
        return 2

    out = memory_gate(msg, force=args.force, top_k=args.top_k)
    topics = ",".join(out.get("topics") or []) or "-"
    skills = ",".join(out.get("skills") or []) or "-"
    if args.json:
        slim = dict(out)
        slim["hits"] = [{k: v for k, v in (h or {}).items() if k != "embedding"} for h in (out.get("hits") or [])]
        print(json.dumps(slim, indent=2, ensure_ascii=False))
    else:
        if not out.get("must_retrieve"):
            print(
                f"# gate: skip (needs_retrieval={needs_retrieval(msg)}) topics={topics} skills={skills}",
                file=sys.stderr,
            )
            print("(no retrieve required)")
            return 0
        print(
            f"# gate: MUST_RETRIEVE topics={topics} skills={skills} "
            f"method={out.get('method')} hits={len(out.get('hits') or [])} ms={out.get('ms')}",
            file=sys.stderr,
        )
        print(out.get("text") or "(no hits — still check decisions.md)")
        if not out.get("hits"):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
