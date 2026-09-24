---
name: grok-cli-only
description: >-
  Use for any Grok CLI agent work: every real ask → Titan/r2 gate first, then
  grok headless on this computer only; append after. AUTO-bootstrap via
  box-bootstrap when aws/grok/skills PATH is missing (e.g. after Update Computer).
---
# Grok CLI only

## Standing rules (Jerome — hard)
1. **Every real question** → **`r2_memory_gate` / `r2_retrieve` FIRST** (Titan / R2Memory on this box), then answer from hits + only the skills the gate names, then **`r2_memory_turn append`** after. Skip only pure chitchat (`hi` / `ok` / `thanks`).
2. **Every question** also goes through the **`grok` CLI** (headless) when the ask needs tooling — after the memory gate.
3. **Always run `grok` and the AWS CLI on this agent’s own computer** (the shared Linux box). Never route AWS/`grok` through a registered Mac or other user machine unless Jerome explicitly asks.
4. Never open a browser, drive a desktop GUI, or use computerUse/browserUse for work a skill/API script can do.
5. AWS identity on this computer is **`grok-bot-titan`** (account `834917996497`). Titan access is required and expected. If Titan is AccessDenied, report that plainly — do **not** silently switch to Mac Shell unless Jerome asked.

## Auto box bootstrap when tooling is missing (HARD — Jerome)

**Do not ask.** If `aws`, `grok`, PATH (`~/.local/bin` / `~/.grok/bin`), or
`~/.grok/skills` is missing/broken (common after Update Computer), **immediately** run:

```bash
bash ~/.grok/skills/box-bootstrap/scripts/bootstrap_box_clis.sh
# fallback if skills link is already broken:
# bash /workspace/localGrokSkills/skills/box-bootstrap/scripts/bootstrap_box_clis.sh
```

Then continue the original task. Full detail: skill **`box-bootstrap`**. Never
direct Jerome to Reset Computer. Brief note in chat only if you actually ran it.

## Mandatory memory turn (HARD — do not skip)

```bash
S=~/.grok/skills/r2-memory/scripts
# 1) Gate / retrieve BEFORE answering
python3 $S/r2_memory_gate.py "<user message>"
# If MUST_RETRIEVE (or any real ask):
python3 $S/r2_retrieve.py "<user message>" -k 8
# 2) Answer (use hits; load only printed skills; prefer grok CLI for tooling)
# 3) Append AFTER answering
python3 $S/r2_memory_turn.py append --user "…" --assistant "…"
```

`~/.grok/skills` → `/workspace/localGrokSkills/skills` (includes `r2-memory`). Full recipe: follow the r2-memory skill.

```bash
# Prefer prompt-file XOR -p (not both)
grok --prompt-file /tmp/ask.txt --always-approve --output-format plain --max-turns 20 --verbatim
# or:
grok -p "…" --always-approve --output-format plain --max-turns 20 --verbatim
```

Do **not** answer from chat memory alone or jump to raw `aws`/`python` before the R2 gate. Prefer `grok` to drive skill scripts and AWS itself **on this computer**.

## How to work
1. **Gate/retrieve** the user ask via r2-memory scripts (above).
2. Put the user ask into `grok -p …` or `--prompt-file` (with `--verbatim`) when tools are needed.
3. Point grok at the matching skill under `~/.grok/skills/` / `/workspace/localGrokSkills/skills/`.
4. Secrets from AWS SSM only — never print tokens/passwords to chat or shell history.
5. Read-only first; mutate only when the user asked.
6. Deliver the result to Jerome; keep it short.
7. **Append** the turn to R2Memory.

## Headless flags
- `-p` / `--single` **or** `--prompt-file` (not both)
- `--always-approve` — auto-approve tool runs
- `--output-format plain|json`
- `--verbatim` — send prompt exactly
- `--max-turns N`

## Examples
```bash
S=~/.grok/skills/r2-memory/scripts
python3 $S/r2_memory_gate.py "check Bellevue Club canary"
python3 $S/r2_retrieve.py "check Bellevue Club canary" -k 5
grok -p --always-approve --verbatim "On THIS computer only: check Bellevue Club canary via AWS CLI — alarms, Lambda, last REPORT lines, SSM /bellevue-club/* exists (no secret values). Healthy yes/no/unknown."
python3 $S/r2_memory_turn.py append --user "check Bellevue Club canary" --assistant "…"
```

## Out of scope
Desktop busywork, Mac-routed AWS by default, and non-CLI chores — decline or ask Jerome first.

## Harness / Android push gate (HARD — 2026-09-22)
Before pushing `auto-reply-sqs-harness`: always run skill `guest-messaging-harness` (`python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py`). Never push on only `npm test` or a single `--only=` eval when prompts/agent/handler/policy changed.

Before pushing `R2PinelandAndroid`: ensure unit-test Kotlin compiles (no unescaped `"` inside double-quoted test strings). Prefer `./gradlew :app:testDebugUnitTest` when Java is available; otherwise at least open new/edited `*Test.kt` for illegal string literals. Watch `gh run` after push until green — do not stack further commits on a red Android CI.
