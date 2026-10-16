---
name: guest-messaging-harness
description: >
  Pre-push checklist and post-fix live verify for jeromevidaao/auto-reply-sqs-harness
  (guest auto-reply / SQS / goldens / eval). Run before any commit or push that
  touches prompts, eval scenarios, goldens, required phrases, agent.js, or tools.
  After a production-miss fix is deployed: always enqueue a new grok_message SQS
  for that guest turn and monitor the live reply (not local-only replay). Use when
  working on auto-reply, guest messaging, harness evals, goldens, parking policy,
  or /guest-messaging-harness.
---

# Guest-messaging harness — pre-push

Repo: `~/auto-reply-sqs-harness` (`jeromevidaao/auto-reply-sqs-harness`).  
Push to `main` auto-deploys Lambda `guest-messaging-agent-harness`.  
CI `eval` job is live Grok + every golden (`npm run eval -- --fail-fast`).

Live Grok responses are cached in DynamoDB `grok-eval-cache` when the composed
prompt is unchanged (`GROK_EVAL_CACHE=1`, default for prepush/eval). Bypass with
`GROK_EVAL_CACHE=bypass`. See harness `docs/grok-eval-cache.md`. Production Lambda
must leave the flag unset.

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
2. **`npm test`** — deterministic policies. Prepush sets `SKIP_LIVE_GROK_UNIT=1` (same as CI) so live-Grok *unit* describes are skipped; the script still loads SSM `/grok/api-key` for the live **eval** steps. Force live unit: `RUN_LIVE_GROK_UNIT=1`.
3. **Targeted live eval** — changed `eval/scenarios/<id>.json` / `eval/goldens/<id>.md` first: `npm run eval -- --only=<id>`.
4. **Full live eval** — `npm run eval` with **no** `--fail-fast` so every golden that the new phrases trip is visible in one run. Unchanged push gate.

Skip steps 3–4 only when the diff is tooling/docs (`scripts/prepush.js`, `scripts/check-eval-phrases.js`, `AGENTS.md`, `docs/`, `.github/`). Any prompt, agent, tool, scenario, golden, or rubric change requires the live eval.

**Do not push if any step is red.**

### Live unit vs live eval (prepush)

Same semantics as CI: `SKIP_LIVE_GROK_UNIT=1` for `npm test` by default; **full live eval is still required** for guest-facing diffs. See harness `tests/liveGrokUnitGate.js` / `AGENTS.md`. Help: `python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py --help`.


## Credential / WiFi / SSID golden sync (HARD — CI 35292706988)

When you change WiFi credential resolution (`_wifiCredentials`, check-in templates, `hostContacts` / SSM `wifiSsid`/`wifiPassword`, `{{WIFI_SSID}}` placeholders, or wifi.md):

1. **Grep the blast radius** before push:
   ```bash
   rg -n "TEST_WIFI|Ansia|10286500|Pineland|lobsterbake|WIFI_SSID|wifiPassword|wifiSsid" eval/ tests/ prompts/
   ```
2. Update **every** scenario/golden whose `requiredPhrases` / seeded snippet asserts an SSID or password in the **same commit/PR**. Do not ship template Pineland while Jane still requires `TEST_WIFI_SSID`.
3. Run the previously-failing eval locally until green **before** push:
   ```bash
   npm run eval -- --only=jane-tv-wifi-connect,sarah-wifi-compliment-early-checkin
   npm test
   ```
4. **Never push on red local eval.** Harden every CI fail permanently — CI must not be the first time credential phrase mismatches are found.

Pine St / West End Victorian (apt-1b/2/3): canonical WiFi is **Pineland** / **lobsterbake** from check-in templates — never Ansia_2.4 / 10286500.

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



## Credential / policy blast radius (HARD — 2026-09-18)

