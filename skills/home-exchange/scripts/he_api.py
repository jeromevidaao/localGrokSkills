#!/usr/bin/env python3
"""HomeExchange API from this laptop.

Auth is always AWS SSM GetParameter (SecureString). The bearer is held in
memory for this process only — never written to disk, never printed, never
accepted as a CLI flag that would land in shell history as a token value.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

REGION = os.environ.get("AWS_REGION", "us-east-1")
HE_API_BASE = os.environ.get("HE_API_BASE", "https://api.homeexchange.com").rstrip("/")
HE_BEARER_SSM = os.environ.get("HE_BEARER_SSM", "/homeexchange/bearer-token")
HE_REFRESH_FN = os.environ.get("HE_TOKEN_REFRESH_FUNCTION", "he-token-refresh")
HE_WEB_VERSION = os.environ.get("HE_WEB_VERSION", "20.29.1-rc.1")
HE_HOME_ID = os.environ.get("HE_HOME_ID", "3202475")

_token: str | None = None


def _aws(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["aws", *args, "--region", REGION],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def ssm_get(name: str) -> str:
    r = _aws(
        [
            "ssm",
            "get-parameter",
            "--name",
            name,
            "--with-decryption",
            "--query",
            "Parameter.Value",
            "--output",
            "text",
        ]
    )
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().replace("\n", " ")[:240]
        raise RuntimeError(f"SSM get {name} failed: {err or 'unknown'}")
    value = (r.stdout or "").strip()
    if not value or value == "None":
        raise RuntimeError(f"SSM {name} is empty")
    return value


def load_bearer(*, force: bool = False) -> str:
    global _token
    if force:
        _token = None
    if _token:
        return _token
    _token = ssm_get(HE_BEARER_SSM).strip()
    return _token


def redact(text: str) -> str:
    if not text:
        return text
    out = text
    if _token and _token in out:
        out = out.replace(_token, "<redacted-bearer>")
    out = out.replace("Bearer ", "Bearer <redacted> ")
    return out


def invoke_token_refresh() -> None:
    out_path = f"/tmp/he-token-refresh-{os.getpid()}.json"
    r = _aws(
        [
            "lambda",
            "invoke",
            "--function-name",
            HE_REFRESH_FN,
            "--cli-binary-format",
            "raw-in-base64-out",
            "--payload",
            '{"source":"localGrokSkills-he-api"}',
            out_path,
        ],
        timeout=90,
    )
    if r.returncode != 0:
        err = redact((r.stderr or r.stdout or "").strip())[:240]
        raise RuntimeError(f"{HE_REFRESH_FN} invoke failed: {err}")
    try:
        os.unlink(out_path)
    except OSError:
        pass
    load_bearer(force=True)


def he_request(
    method: str,
    path: str,
    body: dict[str, Any] | list[Any] | None = None,
    *,
    retry_401: bool = True,
) -> tuple[int, Any]:
    token = load_bearer()
    url = HE_API_BASE + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method.upper(),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en",
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "he_web_version": HE_WEB_VERSION,
            "origin": "https://www.homeexchange.com",
            "referer": "https://www.homeexchange.com/conversations",
            "User-Agent": "localGrokSkills-home-exchange/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = exc.code
        if status == 401 and retry_401:
            invoke_token_refresh()
            return he_request(method, path, body, retry_401=False)
        raise RuntimeError(f"HE {method} {path} HTTP {status}: {redact(raw)[:400]}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"HE {method} {path} network: {exc.reason}") from None

    parsed: Any = None
    if raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": redact(raw)[:800]}
    if status < 200 or status >= 300:
        raise RuntimeError(f"HE {method} {path} HTTP {status}: {redact(raw)[:400]}")
    return status, parsed


def emit(obj: Any, as_json: bool) -> None:
    if as_json:
        json.dump(obj, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return
    if isinstance(obj, str):
        print(obj)
        return
    print(json.dumps(obj, indent=2, default=str))


def cmd_me(_: argparse.Namespace, as_json: bool) -> int:
    _, data = he_request("GET", "/v1/users/me")
    if as_json:
        emit(data, True)
        return 0
    user = data if isinstance(data, dict) else {}
    emit(
        {
            "id": user.get("id") or (user.get("user") or {}).get("id"),
            "email": user.get("email") or (user.get("user") or {}).get("email"),
            "first_name": user.get("first_name") or (user.get("user") or {}).get("first_name"),
        },
        False,
    )
    return 0


def _peer_name(node: dict[str, Any], self_id: str | None) -> str | None:
    inter = node.get("interlocutor") or {}
    if isinstance(inter, dict) and inter.get("first_name"):
        return str(inter["first_name"])
    for key in ("exchanges", "all_exchanges"):
        items = node.get(key) or []
        if not isinstance(items, list):
            continue
        for ex in items:
            guest = (ex or {}).get("guest") or {}
            gid = str(guest.get("id") or "")
            if self_id and gid == str(self_id):
                continue
            if guest.get("first_name"):
                return str(guest["first_name"])
    return None


def _date_range(node: dict[str, Any]) -> str | None:
    items = node.get("exchanges") or node.get("all_exchanges") or []
    if not isinstance(items, list) or not items:
        return None
    first = items[0] or {}
    start = str(first.get("start_on") or "")[:10]
    end = str(first.get("end_on") or "")[:10]
    if start and end:
        return f"{start} → {end}"
    return None


def cmd_conversations(args: argparse.Namespace, as_json: bool) -> int:
    limit = max(1, min(int(args.limit), 50))
    _, me = he_request("GET", "/v1/users/me")
    self_id = None
    if isinstance(me, dict):
        self_id = me.get("id") or (me.get("user") or {}).get("id")
        if self_id is not None:
            self_id = str(self_id)
    _, data = he_request("GET", f"/v3/conversations/me?limit={limit}")
    conv = ((data or {}).get("data") or {}).get("conversations") or {}
    edges = conv.get("edges") or []
    rows = []
    for edge in edges:
        node = (edge or {}).get("node") or edge or {}
        lm = node.get("last_message") or {}
        rows.append(
            {
                "id": str(node["id"]) if node.get("id") is not None else None,
                "peer": _peer_name(node, self_id),
                "dates": _date_range(node),
                "unread": node.get("unread_messages_count") or 0,
                "last_at": (lm.get("send_at") if isinstance(lm, dict) else None)
                or node.get("updated_at"),
                "last_text": (
                    str(lm.get("content") or "")[:160] if isinstance(lm, dict) else ""
                ),
            }
        )
    emit(
        {"total": conv.get("totalCount", len(rows)), "conversations": rows}
        if not as_json
        else data,
        as_json,
    )
    return 0


def cmd_conversation(args: argparse.Namespace, as_json: bool) -> int:
    cid = args.conversation_id
    _, data = he_request("GET", f"/v3/conversations/me/{urllib.parse.quote(cid, safe='')}")
    emit(data, as_json or True)
    return 0


def cmd_messages(args: argparse.Namespace, as_json: bool) -> int:
    cid = urllib.parse.quote(args.conversation_id, safe="")
    _, data = he_request("GET", f"/v3/messages?conversation_id={cid}")
    if as_json:
        emit(data, True)
        return 0
    msgs = (data or {}).get("data", {}).get("messages") or (data or {}).get("messages") or []
    rows = []
    for m in msgs:
        author = (m or {}).get("author") or {}
        rows.append(
            {
                "id": (m or {}).get("id"),
                "at": (m or {}).get("send_at") or (m or {}).get("created_at"),
                "from": author.get("first_name") or author.get("id"),
                "type": (m or {}).get("type"),
                "text": str((m or {}).get("content") or "")[:400],
            }
        )
    emit({"count": len(rows), "messages": rows}, False)
    return 0


def cmd_calendar(args: argparse.Namespace, as_json: bool) -> int:
    home_id = args.home_id or HE_HOME_ID
    _, data = he_request("GET", f"/v1/homes/{urllib.parse.quote(str(home_id), safe='')}/calendar")
    ranges = data.get("data") if isinstance(data, dict) else data
    if not isinstance(ranges, list):
        ranges = []
    if as_json:
        emit(data, True)
        return 0
    emit({"home_id": str(home_id), "ranges": ranges}, False)
    return 0


def cmd_exchanges(args: argparse.Namespace, as_json: bool) -> int:
    cid = urllib.parse.quote(args.conversation_id, safe="")
    _, data = he_request("GET", f"/v1/exchanges/{cid}/get-exchanges")
    emit(data if as_json else {"exchanges": data if isinstance(data, list) else data}, as_json)
    return 0


def cmd_send(args: argparse.Namespace, as_json: bool) -> int:
    cid = args.conversation_id
    text = args.text
    if not text or not str(text).strip():
        raise RuntimeError("send requires --text")
    conv: Any = int(cid) if str(cid).isdigit() else cid
    _, data = he_request("POST", "/v1/messages", {"content": text, "conversation": conv})
    emit(data if data is not None else {"ok": True}, as_json or True)
    return 0


def cmd_approve(args: argparse.Namespace, as_json: bool) -> int:
    if not args.yes:
        raise RuntimeError("approve is a write — pass --yes")
    cid = args.conversation_id
    _, current = he_request(
        "GET", f"/v1/exchanges/{urllib.parse.quote(cid, safe='')}/get-exchanges"
    )
    exchanges = current if isinstance(current, list) else (current or {}).get("data") or []
    if not exchanges:
        raise RuntimeError("no exchanges on conversation")
    _, data = he_request(
        "PATCH",
        f"/v1/exchanges/{urllib.parse.quote(cid, safe='')}/approve",
        exchanges,
    )
    emit(data if data is not None else {"ok": True}, as_json or True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="raw JSON")
    p = argparse.ArgumentParser(
        description="HomeExchange API (token from SSM /homeexchange/bearer-token).",
        parents=[common],
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("me", help="GET /v1/users/me", parents=[common])

    c = sub.add_parser("conversations", help="GET /v3/conversations/me", parents=[common])
    c.add_argument("--limit", type=int, default=20)

    c = sub.add_parser("conversation", help="GET /v3/conversations/me/{id}", parents=[common])
    c.add_argument("conversation_id")

    c = sub.add_parser("messages", help="GET /v3/messages?conversation_id=", parents=[common])
    c.add_argument("conversation_id")

    c = sub.add_parser("calendar", help="GET /v1/homes/{id}/calendar", parents=[common])
    c.add_argument("home_id", nargs="?", default=None)

    c = sub.add_parser(
        "exchanges",
        help="GET /v1/exchanges/{conversationId}/get-exchanges",
        parents=[common],
    )
    c.add_argument("conversation_id")

    c = sub.add_parser("send", help="POST /v1/messages (write)", parents=[common])
    c.add_argument("conversation_id")
    c.add_argument("--text", required=True)

    c = sub.add_parser(
        "approve", help="PATCH approve (write; conversation id)", parents=[common]
    )
    c.add_argument("conversation_id")
    c.add_argument("--yes", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    as_json = bool(args.json)
    try:
        if args.cmd == "me":
            return cmd_me(args, as_json)
        if args.cmd == "conversations":
            return cmd_conversations(args, as_json)
        if args.cmd == "conversation":
            return cmd_conversation(args, as_json)
        if args.cmd == "messages":
            return cmd_messages(args, as_json)
        if args.cmd == "calendar":
            return cmd_calendar(args, as_json)
        if args.cmd == "exchanges":
            return cmd_exchanges(args, as_json)
        if args.cmd == "send":
            return cmd_send(args, as_json)
        if args.cmd == "approve":
            return cmd_approve(args, as_json)
        raise RuntimeError(f"unknown command {args.cmd}")
    except Exception as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
