#!/usr/bin/env python3
"""
Ask R2 (R2Lambda) from the laptop / Grok agent.

Uses AWS credentials (same profile as deploy). Sync-invokes Lambda R2Lambda
in chat mode so the reply includes R2Memory + live Hospitable ops.

Examples:
  python3 ~/.grok/skills/r2/scripts/r2_chat.py "Is unit 2 occupied?"
  python3 ~/.grok/skills/r2/scripts/r2_chat.py --local "What was last month revenue?"
  python3 ~/.grok/skills/r2/scripts/r2_chat.py --diag
  python3 ~/.grok/skills/r2/scripts/r2_chat.py --json "Summarize occupancy"

Env:
  R2_LAMBDA_FUNCTION   default R2Lambda
  R2_JOBS_TABLE        default aiCodePushJobs
  AWS_REGION           default us-east-1
  AWS_PROFILE          optional
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

FUNCTION = os.environ.get("R2_LAMBDA_FUNCTION", "R2Lambda")
REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE = os.environ.get("R2_JOBS_TABLE", "aiCodePushJobs")
SHARED_ID = "chat_shared_ops"
LOCAL_ID = "chat_grok_local"
HISTORY_TURNS = 20
# Chat can load Hospitable + Grok; leave headroom under Lambda 900s
CLI_READ_TIMEOUT = int(os.environ.get("R2_CLI_READ_TIMEOUT", "240"))


def _aws(args: list[str], *, timeout: int | None = 60) -> subprocess.CompletedProcess[str]:
    cmd = ["aws", *args, "--region", REGION, "--output", "json"]
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def ddb_get_messages(conversation_id: str) -> list[dict[str, Any]]:
    """Load recent messages from the shared Dynamo conversation (if any)."""
    r = _aws(
        [
            "dynamodb",
            "get-item",
            "--table-name",
            TABLE,
            "--key",
            json.dumps({"jobId": {"S": conversation_id}}),
            "--projection-expression",
            "messages,#s",
            "--expression-attribute-names",
            json.dumps({"#s": "status"}),
        ],
        timeout=30,
    )
    if r.returncode != 0 or not (r.stdout or "").strip():
        return []
    try:
        item = json.loads(r.stdout).get("Item") or {}
    except json.JSONDecodeError:
        return []
    raw = item.get("messages", {}).get("L") or []
    out: list[dict[str, Any]] = []
    for el in raw:
        m = el.get("M") or {}
        role = (m.get("role") or {}).get("S") or ""
        content = (m.get("content") or {}).get("S") or ""
        if role in ("user", "assistant") and content.strip():
            out.append({"role": role, "content": content})
    return out[-HISTORY_TURNS:]


def invoke_lambda(payload: dict[str, Any]) -> dict[str, Any]:
    out_path = Path(f"/tmp/r2-chat-{uuid.uuid4().hex[:10]}.json")
    payload_path = Path(f"/tmp/r2-payload-{uuid.uuid4().hex[:10]}.json")
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    try:
        r = _aws(
            [
                "lambda",
                "invoke",
                "--function-name",
                FUNCTION,
                "--cli-binary-format",
                "raw-in-base64-out",
                "--cli-read-timeout",
                str(CLI_READ_TIMEOUT),
                "--payload",
                f"fileb://{payload_path}",
                str(out_path),
            ],
            timeout=CLI_READ_TIMEOUT + 30,
        )
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()
            raise RuntimeError(f"lambda invoke failed: {err}")
        meta = {}
        try:
            meta = json.loads(r.stdout) if r.stdout.strip() else {}
        except json.JSONDecodeError:
            pass
        if meta.get("FunctionError"):
            body = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            raise RuntimeError(f"Lambda FunctionError={meta.get('FunctionError')}: {body[:800]}")
        if not out_path.exists():
            raise RuntimeError("lambda invoke produced no output file")
        return json.loads(out_path.read_text(encoding="utf-8"))
    finally:
        try:
            payload_path.unlink(missing_ok=True)
        except Exception:
            pass
        try:
            out_path.unlink(missing_ok=True)
        except Exception:
            pass


def ask_r2(
    message: str,
    *,
    conversation_id: str,
    include_history: bool = True,
    target_repo: str | None = None,
) -> dict[str, Any]:
    history: list[dict[str, Any]] = []
    if include_history:
        history = ddb_get_messages(conversation_id)

    turn_id = f"grok_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    payload: dict[str, Any] = {
        "mode": "chat",
        "conversationId": conversation_id,
        "turnId": turn_id,
        "message": message,
        "history": history,
        "email": "grok-local@cleaningbutton",
    }
    if target_repo:
        payload["targetRepo"] = target_repo

    result = invoke_lambda(payload)
    return result


def diag() -> dict[str, Any]:
    return invoke_lambda({"diag": "github-token", "owner": "jeromevidaao", "repo": "cleaningbutton-android"})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ask R2 (R2Lambda) via AWS Lambda invoke")
    ap.add_argument("message", nargs="*", help="Message to send to R2")
    ap.add_argument(
        "--conversation",
        "-c",
        default=None,
        help=f"Conversation id (default {SHARED_ID}; with --local: {LOCAL_ID})",
    )
    ap.add_argument(
        "--local",
        action="store_true",
        help=(
            f"Use private thread {LOCAL_ID} instead of shared Android/web thread "
            f"({SHARED_ID}). Prefer default shared so history matches phone + website."
        ),
    )
    ap.add_argument(
        "--no-history",
        action="store_true",
        help="Do not load prior Dynamo messages into the prompt",
    )
    ap.add_argument("--repo", default=None, help="Optional targetRepo owner/name for context")
    ap.add_argument("--diag", action="store_true", help="Run R2Lambda github-token diagnostic")
    ap.add_argument("--json", action="store_true", help="Print full JSON response")
    args = ap.parse_args(argv)

    if args.diag:
        try:
            out = diag()
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"worker={out.get('worker')} intent={out.get('intent')} ok={out.get('ok')}")
            if out.get("probe"):
                print(f"probe_ok={out['probe'].get('ok')} source={out.get('source')}")
        return 0 if out.get("ok") else 2

    message = " ".join(args.message).strip()
    if not message:
        # Allow stdin
        if not sys.stdin.isatty():
            message = sys.stdin.read().strip()
    if not message:
        ap.print_help()
        print("\nerror: message required", file=sys.stderr)
        return 2

    if args.conversation:
        cid = args.conversation
    elif args.local:
        cid = LOCAL_ID
    else:
        cid = SHARED_ID

    try:
        out = ask_r2(
            message,
            conversation_id=cid,
            include_history=not args.no_history,
            target_repo=args.repo,
        )
    except subprocess.TimeoutExpired:
        print("error: timed out waiting for R2Lambda (try higher R2_CLI_READ_TIMEOUT)", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 2

    if not out.get("ok"):
        print(f"error: {out.get('error') or out}", file=sys.stderr)
        return 2

    reply = (out.get("reply") or "").strip()
    if not reply:
        print("error: empty reply from R2", file=sys.stderr)
        return 2

    # Human-readable header for the agent transcript
    model = out.get("model") or ""
    print(f"[R2 · {cid}" + (f" · {model}" if model else "") + "]")
    print(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
