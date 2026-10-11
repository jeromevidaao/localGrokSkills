---
name: r2-memory
description: >
  R2Memory — Titan embeddings on S3 for CleaningButton decisions, prefs, and past Q&A.
  Query BEFORE answering occupancy, HomeExchange, parking/harness, AC, pricing,
  billing, skills, or any we-decided/always question. Do not load every skill body —
  retrieve first, then load only the matching skill. Use when: memory, embeddings,
  remember, standing prefs, skill catalog, or /r2-memory.
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

### Grok Bot IAM (`GrokBotTitanAccess` v7)

IAM user **`grok-bot-titan`**. Fetch keys from SSM at use — never commit, never paste the secret into chat or R2Memory.

| | |
|---|---|
| Access key ID | SSM `/grok/titan-iam-access-key-id` |
| Secret | SSM `/grok/titan-iam-secret-access-key` |
| Lambda | `lambda:*` (invoke, update code/config, create/delete, event-source mappings) + `iam:PassRole`/`GetRole` onto `lambda.amazonaws.com` |
| DynamoDB | `dynamodb:*` |
| SQS | `sqs:*` |
| S3 | `s3:*` (all buckets, not only `context/`) |
| CloudWatch | `cloudwatch:*` + `logs:*` (alarms, metrics, log groups) |
| CloudFront | `cloudfront:*` (including CreateInvalidation / UpdateDistribution) |
| EventBridge | `events:*` (PutRule / PutTargets / DescribeRule — e.g. `maine-property-tax-ach-watch`) |
| Bedrock | `InvokeModel` on Titan embed (`amazon.titan-embed-text-v2:0` and v1) |
| SSM | `ssm:*` (all parameters, including Put/Delete/Get) + `kms:Encrypt`/`Decrypt`/`GenerateDataKey` via `ssm.us-east-1` (`alias/aws/ssm`) |
| SNS | Inline `grok-bot-sns-alarm-routing` (not v7): list/subscribe/confirm/create-topic on this account. No publish or delete. See rule `02-ssm-api-credentials.md`. |
| Denied | IAM user/key admin, Cost Explorer, Hospitable API |

```bash
aws ssm get-parameter --name /grok/titan-iam-access-key-id --with-decryption --query Parameter.Value --output text
aws ssm get-parameter --name /grok/titan-iam-secret-access-key --with-decryption --query Parameter.Value --output text
```

On the Grok Bot computer: `aws configure` with those values, region `us-east-1`. Then run `r2_retrieve.py` / `r2_memory_turn.py` from the cloned `localGrokSkills` tree.

### Conversation IDs

| Id | Purpose |
|----|---------|
| `chat_shared_ops` | Phone/web R2 chat |
| `chat_grok_build` | Grok Build turn archive (default local buffer) |
| `chat_agent_ops` | **Unified durable prefs / mandates** (dual-write) |
| `chat_catalog` | Pinned **skill + topic cards** (short; never full SKILL.md) |

Retrieve always searches **all four**.

Do **not** load every skill body. TUI already lists name + description. Gate prints `topics=` and `skills=` — read only those `SKILL.md` files. Resolve paths with `python3 ~/localGrokSkills/scripts/resolve_skill.py <name>` (bundled skills are under `~/.grok/bundled/skills/`, not `~/.grok/skills/`).

### When to retrieve (do not skip)

Gate on **every** real user question. Skip only chitchat (`hi` / `ok` / `thanks`).

```bash
python3 ~/.grok/skills/r2-memory/scripts/r2_memory_gate.py --topics
```

That table is the source of truth (`topic_catalog.py`). Topics include occupancy, HomeExchange, parking/harness, AC, pricing, billing, live R2, ship/CI, and standing prefs.

After adding or editing a user skill, refresh the Titan catalog:

```bash
python3 ~/.grok/skills/r2-memory/scripts/r2_index_catalog.py
```

### Embed mode

`R2_MEMORY_EMBED_MODE=exchange` (default) — only Q&A **exchange** cards get Titan vectors and index slots (~3× more history).  
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

If gate says `MUST_RETRIEVE`, **use those hits** (plus decisions.md) and load only the printed `skills=`.  
Topics: occupancy / HE / parking-harness / AC / pricing / billing / live R2 / ship / standing prefs. See `--topics`.

### C. After every meaningful turn

```bash
python3 ~/.grok/skills/r2-memory/scripts/r2_memory_turn.py append \
  --user "…" --assistant "…"
```

- Skips **chitchat** (ok/thanks/hi)
- Buffers → auto Titan flush every **`R2_MEMORY_FLUSH_EVERY`** (default **1** — searchable this turn)
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

python3 $S/r2_memory_bootstrap.py          # (8) session start + catalog refresh if stale
python3 $S/r2_memory_gate.py "msg"         # (1) mandatory gate (prints topics + skills)
python3 $S/r2_memory_gate.py --topics      # when-to-retrieve table
python3 $S/r2_retrieve.py "query"          # manual search
python3 $S/r2_index_catalog.py             # re-embed skill/topic cards
python3 $S/r2_memory_turn.py append --user "…" --assistant "…"
python3 $S/r2_memory_turn.py status
python3 $S/r2_memory_turn.py flush --force
python3 ~/localGrokSkills/scripts/resolve_skill.py <name>

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
| 9 | Topic map | `topic_catalog.py` — when to retrieve + which skill |
| 10 | Skill catalog index | `chat_catalog` + `r2_index_catalog.py` |
| 11 | Index density | exchange-only index slots; flush every turn |

## Slash

`/r2-memory` → run bootstrap, summarize decisions + standing hits + pending buffer.
