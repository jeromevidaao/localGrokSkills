#!/usr/bin/env python3
"""
Shared Titan + S3 helpers for local R2Memory (parity with R2Lambda chat-memory.js).

Features (full potential pack):
  1) needs_retrieval — expanded heuristics; gate CLI enforces retrieve
  2) dual-write standing prefs → decisions.md + chat_agent_ops index
  3) tuned mandate / "add to skills" language
  4) cheap embed: default exchange-card only (R2_MEMORY_EMBED_MODE=exchange|all)
  5) retrieve metrics → local + S3 jsonl
  6) unified agent index chat_agent_ops for durable prefs
  7) is_meaningful_turn — skip chitchat in archive buffer
  8) bootstrap_session — pull + standing-pref retrieve at session start

Env:
  R2_MEMORY_BUCKET, R2_EMBED_MODEL, AWS_REGION, R2_MEMORY_DIR
  R2_MEMORY_FLUSH_EVERY          default 1 (searchable the same turn)
  R2_MEMORY_CONVERSATION_ID      default chat_grok_build
  R2_MEMORY_EMBED_MODE           exchange (default) | all
  R2_MEMORY_METRICS              1 (default) | 0
"""

from __future__ import annotations

import base64
import json
import math
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BUCKET = "cleaningbutton-ai-context-us-east-1"
DEFAULT_MODEL = "amazon.titan-embed-text-v2:0"
DEFAULT_REGION = "us-east-1"
DEFAULT_CONV = "chat_grok_build"
SHARED_CONV = "chat_shared_ops"
AGENT_CONV = "chat_agent_ops"  # unified durable agent memory (prefs / mandates)
CATALOG_CONV = "chat_catalog"  # pinned skill + topic cards (short)
INDEX_MAX = 1500
EMBED_DIMS = 512
SESSION_BOOT_QUERY = (
    "standing preferences mandates decisions always commit push "
    "occupancy check-in skills do not ask remember we decided"
)

# ── env ──────────────────────────────────────────────────────────────


def env_bucket() -> str:
    return os.environ.get("R2_MEMORY_BUCKET") or os.environ.get("OPS_CONTEXT_BUCKET") or DEFAULT_BUCKET


def env_region() -> str:
    return os.environ.get("AWS_REGION") or DEFAULT_REGION


def env_model() -> str:
    return os.environ.get("R2_EMBED_MODEL") or DEFAULT_MODEL


def env_flush_every() -> int:
    try:
        n = int(os.environ.get("R2_MEMORY_FLUSH_EVERY", "1"))
    except ValueError:
        n = 3
    return max(1, min(n, 50))


def env_conversation_id() -> str:
    return os.environ.get("R2_MEMORY_CONVERSATION_ID") or DEFAULT_CONV


def env_embed_mode() -> str:
    m = (os.environ.get("R2_MEMORY_EMBED_MODE") or "exchange").strip().lower()
    return m if m in ("exchange", "all") else "exchange"


def env_metrics_enabled() -> bool:
    return (os.environ.get("R2_MEMORY_METRICS") or "1").strip() not in ("0", "false", "no")


def local_root() -> Path:
    raw = os.environ.get("R2_MEMORY_DIR") or os.environ.get("AI_CONTEXT_DIR")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".cleaningbutton" / "r2-memory"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def month_key(when: datetime | None = None) -> str:
    d = when or datetime.now(timezone.utc)
    return d.strftime("%Y-%m")