**Incident:** Sarah WiFi compliment + early check-in. Global SSM `/host/contacts-json` had `wifiSsid=Ansia_2.4` / `wifiPassword=10286500`. Policy switched Pine St units to check-in templates (`Pineland` / `lobsterbake`). First push updated Sarah tests but left **Jane TV WiFi** golden requiring `TEST_WIFI_SSID` / `test-wifi-password` → CI red.

When you change **any** of:
- WiFi credential source (SSM hostContacts vs check-in templates vs per-property)
- `_applyWifiPolicy` / early-check-in / multi-intent merge
- SSID or password strings that appear in replies

You MUST in the **same commit/PR**:

1. `rg -n "TEST_WIFI|Ansia_2|10286500|WIFI_SSID|wifiSsid|requiredPhrases" eval/ tests/` and update **every** scenario/golden that asserts old phrases.
2. Run locally **before push** (not "CI will tell us"):
   ```bash
   npm run eval:phrases
   npm test
   npm run eval -- --only=<every-changed-scenario-id>
   npm run prepush   # full live eval, no --fail-fast
   ```
3. **Do not push** until the previously-failing eval and full prepush are green on this machine.
4. If CI fails: pull the log, fix, re-run **that** `--only=<id>` locally to green, then full prepush, then push again. Never push a "hopefully fixed" sibling golden untested.

Pine St / West End Victorian WiFi in replies and goldens: **Pineland** / **lobsterbake** (from check-in templates). Never `Ansia_2.4` / `10286500` for those units.

Sarah-style "I love your WiFi password" + early check-in → **EARLY_CHECKIN** classic (message when cleaning finishes / unit ready). Compliment ≠ password ask; do not dump credentials.


## Judge common sense (Sarah 2026-09-17)

If history shows the host already sent WiFi (or the guest **complimented** the password), the conversation judge + `checkDraftClaims` **must REJECT/REVISE** any draft that re-sends SSID/password. Answer the real ask (early check-in classic). Never APPROVE a credential dump after "I love your WiFi password."

## Never skip prepush (HARD — 2026-09-22 towel/image pile-up)

**Incident:** Apt 2/3 towel copy (Ikea → chaise) and Hospitable `images[]` photo attach were pushed after only unit tests / `--only=kenneth-extra-towels-sofa`. Multiple CI runs stacked; Android Ring-live also failed compile on an unescaped test string in the same window.

**Before every `git push` on this repo**, including changes that look "small":

- `src/clients/HospitableClient.js` send path / `images` / attachments
- `lambda/handler.js` send wiring / `replyImages`
- guest-guide photo URLs / S3 CDN assets referenced by replies
- prompts, agent policy, claimCheck, goldens, scenarios

…you MUST run:

```bash
python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py
```

Do **not** treat those as "tooling/docs" skip cases. Do **not** push on green `--only=<one-id>` alone when agent/prompts/policy/handler changed — full live eval (no `--fail-fast`) is required.

If CI is already red or stacked: fix tip, run full prepush locally to green, push once. Do not pile more "hopefully fixed" commits.

## Git pre-push approvals hook (HARD — 2026-09-22)

Jerome: **run approvals before pushing** so CI is never the first place required-phrase / eval failures show up.

Mechanical gate (do this once per clone, then leave it on):

```bash
cd /path/to/auto-reply-sqs-harness
git config core.hooksPath scripts/git-hooks
```

`scripts/git-hooks/pre-push` blocks `git push` unless `.git/harness-prepush-ok` matches `HEAD`. A successful `npm run prepush` / `python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py` writes that stamp.

Emergency bypass only: `HARNESS_ALLOW_PUSH_WITHOUT_PREPUSH=1 git push` (say why in the commit/PR notes — not for normal work).

Agent rule: after any harness change, run full prepush to green, **then** push. Do not push on unit tests or a single `--only=` eval alone when agent/prompts/handler/policy changed.

## Related


- Harness `AGENTS.md` (product rules + incidents)
- Skill `always-push` (public → push → CI → private)
- SSM `/grok/api-key` (never commit; rule `02-ssm-api-credentials.md`)

## Dirty-linen checkout disposition (HARD — Isabella 2026-09-26)

