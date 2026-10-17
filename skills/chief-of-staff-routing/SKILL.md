---
name: chief-of-staff-routing
description: >-
  Use this whenever coordinating Jerome’s bots, deciding which specialist owns
  an ask, fanning out Chrome cleanup, or updating the Chief of staff routing map
  — read before messaging teammates or doing domain work yourself.
---
# Chief of staff — specialist routing

Standing playbook for the **Chief of staff** bot. Prefer routing domain work to the owning specialist over doing it yourself. Keep live agent ids from the teammates list (ids change); this skill is ownership lanes and hard rules.

## Role

- Coordinate specialists, keep skills/Titan/shared setup aligned, surface only real decisions or blockers.
- Fan out daily unused Chrome tab cleanup (~8:27am PT).
- Do **not** own flights, school, tennis, banking pays, Amazon, stays, medical portal, or ProHealth supplement work when a specialist exists.

## Route by ask

| Ask | Owner |
|---|---|
| Flights (Alaska/SW/Delta/Chase compare), SEA↔SJC / Santa Clara calendar | **Flight Booking** |
| Julie @ Cherry Crest Elementary (calendar, portal, PTSA, childcare) | **Cherry Crest - Julie's Cool** |
| EFGS / Bertschi French Saturdays / out-of-WA class conflicts | **EFGS** |
| Gorin / CourtReserve Bellevue tennis | **Gorin Tennis Booking** (never Bellevue Club) |
| Bellevue Club / ITC / Club youth | **Bellevue Cub** (never Gorin/EFGS/Cherry Crest) |
| Chase pay, Zelle, Ultimate Rewards / points, Chase Travel UR | **Chase** |
| Venmo payments / settle / transfer | **Venmo** (separate from Chase) |
| Bank of America / Preferred Rewards | **BoA** |
| Charles Schwab brokerage/banking | **Charles Schwab** |
| Vanguard investing / brokerage / inbound ACATS (incl. Schwab→Vanguard share moves) | **Vanguard** |
| Amazon shop / reorder / track / account | **Amazon** (prefer live preferred id; ignore stale duplicate Amazon if present) |
| ProHealth (prohealth.com) sign-in and supplement orders | **ProHealth** |
| Airbnb **guest** stays | **Airbnb** |
| Home Exchange verify / GuestPoints guest stays / host outreach / HE host-side guest threads, cancellations, double-booking follow-ups | **Home Exchange Verification** (fare research in-chat; do not ping Flight Booking for prices) |
| Vietnam spring-break 2027 multi-family plan | **April Vacation** |
| MyChart / Overlake medical portal | **MyChart - Medical** |
| Dropbox find / organize / share | **Dropbox** |
| Global Entry / KTN / Trusted Traveler | **Global Entry** (confirm if profile still thin) |
| American Family Insurance / AmFam policies, bills, claims | **American Family Insurance** |
| CLI / AWS / logs / code / Pine–Hospitable–pricing–kumo skills, HE↔Airbnb sync code | **Grok CLI** (box CLI only; never desktop/Chrome cleanup) |

## No dedicated bot

CleaningButton / Pine host ops → **Grok CLI** + skills `hospitable`, `home-exchange`, `pricing`, `kumo`, `aws-account`, `r2-memory`, `guest-messaging-harness`. Skill `r2` is retired; use `r2-memory`.

## Hard rules

1. **Prefer specialist** over managed generic commerce/travel skills when a teammate owns the domain.
2. **Chase:** all Chase pay, Zelle, UR, and Chase Travel → **Chase** (merged; former CutyChase - Pay Balance is deprecated). **Venmo** is a separate bot — do not route Venmo asks to Chase.
3. **Daily Chrome cleanup fan-out:** message desktop bots with priority true; **skip** Chief (self), Grok CLI, obsolete **New Bot**, and deprecated **CutyChase - Pay Balance** until deleted. **Include** **Chase**, **Charles Schwab**, **Vanguard**, **American Family Insurance**, and **ProHealth** in fan-out. Stay silent on FYI “already clean” replies (no ack tools).
4. **Amazon:** use the live preferred Amazon id from the teammates list; do not fan out to empty/stale Amazon duplicates.
5. **Secrets (Jerome standing rule, 2026-10-06):** every site login and password Jerome stores for bots lives in AWS SSM SecureString in us-east-1 (IAM `grok-bot-titan`). Fetch at use only. Never ask him to paste a password in chat. Never write secret values to disk, git, chat, memory, Titan, screenshots, or skill files. Name the SSM paths in skills (e.g. `/chase/username`, `/prohealth/password`); never the values. If a path is missing, say which path and stop.
6. **Cross-cutting:** Titan retrieve→append and `always-push` stay aligned across specialists; secrets from SSM only.
7. **Fan-out:** only when Jerome asked or a standing routine requires it; otherwise propose first.
8. After new ownership learnings: update this skill, append Titan if used, commit+push `localGrokSkills` per `always-push`.

## Verify-before-done (lesson from the 2026-10-15 HE↔Airbnb double bookings)

Any automation that touches guests, bookings, calendars, door access, or money is NOT done just because it exists or a teammate says it shipped. Before calling it done, and when auditing existing setups:

1. **Prove it end to end.** Check the real outcome on every platform involved (for example, the dates are actually blocked on both Airbnb and HomeExchange), not just that the code ran.
2. **Every direction.** For any sync between two systems, confirm both directions exist. A one-way sync is a known gap; flag it.
3. **No silent failures.** Every skipped, partial, or failed action must alarm. If the status is uncertain, fail closed (block on both platforms, hold the send).
4. **Independent cross-check.** Keep a separate scheduled audit that compares the source systems directly (Grok Bot runs one daily at 8:17am PT; Grok CLI runs one hourly) and alarms on overlaps, partial blocks, and missed sync runs.
5. **Guest-facing gate.** Never send door codes or check-in instructions to a guest whose stay overlaps another booking. Hold the send and alert Jerome.
6. **Ask for proof from teammates:** commits, test output, and live readback, not just "deployed".
7. **Permissions:** confirm each alarm and notification path actually has permission to deliver (for example, SNS Publish on the Lambda role) by sending a test alert.

## Ambiguous splits (resolve before routing)

- Family Hawaii / travel: HE guest stay vs flight ticket vs Cherry Crest school calendar — split across HE Verification, Flight Booking, Cherry Crest as needed.
- April 2027 dates: April Vacation vs Cherry Crest calendar for school.
- “Chase” alone: route to **Chase** (pay + rewards merged). Venmo stays separate.

## Related skills

`always-push`, `r2-memory`, `routines`, `scheduling`, `send-on-behalf`, `skill-authoring`, plus each specialist’s domain skill (`flight-booking`, `cutychase-pay-balance`, `cutychase-rewards`, `amazon`, `venmo`, `prohealth`, etc.). Playbooks `cutychase-pay-balance` and `cutychase-rewards` both remain; both are owned by **Chase**.

## AWS routing rule (2026-10-17)
- Anything involving AWS (Lambdas, CloudWatch alarms, SSM, AWS-backed automations such as Bellevue Club court booking) goes to Grok CLI (eed2c114-9ba2-42a9-83ec-8c48da246425). Other bots must not do AWS work themselves.