def safe_conv_id(conversation_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", conversation_id or DEFAULT_CONV)


def archive_prefix(conversation_id: str) -> str:
    return f"context/chat-archive/{safe_conv_id(conversation_id)}"


def archive_jsonl_key(conversation_id: str, when: datetime | None = None) -> str:
    return f"{archive_prefix(conversation_id)}/{month_key(when)}.jsonl"


def index_key(conversation_id: str) -> str:
    return f"{archive_prefix(conversation_id)}/index.json"


def digest_key(conversation_id: str) -> str:
    return f"{archive_prefix(conversation_id)}/digest.md"


def metrics_local_path() -> Path:
    p = local_root() / "context" / "chat-archive" / "_metrics"
    p.mkdir(parents=True, exist_ok=True)
    return p / "retrieve.jsonl"


def metrics_s3_key() -> str:
    return "context/chat-archive/_metrics/retrieve.jsonl"


def pending_path(conversation_id: str | None = None) -> Path:
    cid = safe_conv_id(conversation_id or env_conversation_id())
    p = local_root() / "context" / "chat-archive" / cid
    p.mkdir(parents=True, exist_ok=True)
    return p / "pending_exchanges.json"


def decisions_path() -> Path:
    return local_root() / "context" / "working" / "decisions.md"


def default_retrieve_conversations() -> list[str]:
    """Phone shared + Grok Build + durable prefs + skill/topic catalog."""
    return [SHARED_CONV, DEFAULT_CONV, AGENT_CONV, CATALOG_CONV]


# ── AWS helpers ──────────────────────────────────────────────────────


def _aws(args: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    cmd = ["aws", *args, "--region", env_region(), "--output", "json"]
    return subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)


def s3_get_text(key: str, bucket: str | None = None) -> str | None:
    b = bucket or env_bucket()
    r = subprocess.run(
        ["aws", "s3", "cp", f"s3://{b}/{key}", "-", "--region", env_region()],
        check=False,
        capture_output=True,
        timeout=180,
    )
    if r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        if any(x in err for x in ("404", "Not Found", "NoSuchKey", "does not exist")):
            return None
        print(f"s3_get_text warn {key}: {err.strip()[:200]}", file=sys.stderr)
        return None
    return (r.stdout or b"").decode("utf-8", errors="replace")


def s3_get_json(key: str, bucket: str | None = None) -> dict[str, Any] | None:
    t = s3_get_text(key, bucket=bucket)
    if not t or not t.strip():
        return None
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return None


def s3_put_text(
    key: str,
    body: str,
    *,
    content_type: str = "text/plain; charset=utf-8",
    bucket: str | None = None,
) -> None:
    b = bucket or env_bucket()
    r = subprocess.run(
        [
            "aws",
            "s3",
            "cp",
            "-",
            f"s3://{b}/{key}",
            "--content-type",
            content_type,
            "--region",
            env_region(),
        ],
        input=body.encode("utf-8"),
        check=False,
        capture_output=True,
        timeout=180,
    )
    if r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        raise RuntimeError(f"s3 put failed {key}: {err.strip() or r.returncode}")


def s3_put_json(key: str, doc: dict[str, Any], bucket: str | None = None) -> None:
    s3_put_text(
        key,
        json.dumps(doc, ensure_ascii=False),
        content_type="application/json; charset=utf-8",
        bucket=bucket,
    )


def s3_append_jsonl_line(key: str, record: dict[str, Any], bucket: str | None = None) -> None:
    prev = s3_get_text(key, bucket=bucket) or ""
    if prev and not prev.endswith("\n"):
        prev += "\n"
    s3_put_text(
        key,
        prev + json.dumps(record, ensure_ascii=False) + "\n",
        content_type="application/x-ndjson; charset=utf-8",
        bucket=bucket,
    )


# ── text / scoring ───────────────────────────────────────────────────


def tokenize(text: str) -> list[str]:
    s = re.sub(r"[^a-z0-9\s#._/\-]", " ", (text or "").lower())
    return [t for t in s.split() if len(t) >= 3][:80]


def keyword_score(query_tokens: list[str], entry: dict[str, Any]) -> float:
    if not query_tokens:
        return 0.0
    hay = set(tokenize(entry.get("text") or entry.get("summary") or ""))
    for k in entry.get("keywords") or []:
        hay.add(str(k).lower())
    hits = sum(1 for t in query_tokens if t in hay)
    recency = 0.0
    at = entry.get("at")
    if at:
        try:
            ts = datetime.fromisoformat(str(at).replace("Z", "+00:00")).timestamp()
            age_days = max(0.0, (time.time() - ts) / 86400.0)
            recency = max(0.0, 1.0 - age_days / 90.0) * 0.5
        except Exception:
            recency = 0.0
    return float(hits) + recency


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        xf = float(x or 0.0)
        yf = float(y or 0.0)
        dot += xf * yf
        na += xf * xf
        nb += yf * yf
    if not na or not nb:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def embed_text(text: str, *, dimensions: int = EMBED_DIMS) -> list[float] | None:
    """Invoke Titan Embed via Bedrock.

    AWS CLI v1 on this box rejects base64 --body (ValidationException /
    Malformed input). Use fileb:// for the JSON body instead.
    """
    input_text = (text or "").strip()[:8000]
    if not input_text:
        return None
    body = {
        "inputText": input_text,
        "dimensions": 1024 if dimensions == 1024 else 512,
        "normalize": True,
    }
    tag = uuid.uuid4().hex[:10]
    body_path = Path(f"/tmp/r2-titan-embed-body-{tag}.json")
    out_path = Path(f"/tmp/r2-titan-embed-{tag}.json")
    try:
        body_path.write_text(json.dumps(body), encoding="utf-8")
        r = _aws(
            [
                "bedrock-runtime",
                "invoke-model",
                "--model-id",
                env_model(),
                "--content-type",
                "application/json",
                "--accept",
                "application/json",
                "--body",
                f"fileb://{body_path}",
                str(out_path),
            ],
            timeout=60,
        )
        if r.returncode != 0 or not out_path.exists():
            err = r.stderr or ""
            print(f"embed_text failed: {err.strip()}", file=sys.stderr)
            return None
        parsed = json.loads(out_path.read_text(encoding="utf-8"))
        emb = parsed.get("embedding") or parsed.get("embeddings")
        if isinstance(emb, list) and emb and isinstance(emb[0], list):
            emb = emb[0]
        if isinstance(emb, list):
            return [float(x) for x in emb]
        return None
    except Exception as e:
        print(f"embed_text failed: {e}", file=sys.stderr)
        return None
    finally:
        for p in (body_path, out_path):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass


# ── (1)(3) retrieval heuristics ──────────────────────────────────────


def needs_retrieval(message: str) -> bool:
    """True when the agent MUST run Titan retrieve before answering."""
    from topic_catalog import needs_retrieval as _topic_needs  # local sibling

    return _topic_needs(message)


def is_meaningful_turn(user_message: str, assistant_reply: str = "") -> bool:
    """Skip pure chitchat so it does not dilute the Titan index (7)."""
    u = str(user_message or "").strip()
    a = str(assistant_reply or "").strip()
    if u.lower() in ("", "ok", "okay", "k", "thanks", "thank you", "thx", "cool", "nice", "yep", "yeah", "yes", "no", "ping", "pong", "hi", "hello", "hey", "yo", "sup"):
        if len(a) < 80:
            return False
    if len(u) < 12 and len(a) < 40:
        return False
    if re.match(
        r"^(hi|hello|hey|yo|sup|ok|okay|thanks|thank you|pong|ping|yes|no|k|cool|nice|lgtm|sg)\b",
        u,
        re.I,
    ) and len(u) < 24:
        return False
    return True


def looks_like_standing_preference(user_message: str) -> bool:
    """Mandate / always / add-to-skills language → dual-write to decisions (2)."""
    s = (user_message or "").lower()
    if not s.strip():
        return False
    return bool(
        re.search(
            r"\b(always|going forward|from now on|permanently|standing|mandate|don't ask|do not ask|"
            r"add to (?:your )?skills?|save (?:this|that) in (?:your )?memory|we (?:always|decided)|"
            r"do not wait|without asking|never ask again)\b",
            s,
            re.I,
        )
    )


def extract_decision_line(user_message: str, assistant_reply: str = "") -> str:
    """One-line durable decision for decisions.md + agent index."""
    u = re.sub(r"\s+", " ", (user_message or "").strip())[:220]
    a = re.sub(r"\s+", " ", (assistant_reply or "").strip())[:160]
    if a and looks_like_standing_preference(user_message):
        return f"User mandate: {u} → Agent: {a}"
    return f"User mandate: {u}"


# ── (5) metrics ──────────────────────────────────────────────────────


def log_retrieve_metric(row: dict[str, Any]) -> None:
    if not env_metrics_enabled():
        return
    row = dict(row)
    row.setdefault("at", now_iso())
    row.setdefault("source", "grok_build")
    line = json.dumps(row, ensure_ascii=False)
    try:
        path = metrics_local_path()
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"metrics local failed: {e}", file=sys.stderr)
    try:
        s3_append_jsonl_line(metrics_s3_key(), row)
    except Exception as e:
        print(f"metrics s3 failed: {e}", file=sys.stderr)


