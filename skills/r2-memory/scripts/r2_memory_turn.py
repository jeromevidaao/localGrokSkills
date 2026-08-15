#!/usr/bin/env python3
"""
Buffer Grok Build turns → auto-archive to S3 + Titan after N exchanges.
Skips chitchat; dual-writes standing preferences to decisions.md + chat_agent_ops.

  python3 r2_memory_turn.py append --user "…" --assistant "…"
  python3 r2_memory_turn.py flush --force
  python3 r2_memory_turn.py status
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from r2_titan_lib import (  # noqa: E402
    archive_exchange,
    env_conversation_id,
    env_embed_mode,
    env_flush_every,
    flush_pending,
    load_pending,
    pending_path,
    record_turn_auto,
    safe_conv_id,
)


def main() -> int:
    p = argparse.ArgumentParser(description="R2Memory turn buffer + Titan auto-flush")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("-c", "--conversation", default=None)

    ap = sub.add_parser("append", help="Buffer exchange; skip chitchat; dual-write prefs; auto-flush")
    add_common(ap)
    ap.add_argument("--user", required=True)
    ap.add_argument("--assistant", required=True)
    ap.add_argument("--force-flush", action="store_true")
    ap.add_argument("--no-dual-write", action="store_true")
    ap.add_argument("--json", action="store_true")

    fl = sub.add_parser("flush", help="Flush pending to S3+Titan")
    add_common(fl)
    fl.add_argument("--force", action="store_true")
    fl.add_argument("--json", action="store_true")

    st = sub.add_parser("status", help="Pending buffer status")
    add_common(st)
    st.add_argument("--json", action="store_true")

    ar = sub.add_parser("archive-now", help="Archive one exchange immediately")
    add_common(ar)
    ar.add_argument("--user", required=True)
    ar.add_argument("--assistant", required=True)
    ar.add_argument("--json", action="store_true")

    args = p.parse_args()
    cid = args.conversation or env_conversation_id()

    if args.cmd == "append":
        out = record_turn_auto(
            args.user,
            args.assistant,
            conversation_id=cid,
            force_flush=bool(args.force_flush),
            dual_write=not args.no_dual_write,
        )
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            a, f, d = out["append"], out["flush"], out.get("decision") or {}
            if a.get("skipped"):
                print(f"skipped chitchat  pending={a.get('pending')}/{a.get('flushEvery')}  conv={safe_conv_id(cid)}")
            else:
                print(
                    f"pending={a['pending']}/{a['flushEvery']}  flushed={f.get('flushed', 0)}  "
                    f"reason={f.get('reason', 'ok')}  embed={f.get('embedMode', env_embed_mode())}  "
                    f"conv={safe_conv_id(cid)}"
                )
            if d.get("wrote"):
                print(f"decision dual-write: decisionsMd={d.get('decisionsMd')} agentIndex={d.get('agentIndex')}")
            if f.get("errors"):
                print("errors:", f["errors"], file=sys.stderr)
                return 1
        return 0

    if args.cmd == "flush":
        out = flush_pending(conversation_id=cid, force=bool(args.force))
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(
                f"flushed={out.get('flushed')}  pending={out.get('pending')}  "
                f"reason={out.get('reason', 'ok')}  embed={out.get('embedMode')}  conv={out.get('conversationId')}"
            )
            if out.get("errors"):
                print("errors:", out["errors"], file=sys.stderr)
                return 1
        return 0

    if args.cmd == "status":
        pending = load_pending(cid)
        out = {
            "conversationId": safe_conv_id(cid),
            "pending": len(pending),
            "flushEvery": env_flush_every(),
            "embedMode": env_embed_mode(),
            "pendingPath": str(pending_path(cid)),
        }
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(
                f"conv={out['conversationId']}  pending={out['pending']}/{out['flushEvery']}  "
                f"embed={out['embedMode']}  path={out['pendingPath']}"
            )
        return 0

    if args.cmd == "archive-now":
        tid = archive_exchange(
            conversation_id=cid,
            user_message=args.user,
            assistant_reply=args.assistant,
            source="grok_build",
        )
        out = {"turnId": tid, "conversationId": safe_conv_id(cid), "embedMode": env_embed_mode()}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"archived turnId={tid} conv={safe_conv_id(cid)} embed={env_embed_mode()}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
