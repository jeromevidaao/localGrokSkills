---
name: r2
description: >
  Call R2 (R2Lambda) directly from this laptop: live Hospitable occupancy/revenue,
  R2Memory Q&A, AWS Cost Explorer billing (account spend), Kumo AC, cleaning spend,
  CleaningButton ops answers. Use when the user says "ask R2", "call R2", "/r2",
  wants unit guest status, past-month revenue, AWS bill/cost, or to query the
  same ops agent as the Android/web R2 chat without opening the app.
---

# Ask R2 (R2Lambda)

R2 is the CleaningButton ops agent (Lambda **`R2Lambda`**).

**Default chat** loads **R2Memory only** (fast). Live APIs (Hospitable, Kumo, CMP, AWS, **GitHub source pull**, …) load after an **LLM data-intent step** (structured JSON router in `lib/chat-intent.js`, regex safety net) — not only brittle keyword matches.

**GitHub code (read-only):** when the host asks about source, Pricing Lambda, occupancy **goals**/targets, or “what does the code say”, R2 pulls selected files from Jerome’s GitHub repos via the PAT (`lib/github-code.js`) into a `## GitHub source code` section. It must **not** claim it cannot read GitHub when that path is available.

**Occupancy goals / strategy / performance (standing):**

| Ask | R2 loads |
|-----|----------|
| **What are the goals / SEASON_BANDS?** | GitHub `jeromevidaao/pricing-tool` → `report.js` (`needGithubCode`) — deterministic bands |
| **Pricing strategy / reach 85% without leaving money on the table?** | GitHub → **`index.js` levers** (`needGithubCode`, strategy direct answer) — **not** SEASON_BANDS table alone |
| **How are we doing with the goals?** | Weekly S3 report `https://www.cleaningbutton.com/data/occupancy/latest.json` (`needOccupancyReport`) — actuals + targets already scored |
| **Live guest / fresher than weekly** | Hospitable (`needHospitable`) — only when host asks live/refresh/more detail |

Skill **`pricing`** owns the cascade. **Do not** answer “how are we doing with goals?” with only SEASON_BANDS and claim actuals are missing — load the S3 report (or call R2, which does).  
**Do not** answer a **pricing strategy** question with only the SEASON_BANDS month table — explain `index.js` levers (occ mult, YoY cap, last-minute, push rules).  
Sep/Oct definition = **shoulder** 60–85% (85% is **not** a year-round mandate).

**Long-term memory:** every turn is archived on S3 with Titan embeddings; digests/decisions are extracted; “remember / last time…” retrieves top hits — see skill **`r2-memory`**.

This skill **invokes the Lambda** with AWS creds (not the phone app).

## When to use

- User: “ask R2…”, “call R2…”, `/r2 …`
- Occupancy / guests: “is unit 2 free?”, “who is in apt 3?”
- Revenue: “past month revenue?”, “July net by unit?”
- **Hospitable API map** (endpoints, scopes, financials shape): skill **`hospitable`** / `/hospitable` — full Public API v2 index; use this skill for live answers
- Cleaning spend: “how much did we spend on cleaning last week?”
- AC/HVAC: “any AC running?” (KumoCloud via R2Lambda)
- **AWS account:** “what is our AWS bill?”, “cloud spend this month?” (Cost Explorer + STS via R2Lambda execution role — see also `aws-account` skill)
- **Rework status:** “rework status?”, “any open re-works?”, “status of rework_…” → DynamoDB `aiCodePushJobs` kind=`r2_rework` (comprehensive queue + detail)
- **Goal definitions:** “occupancy goals Sep/Oct?”, “what does SEASON_BANDS say?”, “read the Pricing Lambda” → GitHub pull (`needGithubCode` → `jeromevidaao/pricing-tool`). See skill **`pricing`**.
- **Pricing strategy:** “pricing strategy to reach 85%?”, “how do we price without leaving money on the table?”, fill vs ADR → GitHub **`index.js`** strategy answer (not SEASON_BANDS dump). See skill **`pricing`**.
- **Performance vs goals:** “how are we doing with the goals?”, “tracking vs targets?” → weekly S3 occupancy report (`needOccupancyReport`). Add Hospitable only if the host asks for live/fresher detail. See skill **`pricing`**.
- Ops architecture questions that benefit from R2Memory + live data + optional GitHub pull

## How to call (preferred)

Run the helper script via the shell tool:

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py "Is unit 2 occupied right now?"
```

Shared continuous thread (same as Android/web R2 chat):

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py "What was last month total net revenue?"
# default conversation id: chat_shared_ops
```

AWS bill (same CE data as Android More → AWS Billing):

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py "What is our AWS bill this month?"
```

Performance vs occupancy goals (S3 weekly report — no Hospitable by default):

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "How are we doing with the occupancy goals?"
```

Pricing strategy (GitHub index.js levers — not SEASON_BANDS dump):

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "what is your pricing strategy to reach 85% occupancy rate without leaving too much money on the table?"
```

Live refresh beyond the weekly snapshot:

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local --no-history \
  "How are we doing with goals — refresh live from Hospitable"
```

Private Grok-only thread (do not pollute the shared app chat):

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --local "Explain R2Lambda intents"
```

Full JSON / diagnostics:

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py --json "Summarize occupancy"
python3 ~/.grok/skills/r2/scripts/r2_chat.py --diag
```

Optional flags:

| Flag | Meaning |
|------|---------|
| `--local` | Thread `chat_grok_local` instead of `chat_shared_ops` |
| `-c ID` | Explicit conversation id |
| `--no-history` | Do not load prior Dynamo messages |
| `--repo owner/name` | Pin code-context repo |
| `--json` | Print full Lambda response |
| `--diag` | Health probe (worker + GitHub token) |

Env overrides: `R2_LAMBDA_FUNCTION`, `R2_JOBS_TABLE`, `AWS_REGION`, `AWS_PROFILE`, `R2_CLI_READ_TIMEOUT` (seconds, default 240).

## Agent workflow

1. **Decide thread:** default **shared** (`chat_shared_ops`) so answers align with the phone; use `--local` only when the user wants a private Grok thread.
2. **Run the script** with the user’s question as the message (quote properly).
3. **Relay R2’s reply** to the user (do not invent guest names or revenue if the script errors).
4. If invoke fails: check AWS creds, that function `R2Lambda` exists in `us-east-1`, and `--diag`.

## Rules

- **Do** use this for live guest/revenue facts instead of guessing.
- **Do not** put JWTs, full bearer tokens, or raw SSM secrets in chat notes.
- Chat turns can take **30–120s** (Hospitable + Grok); do not kill the command early.
- Code-push jobs are **not** this skill — those stay `act=ai_code_submit` / AI tab.

## Slash

`/r2 <message>` → run `r2_chat.py` with that message and report the reply.