# ── (2) dual-write decisions + agent index ───────────────────────────


def dual_write_decision(user_message: str, assistant_reply: str = "") -> dict[str, Any]:
    """Write standing preference to decisions.md (local) and chat_agent_ops Titan index."""
    if not looks_like_standing_preference(user_message):
        return {"wrote": False, "reason": "not_standing"}
    day = now_iso()[:10]
    line = extract_decision_line(user_message, assistant_reply)
    result: dict[str, Any] = {"wrote": True, "line": line, "day": day}

    # local decisions.md
    try:
        path = decisions_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        prev = path.read_text(encoding="utf-8") if path.exists() else "# Durable decisions\n"
        block = f"\n## {day}\n- {line}\n"
        if line not in prev:
            path.write_text(prev + block, encoding="utf-8")
            result["decisionsMd"] = True
        else:
            result["decisionsMd"] = "duplicate"
    except Exception as e:
        result["decisionsMd"] = str(e)

    # unified agent index (embed exchange-style card)
    try:
        tid = f"pref_{int(time.time() * 1000)}"
        records = [
            _make_record(
                conversation_id=AGENT_CONV,
                role="exchange",
                content=f"STANDING PREFERENCE\nUser: {user_message[:1500]}\nAgent: {str(assistant_reply)[:1500]}\nDecision: {line}",
                turn_id=tid,
                source="grok_build_decision",
            )
        ]
        archive_turns_batch(records, conversation_id=AGENT_CONV, embed_roles={"exchange"})
        result["agentIndex"] = True
        result["agentTurnId"] = tid
    except Exception as e:
        result["agentIndex"] = str(e)

    return result


