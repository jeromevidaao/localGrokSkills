---
name: family-travel
description: >
  Jerome/Ruby family vacation planning: Cherry Crest (Bellevue BSD405) school
  calendar, SEA–HNL nonstop flights, HomeExchange dest search for 2 adults +
  6-year-old. Use when school break, Christmas vacation, Oahu/Hawaii trip,
  Cherry Crest calendar, or SEA-HNL.
---

# Family travel

Load **`home-exchange`** for any HE search or host contact. This file is dates, party, and flights only.

## Party

| | |
|---|---|
| Travelers | Jerome, Ruby, daughter (6) → HE search **`--adults 2 --children 1`** |
| HE account | Ruby Dinh, user **`5703979`**. Sign outbound messages as Ruby. |
| Outreach | `GET /v1/users/me` `verified_status` must be **`1`**. `-1` = still on verification — do not `request-stay`. |

No 3-bedroom minimum for this party. (Manhattan 5 people / 3 kids is the 3BR stay — see home-exchange.)

## Cherry Crest / BSD405 (not Bellevue NE)

**Canonical school calendar** now lives in skill **`cherry-crest`**
(`skills/cherry-crest/SKILL.md`, Cherry Crest - Julie's Cool bot). Prefer that
file (or the live BSD405 PDF) over duplicating dates here. Snapshot below kept
for quick Hawaii trip planning.


Official [BSD405 2026–27 staff calendar](https://resources.finalsite.net/images/v1770322933/bsd405org/bsd405org/kdzrn6mn0roqufznmld0/2026-2027-Staff-District-Calendar.pdf):

| | |
|---|---|
| Winter / Christmas | **21 Dec 2026 → 1 Jan 2027** |
| Last school day | Fri **18 Dec 2026** |
| School resumes | Mon **4 Jan 2027** |
| Off window for a trip | Sat 19 Dec through Sun 3 Jan |

A 5–7 night Oahu trip must fit that window. Checkout 3 Jan is the last morning before school.

## SEA → HNL nonstop

Alaska (~5–6/day) and Delta (~2/day), ~6h15. Kayak result cards **do not server-render prices** — quote live Google Flights nonstop (same carriers) and give Kayak links:

`https://www.kayak.com/flights/SEA-HNL/{from}/{to}/2adults/1children?sort=price_a&fs=stops=0`

NYE return is the expensive leg. Sample 2026-08-28 (2 adults + 1 child, nonstop):

| Window | Family total | Carrier |
|---|---|---|
| 28 Dec → 3 Jan (6n) | ~$3,302 | Delta cheapest |
| 21 Dec → 28 Dec (7n) | ~$3,505 | Alaska |

Re-price live; do not reuse these dollars as fact.

## HE dest search (this party)

```bash
S=~/.grok/skills/home-exchange/scripts/he_api.py
python3 $S search --place oahu --from YYYY-MM-DD --to YYYY-MM-DD --adults 2 --children 1
```

GuestPoints + response-rate + calendar verify (home-exchange defaults). Listing links: `https://www.homeexchange.com/homes/view/{id}`. Last Oahu snapshot (28 Dec 2026–3 Jan 2027) lives in **home-exchange** “Current dest search (2026-08-28)”.
