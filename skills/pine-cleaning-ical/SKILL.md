---
name: pine-cleaning-ical
description: >
  Pine cleaning-team iCal feeds (Airbnb + HomeExchange) for Apt #1B / #2 / #3.
  Lambda pineCleaningIcal hourly EventBridge; public cleaningbutton.com/calendar
  URLs; Karen Trask calendar-link updates. Use when the user asks about Pine
  cleaning calendars, .ics links for cleaners, HE Reserved on the cleaning
  calendar, pineCleaningIcal, or /pine-cleaning-ical.
---

# Pine cleaning iCal

Repo: `jeromevidaao/pine-cleaning-ical` (`~/pine-cleaning-ical` / `/workspace/pine-cleaning-ical`).  
Lambda: **`pineCleaningIcal`** (`us-east-1`, nodejs22.x).  
Schedule: EventBridge **`pineCleaningIcal-hourly`** (`rate(1 hour)`).

Publishes Airbnb-format iCal plus HE BOOKED (and pre-approved/finalized inbox) as extra `SUMMARY:Reserved` VEVENTs so the cleaning team sees HE turnovers.

## Public URLs (one per apt)

| Unit | URL |
|---|---|
| Apt #3 | https://www.cleaningbutton.com/calendar/pine-apt-3.ics |
| Apt #2 | https://www.cleaningbutton.com/calendar/pine-apt-2.ics |
| Apt #1B | https://www.cleaningbutton.com/calendar/pine-apt-1b.ics |

Also written to `s3://cleansite/calendar/pine-apt-*.ics` and `s3://planning-calendar/pine-apt-*.ics`.

## Format

- Same Airbnb hosting iCal shape (`PRODID:-//Airbnb Inc//Hosting Calendar 1.0//EN`).
- HE stays → extra Reserved VEVENTs: `UID:he-{conversationId}-{YYYYMMDD}@cleaningbutton.com`, `DESCRIPTION:HomeExchange reservation (Guest Name)`.
- Skip HE `RESERVED` / `UNAVAILABLE` / `NON_RECIPROCAL`, requested (`status=0`), cancelled (`status=5`).

## Cleaner calendar-link updates

| | |
|---|---|
| **To** | Karen Trask — `cleanforme207@gmail.com` (also seen `karen@cleanforme207.com`) |
| **Cc** | Usually `ngoc.h.dinh@gmail.com` |
| **Send** | Draft only — Jerome reviews/sends |

When updating links for cleaners: draft the three URLs above, ask them to replace old Airbnb-only subscriptions. Do not send without Jerome’s approval.

## Verify

```bash
for u in pine-apt-3 pine-apt-2 pine-apt-1b; do
  curl -sS -o /tmp/$u.ics -w "$u %{http_code}\n" \
    "https://www.cleaningbutton.com/calendar/$u.ics"
  head -5 /tmp/$u.ics   # BEGIN:VCALENDAR
  rg -n "UID:he-|DESCRIPTION:HomeExchange" /tmp/$u.ics || true
done
aws logs filter-log-events --log-group-name /aws/lambda/pineCleaningIcal \
  --start-time $(($(date +%s)*1000 - 7200000)) \
  --filter-pattern '"pineCleaningIcal ok"' --limit 5
```

Expect HTTP **200**, `VCALENDAR`, HE `DESCRIPTION`/`UID` when HE stays exist, Lambda log **`pineCleaningIcal ok`**.

## Deploy

Push `main` on `jeromevidaao/pine-cleaning-ical` (always-push). Do not update the Lambda from the AWS console.

## Related

- Skill `home-exchange` (HE calendar / BOOKED)
- Skill `hospitable` (Airbnb occupancy)
- Skill `always-push`