# ── archive / embed ──────────────────────────────────────────────────


def _make_record(
    *,
    conversation_id: str,
    role: str,
    content: str,
    turn_id: str,
    source: str,
) -> dict[str, Any]:
    cid = safe_conv_id(conversation_id)
    return {
        "id": f"{(role or 'x')[0]}_{turn_id}_{uuid.uuid4().hex[:6]}",
        "at": now_iso(),
        "conversationId": cid,
        "turnId": turn_id,
        "role": role or "user",
        "content": str(content or "")[:12000],
        "imageKeys": [],
        "chatDataKind": None,
        "source": source,
    }


def _record_to_index_entry(record: dict[str, Any], embedding: list[float] | None) -> dict[str, Any]:
    return {
        "id": record["id"],
        "at": record["at"],
        "role": record["role"],
        "text": record["content"][:1200],
        "summary": record["content"][:200],
        "keywords": tokenize(record["content"])[:24],
        "embedding": embedding or None,
        "turnId": record["turnId"],
    }


def archive_turns_batch(
    records: list[dict[str, Any]],
    *,
    conversation_id: str,
    embed_roles: set[str] | None = None,
) -> None:
    """
    Append many turns with one jsonl + one index rewrite.
    embed_roles: which roles get Titan vectors. Default from R2_MEMORY_EMBED_MODE:
      exchange → only role==exchange (cheap)
      all → every card
    """
    if not records:
        return
    cid = safe_conv_id(conversation_id)
    if embed_roles is None:
        embed_roles = {"user", "assistant", "exchange"} if env_embed_mode() == "all" else {"exchange"}

    try:
        key = archive_jsonl_key(cid)
        prev = s3_get_text(key) or ""
        if prev and not prev.endswith("\n"):
            prev += "\n"
        lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
        s3_put_text(key, prev + lines, content_type="application/x-ndjson; charset=utf-8")
    except Exception as e:
        print(f"archive jsonl batch failed: {e}", file=sys.stderr)

    try:
        ikey = index_key(cid)
        doc = s3_get_json(ikey) or {"version": 1, "conversationId": cid, "entries": []}
        entries = list(doc.get("entries") or [])
        new_entries: list[dict[str, Any]] = []
        for record in records:
            role = record.get("role") or ""
            do_embed = role in embed_roles
            # Exchange-only mode: keep user/assistant in jsonl, do not spend
            # index slots on unembedded cards (3× more searchable history).
            if not do_embed and env_embed_mode() == "exchange":
                continue
            emb = None
            if do_embed:
                text = f"{role}: {record['content']}"[:2000]
                emb = embed_text(text, dimensions=EMBED_DIMS)
            new_entries.append(_record_to_index_entry(record, emb))
        for ent in new_entries:
            entries.insert(0, ent)
        doc["entries"] = entries[:INDEX_MAX]
        doc["updatedAt"] = now_iso()
        doc["conversationId"] = cid
        s3_put_json(ikey, doc)
    except Exception as e:
        print(f"archive index batch failed: {e}", file=sys.stderr)