Guest asks to change linens / where to put dirty ones at checkout → auto-reply **must** say both **strip** and **bathroom floor**. Distinct from EXTRA_LINENS (chaise find-more towels/sheets).

- `draftHasDirtyLinenBathroomGuidance` requires **BOTH** phrases (CI flake: Conversation Judge rewrite can keep "bathroom floor" but drop "strip").
- Policy / `claimCheck` force the canonical snippet when either phrase is missing.
- Scenario `isabella-dirty-linens-bathroom` `requiredPhrases`: `bathroom floor`, `strip`.
- `CleaningIssueTool` must **not** treat dirty-linen disposition as a cleaning complaint (bare "dirty" must not escalate / wipe CHECKOUT).

## HE cleaning-fee gate (HARD — Katie / Caroline / Jessica)

**Never** approve or pre-approve an HE stay until `cleaningFeeAccepted: true`. Ask the fee first. Cancel-after-wrong-approve is **not** recovery — do not use it as a fix path.

## sendMessage junk guard (HARD — Jessica probe + Gwynneth bare Name!)

Shared util `src/utils/sendableMessageContent.js` (`isSendableMessageContent`) — used by **both** HomeExchange and Hospitable send paths.

Refuse before POST:
- empty / whitespace
- 1-character
- literal `"x"` / probe junk (`ok`, `?`, `.`)
- **bare guest Name!** only: `/^\s*[A-Za-z][A-Za-z'’\-]{0,40}\s*[!?.…]*\s*$/` (Gwynneth 2026-09-27 shipped `Gwynneth!`)

### Gwynneth arrival heads-up (2026-09-27)

After unit-ready, guest "On our way! Be there soon." (no thank-you):
1. Post-welcome thank-you must **require thank-you intent** — do not force `You're welcome, Name!` on arrival FYI.
2. `_stripFalseYoureWelcome` must not leave bare `Name!` (comma must not match `[!.,]` and gut-threshold must reject Name!-only remainder).
3. FYI heads-up acknowledgement policy → customize from history + guest wording (Jerome: "Thank you for letting us know, have a safe drive") — not only rigid "Sounds good".
4. Scenario `gwynneth-unit-ready-on-our-way` + unit tests in `tests/sendableMessageContent.test.js` / `tests/gwynnethUnitReadyArrivalAck.test.js`.

Do not re-message the live guest unless Jerome asks.


## Never invent guest sentiment / praise unmentioned topics (HARD — Eve Apt 1B 2026-10-01, generic)

Guest acks checkout instructions with "Perfect! We got it. We will message when we leave" (no WiFi words) → must NOT reply "glad you like the WiFi." Same for parking / view / bed / location / any amenity the guest never raised.

- **Judge stop-gate:** conversation-judge HARD rule — REVISE drafts that invent guest liking a topic absent from the current guest message.
- claimCheck `invented_guest_sentiment` strips invented praise (WiFi, parking, view, bed, location, …) when guest never mentioned that topic.
- `_guestSignalsKnowsWifi` must NOT treat bare `got it` as WiFi knowledge — require wifi/password/network in the same message.
- `_applyWifiEarlyCheckinMultiIntentPolicy` WiFi-compliment-alone path only when current message is a real WiFi compliment/ack.
- Scenario `eve-checkout-ack-no-wifi-praise` + `tests/eveCheckoutAckNoWifiPraise.test.js` + `tests/inventedGuestSentimentClaimCheck.test.js`.

Do not re-message Eve unless Jerome asks.

## Trailing thanks on a request (HARD — Eve Apt 1B 2026-09-30)

Guest asks to drop bags / check in earlier than 4pm and ends with "Thanks!" (no `?`). Production sent only "You're welcome, Eve!".

