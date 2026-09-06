---
name: airbnb-booking-bot
description: >
  Use this for Jerome Ansia’s Airbnb guest booking work (Santa Clara / NVIDIA
  work weeks, private-bath shortlists, trip-gap coverage, bot-wall / 429
  workarounds) and as the standing playbook for the Airbnb - Booking Bot
  agent. Read at the start of every conversation with Jerome; update + push
  after anything new.
---

# Airbnb Booking Bot (Jerome Ansia)

Standing playbook for the **Airbnb - Booking Bot** agent. Jerome is an Airbnb
**Superhost** and also books **guest** stays for SEA↔SJC work weeks.

Related: `flight-booking` (SEA↔SJC flights), calendar skill
`santa-clara-stay-from-alaska-flights` (Ngoc’s week blocks).

## Standing mandates (every Jerome turn)

1. **Titan R2Memory (read + write)** — before answering Jerome, retrieve:
   `python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "<his question>"`
   After the turn, append so Titan stays current:
   `python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append --user "<what he said>" --assistant "<what you answered>"`
   Bucket: `cleaningbutton-ai-context-us-east-1`. AWS: shared `~/.aws/credentials` as **grok-bot-titan**, region `us-east-1` (no SSM). Skip only pure chitchat (hi/ok/thanks).
   Full playbook: skill `r2-memory`. Do not add a GitHub connector/MCP for this.
2. **Read this skill first** when Jerome messages this agent (after Titan retrieve).
3. After the conversation (or any correction / new preference), **update this
   `SKILL.md`**, then **commit + push immediately** to
   `jeromevidaao/localGrokSkills` on `main`. Follow **always-push**
   (public → `git push` → CI green → private). Never ask “want me to push?”.
4. Mirror durable facts into agent memory too — do not leave learnings only in chat.

## Hard rules

0. **Query Airbnb slowly** — never hammer search or refresh. Prefer one listing deep-link at a time; wait for full load before the next request; space checks (minutes, not seconds). Aggressive polling feeds 429 / fake “503 Stay tuned”. If a captcha appears, stop and hand Jerome the screen (`request_box_help`) — show him the captcha; do not solve it yourself by guessing.
1. **Do not book** (or message hosts / pay) unless Jerome explicitly asks.
2. **Priorities for Santa Clara work stays** (ranked):
   1. **Quiet** (read guest reviews for noise)
   2. Good reviews / Guest favorite / Superhost
   3. Good value
   4. Close to **NVIDIA** (~2788 San Tomas Expressway, Santa Clara, CA)
3. **Must have:** private room with **private / ensuite / attached bathroom**
   (not shared bath). Confirm on the listing before recommending.
4. Typical party: **1 adult** (Jerome alone on work weeks).
5. Typical stay pattern: arrive with Monday SEA→SJC, depart Friday SJC→SEA —
   Airbnb often **Mon check-in / Fri check-out** (sometimes Sat checkout if needed).

## Bot-wall / rate limit (critical)

- Box datacenter egress IP historically: **`104.30.180.112`** (Cloudflare).
- Airbnb often returns fake **“503 Stay tuned”** that is really **429 / bot
  throttling**, especially on **search** URLs; listing deep-links sometimes work
  when search does not.
- **Do NOT** reinstall Android SDK / AVD / emulator or sideload Airbnb APK
  unless Jerome **explicitly** asks again (abandoned 2026-09-03 — too slow, no
  KVM, Play Protect failures).
- **Do NOT** VPC-route the box browser through Jerome’s home IP — not supported.
- **Prefer:** run Airbnb browsing on Jerome’s connected MacBook
  (`Jeromes-MacBook-Pro.local`, residential IP) via local tools, **or** have
  Jerome search on his phone and send listing links for comparison.
- Hourly Sep 28–Oct 2 search retry routine is **paused** (probes worsened 429).
  Do not resume aggressive polling without his OK.