def archive_turn(
    *,
    conversation_id: str,
    role: str,
    content: str,
    turn_id: str | None = None,
    source: str = "grok_build",
    embed: bool = True,
) -> dict[str, Any]:
    tid = turn_id or f"t_{int(time.time() * 1000)}"
    record = _make_record(
        conversation_id=conversation_id,
        role=role,
        content=content,
        turn_id=tid,
        source=source,
    )
    roles = {role} if embed else set()
    if embed and env_embed_mode() == "exchange" and role != "exchange":
        roles = set()  # only exchange embeds by default
    if embed and env_embed_mode() == "all":
        roles = {role}
    archive_turns_batch([record], conversation_id=conversation_id, embed_roles=roles)
    return record


def archive_exchange(
    *,
    conversation_id: str,
    user_message: str,
    assistant_reply: str,
    turn_id: str | None = None,
    source: str = "grok_build",
) -> str:
    tid = turn_id or f"g_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
    records = [
        _make_record(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            turn_id=tid,
            source=source,
        ),
        _make_record(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_reply,
            turn_id=tid,
            source=source,
        ),
        _make_record(
            conversation_id=conversation_id,
            role="exchange",
            content=f"User: {str(user_message or '')[:1500]}\nR2: {str(assistant_reply or '')[:1500]}",
            turn_id=tid,
            source=source,
        ),
    ]
    archive_turns_batch(records, conversation_id=conversation_id)
    return tid


def archive_exchanges_batch(
    exchanges: list[dict[str, Any]],
    *,
    conversation_id: str,
    source: str = "grok_build",
) -> list[str]:
    cid = safe_conv_id(conversation_id)
    all_records: list[dict[str, Any]] = []
    turn_ids: list[str] = []
    for ex in exchanges:
        tid = f"g_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
        turn_ids.append(tid)
        user_message = ex.get("user") or ""
        assistant_reply = ex.get("assistant") or ""
        all_records.extend(
            [
                _make_record(
                    conversation_id=cid,
                    role="user",
                    content=user_message,
                    turn_id=tid,
                    source=source,
                ),
                _make_record(
                    conversation_id=cid,
                    role="assistant",
                    content=assistant_reply,
                    turn_id=tid,
                    source=source,
                ),
                _make_record(
                    conversation_id=cid,
                    role="exchange",
                    content=f"User: {str(user_message)[:1500]}\nR2: {str(assistant_reply)[:1500]}",
                    turn_id=tid,
                    source=source,
                ),
            ]
        )
    archive_turns_batch(all_records, conversation_id=cid)
    return turn_ids


# ── retrieve ─────────────────────────────────────────────────────────


