---
name: bellevue-court-arms
description: >
  Arm a future Bellevue Club indoor court through Lambda bellevueClubTennis,
  and manage those one-off runs (list, create, update, delete) on the
  cleaningbutton website and Android Tennis / Swim page. Use when Jerome asks
  to book a court in advance, arm a slot, change a targeted run, or show when
  a future indoor booking will fire. Not for Gorin, outdoor courts, or the
  standing Sunday 6:00 PM / Saturday 10:30 schedules.
---

# Bellevue court arms

One-off indoor courts. Standing Sunday 6:00 PM (`sunday-1800`) and Saturday 10:30 (`saturday-745`) stay on their own schedules. Do not edit those from this flow. Club login, Cloudflare, and the 7:45 refresh rules live in **bellevue-cub**.

## Window

Jerome names the **court date and start**. The create/edit form on Tennis / Swim uses a date picker and the indoor slot list (not a typed time). Work backward:

1. Inventory opens **7 days earlier, same weekday, 7:45:00 a.m. PT**.
2. The schedule fires that morning at **7:40 a.m. PT**. The Lambda logs in, waits until 7:45:00, then races ITC 1–6.
3. End is start **+ 75 minutes**. Indoor only. If that start is gone, do not book a different time.

Example: Wed Oct 14 2026 6:00 PM → fire **Wed Oct 7 2026 7:40 a.m. PT**, book **6:00–7:15 PM**.

Indoor starts are 75 minutes, back to back. The form only offers these:

- Weekday: 5:30 AM through 8:30 PM (last slot ends 9:45 PM)
- Saturday: 6:45 AM through 8:30 PM
- Sunday: 6:45 AM through 7:15 PM

`normalizeArmInput` rejects any other start. The list is also `advanceArms.slotCatalog` on `tennis_ops_status`.

A custom run time is allowed. The booker waits for 7:45 only when the run is 7:40. Any other clock attempts as soon as the invoke starts.

## Arm it

From a machine that can write EventBridge Scheduler (Jerome’s Mac, not the Titan user):

```bash
node ~/cleaningbutton-api/scripts/arm-court.js --court 2026-10-14 --start "06:00 PM"
node ~/cleaningbutton-api/scripts/arm-court.js --delete 20261014-1800
```

Optional `--run 2026-10-07T07:40` and `--id`. Blank run time means 7:40 on the open morning.

The same write path is `act=tennis_arm_upsert` / `act=tennis_arm_delete` (owner JWT). List is `bellevue.advanceArms` on `act=tennis_ops_status`.

Schedule name: `bellevueClubTennis-arm-<id>`. Input: `targetYmd`, `targetStart`, `targetWeekday`, `oneOff: true`. Expression: `at(YYYY-MM-DDTHH:mm:ss)` in `America/Los_Angeles`. `ActionAfterCompletion=DELETE`. Retries 0.

`bash ~/cleaningbutton-api/scripts/ensure-tennis-arm-iam.sh` attaches managed policy `TennisArmScheduler` to `apiRole` (inline policies are full) and the Lambda permission for `bellevueClubTennis-arm-*`. Run it if the phone or site reports scheduler access denied.

## Where Jerome sees it

Tennis / Swim → **Advance books**, on cleaningbutton.com `#!/tennis-ops` and Android R2 (OTA). Each row shows **run time** and **court date/time**. Create, edit, and delete work on both. After a save, refresh that page and confirm the row.

Verify the live schedule:

```bash
aws scheduler get-schedule --name bellevueClubTennis-arm-<id> --region us-east-1
```

Do not claim it is armed until that schedule exists and the Tennis / Swim row matches it.

## After a change

Update this skill if the schedule contract or the screen changes, then commit and push `localGrokSkills`. Append the turn to Titan. Leave standing Sunday/Saturday schedules alone.