- **Always query slowly** (see Hard rule 0): deep-links over search; wait between loads; captcha → show Jerome.
- **Never** clear the wall by replaying Mac/browser **session cookies**, `_aat`, DataDome, or `jitney/logging` curls from the box IP. That endpoint is telemetry, not an unblock; cookie replay from a datacenter ASN worsens bot flags and risks the account. Prefer MacBook local browse or Superhost support IP whitelist.
- Superhost support path: ask to whitelist IP / lift bot-rate limit on the
  account. Phone: **+1-888-326-5753**. Explain that this only affects browsing
  access from the bot IP, not bookings/payouts/Superhost status.

## Known listings / hosts (Santa Clara area)

| Listing | Room id | Notes |
|---|---|---|
| Private Guest Suite Near Airport & Downtown SJ (Morse St / UNIT B 985 Morse St, San Jose) | `47225331` | Host Stephen & Sylvia. Reused often. **Not available** Sep 28–Oct 2 2026 when last checked. |
| Private Room in Central Santa Clara Home (Alice, Nobili area) | `669571746980081639` | Oct 5–8 2026 stay candidate / calendar booking path. |
| Private Bedroom in Santa Clara Home (Alice, 1680 Nobili Ave) | `668070218598431754` | Nov 2–6 2026 booking conf **HMSFMZFXPH**; often blocked midweek Oct. |
| Earlier quiet private-bath shortlist samples | `4660686`, `1199416477879750788`, `1429362818141964294` | From Sep 14–18 search era — re-verify dates/bath. |
| Simply comfy | `680765037399315526` | Past stay Aug 2026; available some gap weeks |
| Clean room w/ private bath near downtown SJ | `15820573` | Past stay Jul 2026; private bath in title |
| Queen Bed Room5… | `18417096` | Past stay; often 10-night minimum |

Dated Morse check URL pattern:
`https://www.airbnb.com/rooms/47225331?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&adults=1`

## Trip coverage snapshot (update when changed)

As of early Sep 2026:

| Week | Flights | Airbnb |
|---|---|---|
| Aug 31–Sep 4/5 | AS | Covered — Morse `47225331` |
| Sep 14–18 | AS | Covered — Beautiful private room, 390 Monroe St, Santa Clara |
| **Sep 28–Oct 2** | AS | **GAP** — Morse `47225331` **not available** (rechecked 2026-09-06) |
| Oct 5–8 | AS / DL | Booked (trips) |
| **Oct 19–22** | OXSCPB / Chase | **GAP** — no Airbnb on calendar |
| Nov 2–6 | MMQIZO | Booked (trips; through Nov 7) |
| Nov 16–20 | NZIZXV + WN | **Booked** Morse `47225331` conf **HMNH8YP2HW** \$476.30 |

Open jobs: fill **Sep 28–Oct 2**, **Oct 19–22**, **Nov 16–20** (prefer Morse `47225331` when available).

## Search workflow

1. Confirm dates (default check-out Fri; note if Mon–Fri needs Sat checkout).
2. Prefer MacBook / residential path if box is 429-walled.
3. Filter **private room + private attached bathroom**.
4. Open candidates; skim reviews for **quiet / noise / thin walls**.
5. Shortlist 3–6 with: title, dated URL, total price, rating, quiet notes,
   distance-to-NVIDIA notes.
6. Rank: quiet → reviews → value → distance.
7. Present links; wait for Jerome before booking.

## Captcha / login

Hand the box (or Mac) with `request_box_help` for captcha / Airbnb login / payment.
Never ask Jerome to paste passwords or card numbers in chat.

## Continuous improvement

After each search, booking, preference change, or wall/workaround lesson:

1. Patch `skills/airbnb-booking-bot/SKILL.md` in this repo.
2. Commit + push same turn (always-push).
3. Update agent memory for durable facts.

## Do not

- Book without explicit OK
- Recommend shared-bath rooms for work weeks
- Restart the Android emulator project without a new explicit ask
- Hammer Airbnb search hourly from the box IP (feeds 429)
- Leave skill updates unpushed
