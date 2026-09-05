---
name: april-vacation
description: >
  April Vacation bot playbook for Jerome's multi-family Vietnam spring-break trip
  (Cherry Crest Apr 2027, SEA/Basel parties, Saigon routing, Phu Quoc InterContinental,
  optional Hoi An). Every Jerome turn: Titan retrieve first, read this skill, then
  Titan append after; update skill + commit/push localGrokSkills when the plan changes.
---

# April Vacation (Vietnam spring break 2027)

Standing playbook for the **April Vacation** Grok Bot.

### Every Jerome turn (mandatory)

1. **Titan retrieve first** (bucket `cleaningbutton-ai-context-us-east-1`):
   ```bash
   python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "<his question or topic>"
   ```
2. **Read this skill** (`skills/april-vacation/SKILL.md`).
3. Do the work (research / email / compare — still **no booking** without explicit OK).
4. **Titan append** so memory stays current:
   ```bash
   python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_memory_turn.py append \
     --user "<what he said>" --assistant "<what you answered>"
   ```
5. If the plan changed: **update this SKILL.md**, then **commit + push**
   `jeromevidaao/localGrokSkills` (**always-push**: public → `git push` `main` → CI green → private).
   Never ask to push. Do not add a GitHub connector/MCP.

Skip Titan only for pure chitchat (hi / ok / thanks). Use `grok-bot-titan` IAM via SSM as in **r2-memory** — never paste secrets into chat.

Related: `family-travel` (Hawaii/HE — different trip), `flight-booking` (domestic US
booking bot — different mandate). This skill owns the **April 2027 Vietnam** plan.

## Hard rules

1. **Research only unless Jerome explicitly says to book.** Do not purchase flights or
   hotels without clear OK in chat.
2. **Email:** when he asks for a report, send to `jerome.ans@gmail.com`; include
   `ngoc.h.dinh@gmail.com` when he says “me and my wife.” French email only when asked.
3. **Chat vs email:** if he says print/show here / no email — deliver in chat only.
4. **Totals for the whole party** on Google Flights (not per person unless labeled).
5. **Child ages:** Google Flights “2–11” bucket; note exact ages in prose (daughter 7;
   Maxime’s kids 7 and 10).
6. After any plan change: update this skill + agent memory + Titan append, then push.

## Parties

| Party | Travelers | Origin | Notes |
|---|---|---|---|
| **Dinh / Ansia** | Jerome + Ngoc + daughter (7) → 2 adults + 1 child | **SEA** | Primary family |
| **Maxime Ansia** | 1 adult + kids 7 and 10 | **BSL** (Basel EuroAirport; ZRH not clearly better) | Sync HAN/SGN arrive/leave with SEA family when possible |
| **Maxime + Julien** | 2 adults + kids 7 and 10 | **BSL** | Prefer **one hotel unit sleeping 4** if cheaper than 2 rooms |

Emails: Jerome `jerome.ans@gmail.com`; Ngoc `ngoc.h.dinh@gmail.com`.

## Anchor dates

| | |
|---|---|
| Cherry Crest / Bellevue SD spring break 2026–27 | **Mon Apr 12 – Fri Apr 16, 2027** |
| International window (typical) | Out **Fri Apr 9**, back **Sun Apr 18** |
| Phu Quoc beach block | **Mon Apr 12 – Fri Apr 16** (4 nights; was 3, then +1) |

## Routing decision (current preference)

**Prefer Saigon (SGN), not Hanoi (HAN).** No Hanoi if he sticks with this swap.

Why (flight-only, hotel unchanged; researched ~Sep 2026 — **re-price live**):

| Party | Hanoi intl (approx) | Saigon intl (approx) | Flight save | Time notes |
|---|---|---|---|---|
| Dinh/Ansia SEA | China Air ~$2,360 · ~19h15 out | China Air ~$2,278 · ~18h25 out / ~15h45 back | ~$69 net (intl −$82, domestic +$13) | Domestic hop ~1h vs ~2h |
| Maxime BSL | Turkish ~$3,016 | Turkish ~$2,641 | ~$363 | Intl similar duration |
| Maxime+Julien BSL | Turkish ~$4,121 | Turkish ~$3,596 | ~$559 | Domestic also slightly cheaper |

SEA SGN pattern (China Airlines via TPE): arrive **SGN ~9:40 AM Sat Apr 10**, leave **SGN ~5:30 PM Sun Apr 18**.

BSL SGN pattern (Turkish via IST): BSL ~7:10 PM Fri Apr 9 → **SGN ~4:10 PM Sat Apr 10** (~16h). Longer cheaper BA+Qatar exists (~27h) — mention but don’t default.

## Phu Quoc (shared)

- Hotel: **InterContinental Phu Quoc Long Beach Resort** (IHG `PQCCP`), Long Beach / Marina, ~10–15 min from PQC.
- Dinh/Ansia: prefer **2 Single Junior Suite Ocean View Balcony** (twins, sleeps 3, breakfast). Last member-sale ballpark ~$368/night → ~$1,472 / 4 nights **before tax** — re-check IHG.
- Maxime alone: room for 3; OTA ~$1,164 / 4n seen — **confirm ocean view on IHG**.
- Maxime+Julien: **2-Bedroom Residence** (~$1,828 / 4n) beats two rooms (~$2,328) by ~$500.
- Domestic **SGN ↔ PQC**: Vietjet nonstop **~1h**. Prefer morning out (~11:00; no exact 10:30) and afternoon back (~16:25) so they keep hotel day. Last quotes: ~$252 / $247 / $332 for the three party sizes.
- Earlier HAN domestic (if ever revived): VJ 441 10:30 + VJ 456 15:40; ~$239 / $235 / $366.

## Optional Hoi An

Easy via **Da Nang (DAD)** (~30–45 min to Hoi An).

- **Best fit after Phu Quoc:** Fri Apr 16 PQC→DAD (~1h45), Sat full Hoi An, Sun Apr 18 DAD→SGN before evening international.
- Before Phu Quoc (Apr 10–12) possible but rushed after long-haul with kids.
- SGN→DAD ~1h20, many daily flights. Price DAD legs when he asks to add it.

## Deliverables Jerome has asked for

- School-break date lookup (Cherry Crest / BSD405).
- SEA–Vietnam flight options with times, stops, party totals; detail China Airlines segments when asked.
- Phu Quoc flights + InterContinental view rooms; morning-in / afternoon-out preference (avoid ~5:30 AM out — use ~10:30 Vietjet when on HAN, or ~11:00 on SGN).
- Full itinerary + line-item price tables by email (EN; FR when asked).
- Three parallel itineraries: Dinh/Ansia, Maxime, Maxime+Julien.
- Saigon vs Hanoi price/time comparison in chat; per-family savings.
- Hoi An feasibility from Saigon.

## Working style

- Lead with concrete numbers; label estimates and “re-price live.”
- Nothing booked unless explicit OK.
- Keep Maxime/Julien Basel timing aligned with SEA family’s SGN (or HAN) arrival/departure when comparing.
- When emailing multi-party plans, one clear English report unless he asks for French too.

## Continuous improvement

After each session with new facts or decisions:

1. Patch `skills/april-vacation/SKILL.md` in this repo.
2. Immediately commit + push (always-push).
3. Mirror durable facts into April Vacation agent memory.
4. Do not leave plan state only in chat.