- "We are in the area" is sightseeing, **not** already inside the unit. Do not let `_alreadyInUnit` match bare "we are in".
- `_applyInStaySeeYouSoonPolicy` must not collapse an early-check-in draft that mentions 4pm into bare You're welcome.
- Trailing thanks does **not** make a request thanks-only (`guestMessageHasActionableAsk` / `_guestHasActionableAsk`). Do not set `recentWelcomeSent` or force the post-welcome You're-welcome short path.
- Answer with classic early check-in: 4pm, can't guarantee, getting the unit ready, message you. Scenario `eve-early-checkin-trailing-thanks`.

Do not re-message Eve unless Jerome asks.

## Apt 1B layout / TV / listing photo (HARD — Sc 2025-11; Jerome approved 2026-09-28)

Downtown Studio / 53 Pine Apt 1B:
- Kind of a **junior one-bedroom** — **two spaces**, not fully separated (**no door**). Bedroom area + living/kitchen side of the same open unit — not a true closed-off 1BR.
- **TV is in the bedroom area.**
- Never hedge ("I'm not sure which photo" / "get back to you") when these facts exist. Do not invent bath-across-hall / unstated floor details.

Property file `prompts/properties/1b.md`. Category `UNIT_LAYOUT_QUESTION` in misc-questions. Deterministic `_applyApt1bLayoutPolicy` + claimCheck `force_apt1b_layout_tv`. Scenario `sc-apt1b-layout-tv-photo`. Do not re-message Sc unless Jerome asks.

## Post-fix live verify via SQS (HARD — Jerome 2026-09-30)

After **any** production-miss fix that should change what a guest sees:

1. Ship as usual: TDD golden → prepush → push → CI green → Lambda deploy → repo private.
2. **Do not stop at local `node scripts/replay-*.js` dry-run.** Prefer the real path.
3. **Enqueue a new message on `grok_message`** that replicates the guest’s last turn (same reservation / platform / body shape as production `message.created`). Use or extend a `scripts/replay-*.js` that `aws sqs send-message`s to `GROK_MESSAGE_QUEUE_URL` / `https://sqs.us-east-1.amazonaws.com/834917996497/grok_message` (see `scripts/replay-rebecca-review-promise.js`, `replay-real-sqs.js`, Eve/Michael replay scripts).
4. **Monitor** until the harness posts the live host reply (CloudWatch / Hospitable thread / FCM as appropriate). Confirm text + time PT to Jerome.
5. Only say “replied” after that live send is confirmed — not when CI is green.

Local `--send` Hospitable shortcuts are a fallback if SQS cannot be used; default is **SQS → Lambda → real send**.

## Push gate (unchanged)

Full gate before any harness push:

```bash
python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py
```

Leave `git config core.hooksPath scripts/git-hooks` on. Do not touch harness push when another agent owns an in-flight Isabella prepush.

## Permanent booking-safety rules (Jerome, 2026-10-15)

1. **HE↔Airbnb sync is two-way and fails closed.** `pine-booking-sync` (every 15 min) blocks Airbnb nights on HE and active HE stays on Airbnb/Hospitable, reads every write back, and on any read/write failure blocks the dates on both sides rather than leaving them open. Any skipped, unconfirmed or partial block alarms (SNS `homeexchange-alerts` → ansia@mail.grokbot.com; DLQ `pine-booking-guard-dlq`). `pine-booking-audit` (hourly) is the independent overlap check.
2. **Never send a door code or check-in instructions to a stay that overlaps another booking.** The harness HE check-in sender (`src/useCases/heCheckinOverlapGuard.js`) calls `pine-booking-audit` before building the message and holds + alarms on: an unresolved overlap for that conversation, a manual hold (`DEFAULT_HE_CHECKIN_HOLD_CONVS` / env `HE_CHECKIN_HOLD_CONVS`), or missing/erroring audit data (fail closed). The cleaningbutton-api scheduler hold is `checkinInstructionsQueuedAt = "HOLD:..."` on the conversation in DynamoDB `homeexchangeMessageState` pk=`cursor` (do not run the poll with `force=1` while a hold is set). Remove a hold only after Jerome confirms the overlap is resolved.
3. **Every change ships with a test plus a live readback on both platforms** (HE calendar and Airbnb/Hospitable calendar, or the live Lambda result), and keeps a published Lambda version for rollback.