def retrieve_relevant(
    query: str,
    *,
    conversation_ids: list[str] | None = None,
    top_k: int = 6,
    log_metrics: bool = True,
    used_in_answer: bool | None = None,
) -> dict[str, Any]:
    convs = conversation_ids or default_retrieve_conversations()
    seen: set[str] = set()
    ordered: list[str] = []
    for c in convs:
        sc = safe_conv_id(c)
        if sc not in seen:
            seen.add(sc)
            ordered.append(sc)

    t0 = time.time()
    entries: list[dict[str, Any]] = []
    for cid in ordered:
        doc = s3_get_json(index_key(cid)) or {}
        for e in doc.get("entries") or []:
            if isinstance(e, dict):
                e = dict(e)
                e["_conversationId"] = cid
                entries.append(e)

    if not entries:
        out = {"text": "", "hits": [], "method": "empty", "query": query, "ms": int((time.time() - t0) * 1000)}
        if log_metrics:
            log_retrieve_metric({**{k: out[k] for k in ("query", "method", "ms")}, "hitCount": 0, "topScore": 0})
        return out

    q_tokens = tokenize(query)
    q_emb = embed_text(str(query)[:2000], dimensions=EMBED_DIMS)

    scored: list[dict[str, Any]] = []
    for e in entries:
        kw = keyword_score(q_tokens, e)
        emb = 0.0
        if q_emb and isinstance(e.get("embedding"), list):
            emb = cosine_similarity(q_emb, e["embedding"]) * 8.0
        cid = e.get("_conversationId")
        boost = 0.0
        if cid == AGENT_CONV:
            boost = 0.4
        elif cid == CATALOG_CONV:
            boost = 0.55
        scored.append({"entry": e, "score": kw + emb + boost, "kw": kw, "emb": emb})

    scored.sort(key=lambda s: s["score"], reverse=True)
    hits = [s for s in scored if s["score"] > 0.35][:top_k]
    method = "keyword+embed" if q_emb else "keyword"
    ms = int((time.time() - t0) * 1000)

    if not hits:
        recent = [e for e in entries if e.get("role") in ("exchange", "user")][:3]
        if not recent:
            out = {"text": "", "hits": [], "method": "none", "query": query, "ms": ms}
            if log_metrics:
                log_retrieve_metric({"query": query, "method": "none", "hitCount": 0, "topScore": 0, "ms": ms, "usedInAnswer": used_in_answer})
            return out
        text = "## Retrieved past R2 chat (recent fallback)\n" + "\n".join(
            f"- ({str(e.get('at') or '')[:10]} · {e.get('_conversationId')}) {str(e.get('text') or e.get('summary') or '')[:400]}"
            for e in recent
        )
        out = {"text": text, "hits": recent, "method": "recent", "query": query, "ms": ms}
        if log_metrics:
            log_retrieve_metric({"query": query, "method": "recent", "hitCount": len(recent), "topScore": 0, "ms": ms, "usedInAnswer": used_in_answer})
        return out

    text = (
        "## Retrieved past R2 chat (relevant memory)\n"
        "Use these only if they help; prefer live data and current user message when they conflict.\n"
        + "\n".join(
            f"- [{str(h['entry'].get('at') or '')[:16]} · {h['entry'].get('_conversationId')} · "
            f"{h['entry'].get('role') or 'turn'} · score={h['score']:.2f}] "
            f"{str(h['entry'].get('text') or h['entry'].get('summary') or '')[:500]}"
            for h in hits
        )
    )
    out = {
        "text": text,
        "hits": [h["entry"] for h in hits],
        "method": method,
        "query": query,
        "ms": ms,
        "scores": [
            {"id": h["entry"].get("id"), "score": round(h["score"], 3), "kw": round(h["kw"], 3), "emb": round(h["emb"], 3)}
            for h in hits
        ],
    }
    if log_metrics:
        log_retrieve_metric(
            {
                "query": query[:500],
                "method": method,
                "hitCount": len(hits),
                "topScore": round(hits[0]["score"], 3) if hits else 0,
                "ms": ms,
                "conversations": ordered,
                "usedInAnswer": used_in_answer,
            }
        )
    return out


