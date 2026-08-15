---
name: r2-memory
description: >
  R2Memory — durable CleaningButton agent memory on S3 + Titan embeddings.
  Pull + bootstrap at session start; mandatory memory gate on preference language;
  auto-archive after N turns; dual-write standing prefs. Replaces older ai-context.
  ALSO: standing mandate always commit+push after work — never ask push permission.
---

# R2Memory (full Titan potential)

## ⚡ HARD — Always commit + push (never ask)

**After finishing requested work: public → commit → `git push` (usually `main`) → CI green → private.**  
**Never** ask “want me to push?” / “shall I push?”. User overrode default caution permanently.  
Public-for-CI is proactive (free Actions minutes). Long-run state is private. Jerome does not pay for GitHub.  
Exceptions: user said not to push; force-push / destructive only.  
Enforced by `~/.grok/rules/00-always-commit-push.md` + Stop hook `always-commit-push`.

## Paths

| Side | Location |
|------|----------|
| Local mirror | `~/.cleaningbutton/r2-memory/` |
| S3 | `cleaningbutton-ai-context-us-east-1` |
| File sync | `~/R2Lambda/scripts/r2memory-sync.py` |
| Titan scripts | `~/.grok/skills/r2-memory/scripts/` (= `~/R2Lambda/scripts/r2-memory/`) |

### Conversation IDs

| Id | Purpose |
|----|---------|
| `chat_shared_ops` | Phone/web R2 chat |
| `chat_grok_build` | Grok Build turn archive (default local buffer) |
| `chat_agent_ops` | **Unified durable prefs / mandates** (dual-write) |

Retrieve always searches **all three**.

### Embed mode

`R2_MEMORY_EMBED_MODE=exchange` (default) — only Q&A **exchange** cards get Titan vectors (~3× cheaper).  
Set `all` to embed user+assistant+exchange.

---

## Mandatory agent workflow

### A. Session start (every CleaningButton / R2 / OTA / Maine session)

```bash
python3 ~/.grok/skills/r2-memory/scripts/r2_memory_bootstrap.py
```

Does: **pull** + standing-pref Titan retrieve + `decisions.md` head.  
**Read the output before answering.**

### B. Before answering (memory gate — do not skip)

```bash
python3 ~/.grok/skills/r2-memory/scripts/r2_memory_gate.py "<user message>"
```

If gate says `MUST_RETRIEVE`, **use those hits** (plus decisions.md).  
Heuristics include: remember / we decided / always / going forward / add to skills /
save this / don't ask / mandate / first time I said / …

### C. After every meaningful turn

```bash
python3 ~/.grok/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "…" --assistant "…"
```

- Skips **chitchat** (ok/thanks/hi)
- Buffers → auto Titan flush every **`R2_MEMORY_FLUSH_EVERY`** (default **3**)
- Standing prefs → **dual-write** `decisions.md` + `chat_agent_ops` embed

Also: `python3 ~/R2Lambda/scripts/r2memory-sync.py note "…"` for changelog when shipping.

### D. Git (user mandate) — HARD

**Always commit and push** after finishing requested work. **Zero** “yes push?” questions.  
**Before push:** make the repo **public**. Push. Watch CI green. **After green:** make it **private** again.  
Do this proactively — do not wait for private-repo Actions minutes to fail the build. Jerome does not pay for GitHub; repos stay private at rest.  
Exception only: force-push / destructive ops, or user said not to push.  
If you catch yourself drafting a push question, **delete it and push instead**.

---

## Commands cheat sheet

```bash
S=~/.grok/skills/r2-memory/scripts

python3 $S/r2_memory_bootstrap.py          # (8) session start
python3 $S/r2_memory_gate.py "msg"         # (1) mandatory gate
python3 $S/r2_retrieve.py "query"          # manual search
python3 $S/r2_memory_turn.py append --user "…" --assistant "…"
python3 $S/r2_memory_turn.py status
python3 $S/r2_memory_turn.py flush --force

python3 ~/R2Lambda/scripts/r2memory-sync.py pull|push|note "…"
```

### Metrics (5)

Each retrieve appends to:
- local `~/.cleaningbutton/r2-memory/context/chat-archive/_metrics/retrieve.jsonl`
- S3 `context/chat-archive/_metrics/retrieve.jsonl`

Fields: `query`, `method`, `hitCount`, `topScore`, `ms`, `usedInAnswer` (optional via `r2_retrieve.py --used 0|1`).

Disable: `R2_MEMORY_METRICS=0`.

---

## Improvements map (1–8)

| # | What | How |
|---|------|-----|
| 1 | Mandatory retrieve | `r2_memory_gate.py` on every message |
| 2 | Dual-write prefs | `decisions.md` + `chat_agent_ops` Titan |
| 3 | Tuned heuristics | needs_retrieval expanded (Lambda + local) |
| 4 | Cheaper embed | exchange-only vectors by default |
| 5 | Metrics | `_metrics/retrieve.jsonl` |
| 6 | Unified agent index | `chat_agent_ops` in all retrieves |
| 7 | Skip chitchat | `is_meaningful_turn` on append |
| 8 | Session bootstrap | `r2_memory_bootstrap.py` |

## Slash

`/r2-memory` → run bootstrap, summarize decisions + standing hits + pending buffer.