Skills hold SSM path names only (e.g. `/homeexchange/bearer-token`), never secret values.

## 2026-10-15 — guest-message gate
- Every guest-facing message needs Jerome's OK; check the thread for an existing copy before sending; read back after send (one copy only).
- The HE auto-reply sent Katie (conv 95201321) an unapproved message offering other units/dates at 2:21pm PT (msg 1003802226). Auto-replies must not fire on threads under manual handling / active holds.

## HE booking guard in the harness (2026-10-15, end of day)
See `home-exchange` skill → "Booking guard / first-stay ops" for system, IDs, alarms.
- **Reply gate:** hold + alarm on muted convs (`DEFAULT_HE_MUTED_CONVS` / `HE_MUTED_CONVS`), cancelled exchange (status 6), overlap, unreadable conv, or `pine-booking-audit` error. Auto-replies never fire on cancelled exchanges.
- **Check-in:** `heCheckinOverlapGuard.js`; cancelled/overlapping stays never get instructions or PINs. DDB `homeexchangeMessageState` marker `checkinInstructionsQueuedAt`.
- **IAM:** harness role (ARN includes `service-role/`) has `lambda:InvokeFunction` on `pine-booking-audit`.
- **Own hold = open for same guest:** a `Hold for <guest>` block must not make the harness decline that guest's re-request (Katie auto-declined 2:36 PM PT).
- **Inbox paging:** old inbox call ignores paging; use newer list or paginate `first`/`after`, fail closed if incomplete.
- Guest messages need Jerome's direct OK in the owning bot's chat. Never auto-approve an overlapping HE request. Every change = test + live read-back.


## HE guest phone for door codes (2026-10-15, Jerome approved 3:03 PM PT)

**Problem:** Newer BFF-only conversations (ids ≥ ~1e9, e.g. Katie `1000923027`) 404 on `GET api…/v3/conversations/me/{id}`. BFF `exchange/v2` and `v4/conversations` return guest with only `id` + `first_name` — **no phone**. Old v3 detail still has `guest.phone`.

**Primary source (works for BFF-only + finalized stays):**
`GET https://api.homeexchange.com/v1/exchanges/{conversationId}/get-exchanges`
→ use `additional_informations.phone` when `additional_informations.is == "guest"`.
(The nested `guest` object on that payload still omits phone.) Phone appears at/after finalization, not N days before arrival.

**Fallback:** same guest id’s phone from another of their v3 conversation details (Katie: `95201321`).

**Fail closed:** no resolvable phone → no PIN load, no check-in send.

**Never** ask the guest for their phone. **Never** log/print phone numbers (report `last4 present: yes/no` + `phoneSource` only).

**7-day private alert:** `addDeleteCodeWiFiPyschlage` on each sync runs `he_check_missing_phones_upcoming` — confirmed Pine HE stay with check-in ≤7 days and no phone → SNS `homeexchange-alerts` only, deduped in DynamoDB `homeexchangeMessageState` pk `he_missing_phone#{conv}#{check_in}#{day}`. No guest message / no draft.

**Shipped:**
- PIN Lambda `addDeleteCodeWiFiPyschlage` commit `0186c1e`, published version **7** (rollback: version **6** / prior sha `b83980b`).
- Harness `guest-messaging-agent-harness` commit `2fdbf64`, published version **8** (rollback: version **7** / prior sha `d4d8440`).
- Dry-run proof (2026-10-15): `he_pin_guard_dry_run` today=`2026-10-29` listUpcoming → Katie conv `1000923027` `phoneSource=get-exchanges` `last4Present=yes` `pinResolves=true`. Live harness `resolveGuestPhoneLast4` same source/result. No PIN load, no guest message.

