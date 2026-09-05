---
name: home-exchange-verification
description: >
  Use this whenever the Home Exchange Verification agent works for Jerome:
  HE identity/address verification, Zendesk ticket watch, GuestPoints dest
  search and host outreach, finalize/retract stays, calendar invites, or
  family SEA–HNL flight research in this chat. Read at the start of every
  Jerome conversation; update + push after anything new.
---

# Home Exchange Verification (Jerome Ansia)

Standing playbook for the **Home Exchange Verification** Grok Bot. Read this
file first whenever Jerome messages this agent. After the conversation,
**update this skill** with anything new, then **commit + push immediately**
(always-push — never ask).

Repo: `jeromevidaao/localGrokSkills` — path
`skills/home-exchange-verification/SKILL.md`.
On the box: `/workspace/localGrokSkills` (`~/.grok/skills` → `skills/`).

For HE **API** / Pine host ops / `he_api.py`, also load skill **`home-exchange`**.
For **booking** flights (Alaska login, payment), defer to **Flight Booking** /
skill **`flight-booking`** — Jerome told this agent **not** to ping the Alaska /
Flight Booking bot for price research; search Google Flights / Hopper **here**.

## Hard rules

1. **Read this skill first** on every Jerome turn; **update + push** when done.
2. **GuestPoints only** unless he explicitly asks reciprocal. Named greetings
   (`Hi {HostFirstName} -`) on every outbound host message.
3. **Never type passwords.** Hand the box for HE / Google / Drive sign-in.
4. **Do not reply on Dan thread** `95774893` after Jerome said FaceTime is done
   (2026-09-03) unless he asks again.
5. **Do not ping** the Flight Booking / Alaska Airlines agent for fare lookups.
6. Passport / bills: never OCR, quote, or log PII from ID docs.
7. Finalize / Venmo / off-platform fees: only when Jerome explicitly authorizes.

## Account / people

| | |
|---|---|
| HE profile | **Ngoc Hong Dinh** (also Ruby); user **`5703979`** |
| Address | **53 Pine Street, Portland, ME 04102** |
| Sign messages | Ruby & Jerome |
| Jerome email | jerome.ans@gmail.com |
| Wife | Ngoc / Ruby — **ngoc.h.dinh@gmail.com** |
| Child | Daughter, **7** (as of 2026) → flights **2 adults + 1 child** |
| HE GP balance | **910 GP** after Dan stay (−2600 on 2026-09-03; was 3510) |

Verification (2026-09-02): **verified**. Ticket `#4709123` solved (“You are now a verified member!”). Profile name must match ID (**Ngoc Hong** + **Dinh**).

## Pine listings (host side)

| Home id | Title | Notes |
|---|---|---|
| **3202475** | Cozy West End Victorian \| EV Charging + Parking | Primary watch listing |
| 3285044 | (second Pine) | |
| 3285159 | (third Pine) | |

Capacity on 3202475: **6 adults · 1 baby**, 2 BR / 1 BA.

## Winter 2026 Hawaii stay (locked)

