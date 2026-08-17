---
name: guest-messaging-harness
description: >
  Pre-push checklist for jeromevidaao/auto-reply-sqs-harness (guest auto-reply /
  SQS harness / goldens / eval). Run before any commit or push that touches
  prompts, eval scenarios, goldens, required phrases, agent.js, or tools.
  Stops CI eval from being the first time new required phrases or category
  rubrics are tested. Use when working on auto-reply, guest messaging, harness
  evals, goldens, parking policy, or /guest-messaging-harness.
---

# Guest-messaging harness — pre-push

Repo: `~/auto-reply-sqs-harness` (`jeromevidaao/auto-reply-sqs-harness`).  
Push to `main` auto-deploys Lambda `guest-messaging-agent-harness`.  
CI `eval` job is live Grok + every golden (`npm run eval -- --fail-fast`).

**Do not discover required-phrase or category failures on CI.** Local prepush must be green first.

## When this skill applies

Any edit under that repo to `src/`, `prompts/`, `eval/`, `tests/`, `lambda/`, or guest-reply copy.  
Also when the user says auto-reply, goldens, eval, harness, or a guest-message regression.

## HARD checklist (before `git push`)

Run from the harness repo. Fetch the key at use time — never write it to disk, `.env`, a flag, chat, or git.

```bash
python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py
```

Or, if `GROK_API_KEY` is already in the environment:

```bash
cd ~/auto-reply-sqs-harness && npm run prepush
```

That is the whole gate. Do not invent a shorter path. It:

1. **Phrase/snippet sync** (`npm run eval:phrases`) — every `rubric.requiredPhrases` entry must appear in a seeded `suggestedResponseSnippet` when the scenario has one. Same-scenario required ∩ forbidden is a hard fail. No Grok needed.
2. **`npm test`** — deterministic policies. Live Grok unit tests skip without the key; the script loads SSM `/grok/api-key` so they run.
3. **Targeted live eval** — changed `eval/scenarios/<id>.json` / `eval/goldens/<id>.md` first: `npm run eval -- --only=<id>`.
4. **Full live eval** — `npm run eval` with **no** `--fail-fast` so every golden that the new phrases trip is visible in one run.

Skip steps 3–4 only when the diff is tooling/docs (`scripts/prepush.js`, `scripts/check-eval-phrases.js`, `AGENTS.md`, `docs/`, `.github/`). Any prompt, agent, tool, scenario, golden, or rubric change requires the live eval.

**Do not push if any step is red.**

## Required-phrase rules (why CI failed)

Eval scores `requiredPhrases` as **case-insensitive substrings** of `proposedResponse` (`eval/runner.js`). Adding a phrase to a golden without the draft actually saying it fails CI.

When you add or change a required phrase:

- Put the **exact substring** in the deterministic snippet / policy rewrite (e.g. `PostCheckoutParkingTool.refuseSnippet()`), not only in AGENTS.md.
- Put the same substring in `eval/scenarios/<id>.json` `rubric.requiredPhrases`.
- Mention it in `eval/goldens/<id>.md`.
- Run `npm run eval:phrases` immediately — it fails if the seeded snippet does not contain the phrase.
- Then `npm run eval -- --only=<id>` (live Grok) before the full suite.
- Grep other scenarios’ `forbiddenPhrases` for the new wording so you do not require it in one golden and forbid it in another.

Do not add required phrases the model is only “supposed to” say. If the policy does not force the words, do not require them — or force them in the policy first.

## Category flakes

A single `expectedCategory: "CANCELLATION_POLICY"` can fail as `UNCATEGORIZED` (Grok). That is not a reason to skip local eval and “see if CI is luckier.”

- Re-run `npm run eval -- --only=<id>` twice.
- Still red → fix (deterministic category, or a justified `expectedCategory` **array** of aliases). Do not widen the rubric just to go green.
- Then re-run the **full** suite. One flake can hide a real required-phrase miss if you only watch `--fail-fast`.

## After local green

Same always-push mandate as every other repo: public → `git push origin main` → `gh run watch` → private. Never ask to push.

If CI eval still fails after a green local prepush: pull the log, fix, **keep the repo public**, re-run prepush locally, push again. Do not flip private on a red eval.

## Related

- Harness `AGENTS.md` (product rules + incidents)
- Skill `always-push` (public → push → CI → private)
- SSM `/grok/api-key` (never commit; rule `02-ssm-api-credentials.md`)
