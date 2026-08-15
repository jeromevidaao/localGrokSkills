#!/usr/bin/env python3
"""
Session-start R2Memory bootstrap (improvement #8).

Pulls file mirror, runs standing-preference Titan retrieve, prints decisions head.
Agents MUST run this at the start of CleaningButton / R2 work.

  python3 r2_memory_bootstrap.py
  python3 r2_memory_bootstrap.py --no-pull --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from r2_titan_lib import bootstrap_session  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="R2Memory session bootstrap")
    p.add_argument("--no-pull", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--query", default=None, help="Override standing-pref query")
    args = p.parse_args()

    out = bootstrap_session(run_pull=not args.no_pull, standing_query=args.query)
    if args.json:
        print(json.dumps({k: v for k, v in out.items() if k != "decisionsHead"}, indent=2))
        print("--- decisions.md ---")
        print(out.get("decisionsHead") or "(empty)")
        return 0

    print("# R2Memory bootstrap")
    print(f"conversations: {', '.join(out.get('conversations') or [])}")
    print(f"embedMode={out.get('embedMode')}  pending={out.get('pendingTurns')}/{out.get('flushEvery')}")
    if out.get("pull"):
        print(f"pull: {out['pull'][:200]}")
    print(f"standing retrieve: method={out.get('retrieveMethod')} hits={out.get('retrieveHits')}")
    print()
    if out.get("retrieveText"):
        print(out["retrieveText"])
        print()
    print("## decisions.md (head/tail)")
    print(out.get("decisionsHead") or "(empty — pull may have failed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