| | |
|---|---|
| Exchange | **#128015169** Finalized |
| Host | **Dan Cronin** (+ wife **Renée**) — L-C Hale |
| Listing | [2788923](https://www.homeexchange.com/homes/view/2788923) |
| Thread | https://www.homeexchange.com/conversations/95774893 |
| Dates | **Dec 21 → Dec 31, 2026** (10 nights) |
| Guests | **5** (HE request; flights often 2ADT+1CHD) |
| Cost | **260 GP/night · −2600 GP** |
| Address | **333 Aoloa Street, Kailua, HI, USA** |
| Cleaning | Off-platform **Venmo** OK (Jerome agreed) |
| Calendar | Event *HomeExchange: L-C Hale, Kailua (Dan)* all-day Dec 21–31 Hawaii time; Ngoc invited. eid `ht4pvgju3nma3mvpv667iskb10` |

Dan wanted **10+ days**; window fits Cherry Crest / BSD405 winter break **Dec 21 2026 – Jan 1 2027**. NVIDIA free days Dec 23–25; Amazon typically Dec 25 + Jan 1.

FaceTime: Renée offered **Tue Sep 8 2026**, 8:30am–12:30pm Hawaii (**11:30am–3:30pm PT**), ~10 min. Jerome later said **do not reply further** on that thread.

## Outreach batch (Dec 24–31 then superseded)

Sent GP requests then **withdrew** (message only — HE has no guest cancel UI on pending Request-sent) after Dan finalized:

| Host | Conv | Outcome |
|---|---|---|
| Jen / Kailua Oasis 2778013 | 95774853 | Declined |
| Vina 2087763 | 95774937 | Declined |
| Dan 2788923 | 95774893 | **Finalized** |
| Cheryl / Ocean Pointe 3040653 | 95775011 | Withdrawn |
| Christine 2886917 | 95791760 | Withdrawn |
| Erik & Darlene 2486429 | 95791862 | Withdrawn |
| Steven 2823176 | 95792226 | Withdrawn |
| Marie 969774 | 95798466 | Withdrawn |
| Renuka 548002 | 95799315 | Withdrawn |
| Christina 468848 | 95799446 | Withdrawn |
| Janet (Big Island) | 95744360 | Withdrawn |

Skipped: Steph (reciprocal / GP disabled), Sara (Dec 24 unavailable), Levida reciprocal-only, Satya (no kids under 12).

## Flight research (this agent)

Party for quotes: **2 adults + 1 child (7)**. Prefer **nonstop**, **no red-eye**. Earlier SEA outbound preferred when asked; daytime return OK.

Selected option emailed to Ngoc (2026-09-03, **not booked**):

- Out Mon Dec 21: Alaska/Hawaiian **SEA 6:20 PM → HNL 10:49 PM**
- Back Thu Dec 31: **HNL 8:30 AM → SEA 4:17 PM** (daytime)
- Total ~**$3,072** for 3

Pending research (interrupted): return via **SFO** — all 3 HNL→SFO Dec 31; Jerome stays SF; **1 adult + child SFO→SEA Sunday Jan 3**; check **Hopper** + long layovers OK.

## Routines

| Folder | Schedule | Purpose |
|---|---|---|
| `homeexchange-listing-3202475-replies` | `20 8-19 * * 1-5` | Hourly weekday HE inbox watch; silent if no change; chat + email jerome.ans@gmail.com on new inbound |

After Dan finalized + withdrawals, keep the watch quiet unless a host replies on a withdrawn thread or Dan/Renée writes (and Jerome re-authorizes replies).

## Verification playbook (if needed again)

1. Bills from Drive (CMP + heating) → Zendesk if upload locked.
2. Profile name/address must match docs (**Ngoc Hong Dinh**, 53 Pine St).
3. Passport ID if asked; greet support clearly.
4. Hourly ticket watch until solved; delete routine when verified.
5. Email Jerome (and Ngoc if asked) on status changes.

## Dest search / outreach playbook

1. Prefer skill **`home-exchange`** `he_api.py search` when API works; else browser.
2. GP / non-reciprocal; calendar-verify Dec window; skip long min-nights unless he says flex.
3. Table: listing id link `/homes/view/{id}`, location, BR/baths/beds/sleeps, availability, view.
4. Contact only when he asks; copy prior Ruby message; **Hi {Name} -**.
5. Watch replies; on “found lodging”, polite withdraw to all other open threads (no cancel button).

## Calendar / email

- Google Calendar MCP: create all-day stay blocks; invite **ngoc.h.dinh@gmail.com**.
- Gmail MCP: status emails to Jerome and Ngoc when asked.

## Standing: skill hygiene

After every Jerome conversation that changes process or trip state: edit this
`SKILL.md`, `git add`, commit, **public → push main → CI green → private**
(always-push). Do not leave skill edits only on disk.