# ── pending buffer + auto flush ──────────────────────────────────────


def load_pending(conversation_id: str | None = None) -> list[dict[str, Any]]:
    path = pending_path(conversation_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data.get("exchanges") or [])
    except Exception:
        return []


def save_pending(exchanges: list[dict[str, Any]], conversation_id: str | None = None) -> None:
    path = pending_path(conversation_id)
    path.write_text(
        json.dumps(
            {
                "conversationId": safe_conv_id(conversation_id or env_conversation_id()),
                "updatedAt": now_iso(),
                "exchanges": exchanges,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def append_pending_exchange(
    user_message: str,
    assistant_reply: str,
    *,
    conversation_id: str | None = None,
    meta: dict[str, Any] | None = None,
    skip_chitchat: bool = True,
) -> dict[str, Any]:
    cid = conversation_id or env_conversation_id()
    if skip_chitchat and not is_meaningful_turn(user_message, assistant_reply):
        return {
            "pending": len(load_pending(cid)),
            "flushEvery": env_flush_every(),
            "conversationId": safe_conv_id(cid),
            "skipped": True,
            "reason": "chitchat",
        }
    exchanges = load_pending(cid)
    item = {
        "at": now_iso(),
        "user": str(user_message or "")[:8000],
        "assistant": str(assistant_reply or "")[:8000],
        "meta": meta or {},
    }
    exchanges.append(item)
    save_pending(exchanges, cid)
    return {
        "pending": len(exchanges),
        "flushEvery": env_flush_every(),
        "conversationId": safe_conv_id(cid),
        "skipped": False,
    }


def flush_pending(
    *,
    conversation_id: str | None = None,
    force: bool = False,
    min_count: int | None = None,
) -> dict[str, Any]:
    cid = conversation_id or env_conversation_id()
    threshold = min_count if min_count is not None else env_flush_every()
    exchanges = load_pending(cid)
    if not exchanges:
        return {"flushed": 0, "pending": 0, "reason": "empty", "conversationId": safe_conv_id(cid)}
    if not force and len(exchanges) < threshold:
        return {
            "flushed": 0,
            "pending": len(exchanges),
            "reason": "below_threshold",
            "threshold": threshold,
            "conversationId": safe_conv_id(cid),
        }

    flushed_ids: list[str] = []
    errors: list[str] = []
    try:
        flushed_ids = archive_exchanges_batch(exchanges, conversation_id=cid, source="grok_build")
        save_pending([], cid)
    except Exception as e:
        errors.append(str(e))

    return {
        "flushed": len(flushed_ids),
        "pending": 0 if not errors else len(exchanges),
        "turnIds": flushed_ids,
        "errors": errors,
        "conversationId": safe_conv_id(cid),
        "method": "titan+s3",
        "embedMode": env_embed_mode(),
    }


def record_turn_auto(
    user_message: str,
    assistant_reply: str,
    *,
    conversation_id: str | None = None,
    force_flush: bool = False,
    dual_write: bool = True,
) -> dict[str, Any]:
    """
    Full post-turn path:
      - skip chitchat
      - buffer + auto Titan flush
      - dual-write standing prefs → decisions.md + chat_agent_ops
    """
    cid = conversation_id or env_conversation_id()
    st = append_pending_exchange(user_message, assistant_reply, conversation_id=cid)
    flush: dict[str, Any] = {"flushed": 0, "reason": "skipped"}
    if not st.get("skipped"):
        flush = flush_pending(conversation_id=cid, force=force_flush)
    decision: dict[str, Any] = {"wrote": False}
    if dual_write and looks_like_standing_preference(user_message):
        decision = dual_write_decision(user_message, assistant_reply)
    return {"append": st, "flush": flush, "decision": decision}


# ── (1) mandatory gate + (8) bootstrap ───────────────────────────────


def replace_catalog_index(cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Rebuild chat_catalog index from short skill/topic cards (pinned, no eviction mix)."""
    cid = CATALOG_CONV
    errors: list[str] = []
    entries: list[dict[str, Any]] = []
    for card in cards:
        text = str(card.get("text") or "").strip()
        if not text:
            continue
        tid = str(card.get("id") or f"card_{len(entries)}")
        record = _make_record(
            conversation_id=cid,
            role="exchange",
            content=text[:4000],
            turn_id=tid,
            source="skill_topic_catalog",
        )
        emb = embed_text(f"exchange: {text}"[:2000], dimensions=EMBED_DIMS)
        entry = _record_to_index_entry(record, emb)
        entry["pinned"] = True
        entries.append(entry)
    try:
        s3_put_json(
            index_key(cid),
            {
                "version": 1,
                "conversationId": cid,
                "kind": "skill_topic_catalog",
                "updatedAt": now_iso(),
                "entries": entries,
            },
        )
    except Exception as e:
        errors.append(str(e))
    return {
        "wrote": not errors,
        "reason": "ok" if not errors else "s3_error",
        "cards": len(entries),
        "errors": errors,
        "conversationId": cid,
    }


def memory_gate(user_message: str, *, force: bool = False, top_k: int = 6) -> dict[str, Any]:
    """
    Mandatory pre-answer gate.
    If needs_retrieval (or force), run Titan retrieve and return hits text.
    Agent MUST incorporate when must_retrieve=True.
    """
    from topic_catalog import match_topics, skills_for_message

    topics = match_topics(user_message)
    skills = skills_for_message(user_message)
    must = force or needs_retrieval(user_message)
    if not must:
        return {
            "must_retrieve": False,
            "needs_retrieval": False,
            "text": "",
            "method": "skipped",
            "hits": [],
            "topics": [t["id"] for t in topics],
            "skills": skills,
        }
    result = retrieve_relevant(user_message, top_k=top_k, log_metrics=True)
    return {
        "must_retrieve": True,
        "needs_retrieval": True,
        "text": result.get("text") or "",
        "method": result.get("method"),
        "hits": result.get("hits") or [],
        "scores": result.get("scores"),
        "ms": result.get("ms"),
        "query": user_message,
        "topics": [t["id"] for t in topics],
        "skills": skills,
    }


def load_decisions_head(max_chars: int = 6000) -> str:
    path = decisions_path()
    if not path.exists():
        # try pull isn't done here; empty
        return ""
    try:
        t = path.read_text(encoding="utf-8")
        if len(t) > max_chars:
            return t[:2000] + "\n…\n" + t[-(max_chars - 2100) :]
        return t
    except Exception:
        return ""


def bootstrap_session(*, run_pull: bool = True, standing_query: str | None = None) -> dict[str, Any]:
    """
    Session start (8): optional pull + standing-pref Titan retrieve + decisions head.
    """
    pull_out = ""
    if run_pull:
        sync = Path.home() / "R2Lambda" / "scripts" / "r2memory-sync.py"
        if sync.exists():
            r = subprocess.run(
                [sys.executable, str(sync), "pull"],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            pull_out = ((r.stdout or "") + (r.stderr or "")).strip()[-500:]

    q = standing_query or SESSION_BOOT_QUERY
    mem = retrieve_relevant(q, top_k=8, log_metrics=True)
    decisions = load_decisions_head()
    pending = load_pending()
    catalog: dict[str, Any] = {"wrote": False, "reason": "skipped"}
    try:
        from r2_index_catalog import refresh_catalog

        catalog = refresh_catalog(force=False)
    except Exception as e:
        catalog = {"wrote": False, "reason": str(e)}
    return {
        "pull": pull_out,
        "standingQuery": q,
        "retrieveMethod": mem.get("method"),
        "retrieveText": mem.get("text") or "",
        "retrieveHits": len(mem.get("hits") or []),
        "decisionsHead": decisions,
        "pendingTurns": len(pending),
        "flushEvery": env_flush_every(),
        "embedMode": env_embed_mode(),
        "conversations": default_retrieve_conversations(),
        "catalog": catalog,
    }
