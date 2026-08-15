#!/usr/bin/env python3
"""
Retrieve relevant R2Memory hits via keyword + Amazon Titan embeddings.

Default conversations: chat_shared_ops + chat_grok_build + chat_agent_ops

Examples:
  python3 r2_retrieve.py "always commit and push"
  python3 r2_retrieve.py --json --used 1 "occupancy check-in"
  python3 r2_retrieve.py --check "remember our preference"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from r2_titan_lib import (  # noqa: E402
    AGENT_CONV,
    DEFAULT_CONV,
    SHARED_CONV,
    default_retrieve_conversations,
    needs_retrieval,
    retrieve_relevant,
)


def main() -> int:
    p = argparse.ArgumentParser(description="R2Memory Titan+keyword retrieve")
    p.add_argument("query", nargs="+", help="Search query")
    p.add_argument(
        "-c",
        "--conversation",
        action="append",
        dest="conversations",
        help="Conversation id (repeatable). Default: shared+grok+agent_ops",
    )
    p.add_argument("-k", "--top-k", type=int, default=6)
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--used",
        type=int,
        choices=(0, 1),
        default=None,
        help="Mark metric usedInAnswer 0/1 for eval",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Only print whether needs_retrieval(query) is true",
    )
    args = p.parse_args()
    query = " ".join(args.query).strip()
    if not query:
        print("empty query", file=sys.stderr)
        return 2

    if args.check:
        hit = needs_retrieval(query)
        print("needs_retrieval=yes" if hit else "needs_retrieval=no")
        return 0 if hit else 1

    convs = args.conversations or default_retrieve_conversations()
    used = None if args.used is None else bool(args.used)
    result = retrieve_relevant(query, conversation_ids=convs, top_k=args.top_k, used_in_answer=used)

    if args.json:
        slim = dict(result)
        slim["hits"] = [{k: v for k, v in h.items() if k != "embedding"} for h in (result.get("hits") or [])]
        print(json.dumps(slim, indent=2, ensure_ascii=False))
        return 0

    method = result.get("method") or "none"
    print(
        f"# method={method}  hits={len(result.get('hits') or [])}  ms={result.get('ms')}  "
        f"convs={','.join(convs)}",
        file=sys.stderr,
    )
    print(result.get("text") or "(no hits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