## HE auto-reply global kill switch (pause / resume) — added 2026-10-16
Jerome 2026-10-16 09:40 PT: "Pause all HE auto reply for now." **Currently PAUSED. Do not resume until Jerome says so in chat.**
- Switch: SSM `/homeexchange/autoreply-paused` (String, us-east-1) **and** Lambda env `HE_AUTOREPLY_PAUSED` on `guest-messaging-agent-harness`. Paused if env is `true` OR SSM is anything but `false`. SSM missing/unreadable = paused (fail closed).
- Enforced in `HomeExchangeClient.sendMessage / approveConversation / declineConversation` (harness 82cb8ec), so it covers every automated HE write: auto-replies, reply-gate sends, HE check-in instructions (homeExchangeCheckin.js, same path, so held), pre-approve/approve/decline auto-actions, early-checkin / ring-smoke / keypad-lockout HE notices. Hospitable/Airbnb sends are NOT affected.
- Held sends log `[he_autoreply_paused]` once per conv+op per container, no SNS.
- Not touched: pine-booking-sync, pine-booking-audit, alarms, PIN loading (addDeleteCodeWiFiPyschlage), homeexchange-processor (calendar POSTs only, never messages).
- Stopgap also applied 09:41 PT: env `HE_MUTED_CONVS` = all ~143 known Pine HE conv ids. Pre-pause env saved at /workspace/harness-env-before-pause-20261016.json (had no HE_MUTED_CONVS). Rollback code version: published version 9 (= 2fdbf64).
- Probe (read-only, never sends): `aws lambda invoke --function-name guest-messaging-agent-harness --region us-east-1 --cli-binary-format raw-in-base64-out --payload '{"he_autoreply_pause_probe":true,"conversationId":"1000923027"}' /tmp/p.json && cat /tmp/p.json`
- **Pause:** `aws ssm put-parameter --region us-east-1 --name /homeexchange/autoreply-paused --type String --value true --overwrite` (instant, next send).
- **Resume (only on Jerome's explicit OK):**
  1. `aws ssm put-parameter --region us-east-1 --name /homeexchange/autoreply-paused --type String --value false --overwrite`
  2. Restore env from the backup (removes HE_AUTOREPLY_PAUSED and the stopgap HE_MUTED_CONVS): `python3 -c "import json;print(json.dumps({'Variables':json.load(open('/workspace/harness-env-before-pause-20261016.json'))['Environment']['Variables']}))" > /tmp/env.json && aws lambda update-function-configuration --function-name guest-messaging-agent-harness --region us-east-1 --environment file:///tmp/env.json` (re-read current env first in case other vars changed since).
  3. Run the probe; expect `wouldSend:true`.
  - **IAM gap (2026-10-16):** role auto-reply-sqs-role-3i2ozrop gets AccessDenied on ssm:GetParameter for /homeexchange/autoreply-paused, so SSM reads fail closed (= paused). Before resume, Jerome must add ssm:GetParameter on arn:aws:ssm:us-east-1:834917996497:parameter/homeexchange/autoreply-paused to that role (grok-bot-titan has no IAM rights).
  - Note: messages held while paused are not auto-resent; check-in instructions whose window passed need a manual look (Katie 1000923027 due ~Oct 26).

## HE approval mode (run every HE send by Jerome first) — added 2026-10-16 10:12 PT
Jerome: "instead of pausing, run them by me here for approval prior sending". Code: auto-reply-sqs-harness `21a1fa4`, `3360bc8`, `20c4ebb`, `c54fcf2` (src/useCases/heApprovalMode.js).
- **On when** the kill switch is on (env `HE_AUTOREPLY_PAUSED=true` on guest-messaging-agent-harness; keep it true). Drafts are generated as normal (classify, draft, reviewer/judge, shared categories, check-in template). Every HE write (`sendMessage`, `approveConversation`, `declineConversation`) is intercepted by a client Proxy: it stores a pending item and publishes ONE SNS to `homeexchange-alerts`, then throws `he_pending_approval:<op>:<conv>:<approvalId>` (terminal, no SQS retry, no FCM "send failed"). Nothing posts. The real client still asserts the pause too (double guard).
- **Covers** guest replies, check-in instructions (kind `checkin_instructions`), pre-approve and decline (described as the proposed action). NOT covered (still just held by the pause, no approval card): ring-smoke / keypad-lockout / early-check-in notices.
- **Gates still apply** before drafting: cancelled exchange, overlap (pine-booking-audit), unreadable thread. In approval mode a conversation mute does NOT skip draft generation. The 143-conv `HE_MUTED_CONVS` stopgap was removed 10:35 PT (backup: /workspace/harness-env-backup-before-unmute-20261016.json).
- **Store:** role auto-reply-sqs-role-3i2ozrop has NO access to homeexchangeMessageState (AccessDenied on Put/Get/Update/Delete), so env `HE_APPROVAL_TABLE=airbnb-harness-dedup`, `HE_APPROVAL_KEY_ATTR=webhookId`, key `he_pending#<approvalId>` (no ttl attr, so it persists). Role has only Put+Get there, so status changes are conditional full-item Puts. Fields: status (pending/sending/sent/send_failed), op, kind, conversationId, text (exact), actionArgs, guestName, unit, checkIn, checkOut, guestMessage, createdAt, proof. If Jerome grants the role Put/Get on homeexchangeMessageState, just drop the two env vars.
- **Dedupe:** approvalId = `he` + sha256(conv|op|normalized guest message|discriminator)[0:12]. Same guest message → same id → no 2nd row or email (log `deduped:true`). Check-in uses discriminator `checkin:<checkIn>`.
- **APPROVAL email** (to ansia@mail.grokbot.com, SNS JSON envelope; read the `Message` field):
  Subject `APPROVAL: HE reply for <first name> (conv <id>)`. Body: Approval id, Conversation, Guest, Unit, Stay `<in> to <out>`, Kind, Proposed action, Guest's latest message, the exact proposed reply between `-----` lines (or the action args), and the send command. Relay it to Jerome in chat verbatim (proposed text exact) and wait for his explicit OK. These are NOT alarms: the alarm responder must not treat them as incidents.
- **Send an approved draft (only after Jerome says yes to that specific draft):**
  `echo '{"he_send_approved":"<approvalId>"}' > /tmp/sa.json && aws lambda invoke --region us-east-1 --function-name guest-messaging-agent-harness --payload fileb:///tmp/sa.json /tmp/sa-out.json && cat /tmp/sa-out.json`
  It re-runs the cancel/overlap gate, claims pending→sending (concurrent invokes post once), posts exactly the stored text with `heApproved` (bypasses only the pause), marks `sent`+`sentAt`. Refuses: `bad_approval_id`, `not_found`, `status_sent`/`status_send_failed`/`already_claimed`, `gate:<reason>` (e.g. cancelled), `proof_item_never_sendable`. A failed post becomes `send_failed` and is never retried automatically (check the thread before doing anything by hand). If Jerome edits the text, post his version manually instead; never edit the stored row to send.
- **Stale caution:** only approve drafts for fresh messages. A replay of an old message can produce a wrong action (e.g. replaying Katie's 10-15 "submitting as discussed" proposed DECLINING her confirmed stay because her own block makes the dates look closed).
- **Proof / test replay:** add top-level `"he_approval_proof": true` to an SQS-shaped replay event (only works in approval mode). Skips the already-on-thread check so an answered message still yields a draft; the item is `proof:true`, the email starts "TEST / PROOF ONLY", and send-approved always refuses it. Proof 10-16 10:33 PT: Catherine conv 95940761 → `heea1dad10bc95`, text "You're welcome, Catherine!", replay again → deduped. Payload: test-payloads/he-95940761-approval-replay.json.
- **Store probe:** `{"he_approval_store_probe":true}` writes/deletes a probe row per candidate table and reports put/get/update/delete (delete is denied on the dedup table, so remove `he_pending#probe-*` rows with your own creds afterwards).
- **Versions / rollback:** v10 = pre-approval-mode (cce9aae kill switch only, old env with mutes); v11 = approval mode c54fcf2. Code rollback: redeploy cce9aae or `git revert` the 4 commits; env rollback: restore /workspace/harness-env-backup-before-approval-env-20261016.json (has the 143 mutes, no approval vars).
- **Resume full auto later:** needs Jerome's OK, the SSM read permission (see kill switch section), then set HE_AUTOREPLY_PAUSED=false and SSM false.

## Own-guest holds never make a guest's own dates "not open" — added 2026-10-16 10:54 PT
Bug: Katie (HE guest id 4052575) was auto-declined on her re-request 1000923027 (10-15 2:36 PM PT) and a replay proposed declining her finalized stay, because Apt 1B nights carried "Hold for Katie McGovern HE conv 95201321" (her old conv) and HE showed them RESERVED for her own exchange. Fix: auto-reply-sqs-harness `dafa8a4` (src/useCases/heOwnGuestBlocks.js), Lambda v12 (rollback v11).
- Hospitable/Airbnb calendar block whose note names any of this guest's ids counts as OPEN for that guest only. Ids = current conv, every exchange id on it, the HE guest user id, plus every other inbox conv (listConversations limit 50) whose exchanges/interlocutor have the same guest id, and their exchange ids. Only digit runs of 5+ are compared; name alone never matches. Covers "HomeExchange <guest> conv <id>", "Hold for <guest> HE conv <id>", "MANUAL hold for <guest> HE conv <id>". Reasons show `ownGuestHold: true`.
- HE calendar RESERVED nights of the guest's own status 1/3 exchange count open (passed as leftoverNights to analyzeHeCalendarOpen).
- Still unavailable: real Airbnb reservations (Hospitable reservations list) and any other guest's hold.
- Hard guard: no decline for a conversation with a pre-approved (1) or finalized (3) exchange: shouldDeclineHeRequest returns false, HomeExchangeClient.declineConversation throws `he_decline_refused_active_exchange` (fails closed if unreadable), and the approval-mode wrapper refuses before storing/emailing a decline.
- Proof 10-16 11:04 PT: Katie 10-15 message replayed (proof=true) → calendar open (all 5 nights ownGuestHold), no decline, pending proof draft `he4696d8fdbc6a` (never sendable). Residual: for a finalized stay the draft still re-asks the cleaning fee ($80) — first-message flow isn't skipped for an already-finalized exchange; don't approve such drafts.

## Accepted alteration context + confirmation (Rachel Apt #3, 2026-10-16) — branch only, awaiting Jerome
Incident: Jerome accepted Rachel's alteration (Dec 20–Jan 4 → Dec 24–26, `reservation.changed` 12:23 PT). The guest sent "❤️" at 12:26, and at 12:29 PT the harness replied with the cancellation-policy link (help/article/475) "for altering or refunds".
- Root cause: Hospitable `GET /reservations/{id}/messages` has NO system "Request accepted" event, and `reservation.changed` carries only the NEW dates (`alterations: null`, no previous dates). The drafter and judge saw only the guest's earlier change/financial message. The judge's critique pass is what ADDED the 475 link. Prod has no cache.
- No alteration-accepted confirmation path ever existed, so this is not a regression. The lifecycle branch only does the pending→accept welcome (since 25f929b, 2026-08-01).
- Fix (branch `fix/rachel-alteration-accepted-context`, commit 157b125, `src/utils/reservationAlteration.js`): snapshots `resv_dates#<resId>` and `resv_alter#<resId>` in airbnb-harness-dedup. One confirmation post per change, deduped by `resv_alter_confirmed#`. A `System` history event, a judge CRITICAL block, and a deterministic guard before and after the judge.
- Limitation: a change is only detected when an earlier snapshot of that reservation exists.
- Lesson: give the judge reservation events, not just messages. Policy-link rules must check whether a request is still OPEN.
