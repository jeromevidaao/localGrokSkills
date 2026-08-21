---
name: kumo
description: >
  KumoCloud mini-split AC for CleaningButton Pine units — status and control.
  Use when the user asks if AC is running, or to set temp / turn on-off / cool-heat.
  Prefer /r2 which executes via R2Lambda (same path as dashboard Set climate).
---

# KumoCloud AC (CleaningButton)

## Capabilities

| Action | How |
|--------|-----|
| **Read** status (on/off, mode, set/room °C) | R2 loads live zones |
| **Set** power / mode / temperature | R2 executes Kumo commands (power-cycle when needed) |

## Units

| Unit | Rooms |
|------|--------|
| Pine Apt #1B | Bedroom, Kitchen |
| Pine Apt #2 | Living, Bedroom, Small BR |
| Pine Apt #3 | Living, Bedroom, Small BR |

Temps: **16–28°C**. Modes: **cool**, **heat**. Fan speed always auto.

## Examples for R2

```text
Do we have any AC currently running?
Set unit 2 bedroom to 20 cool
Turn off AC in apt 3
Set all AC in unit 2 to 18 degrees
Turn on heat in 1B kitchen 21
```

```bash
python3 ~/.grok/skills/r2/scripts/r2_chat.py "Set unit 2 bedroom to 20 cool"
```

## Implementation

- R2Lambda `lib/kumo.js` — status + `parseClimateCommand` + `applyClimateCommand`
- SSM: `/kumocloud/email`, `/kumocloud/password`
- Same reliability path as API `act=set_climate` (power-cycle when already on)
- **Live room temp:** `GET /v3/devices/{serial}` — **not** `/v3/sites/{id}/zones` (that list caches stale `adapter.roomTemp`; 1B sat at 25.5°C for days while the device endpoint was ~20°C, matching a Nest at 21.6°C). Overlay device onto zone adapters.
- Hourly snapshots: Dynamo `climateTempSamples` (HeatPump + dashboard attach). Graph API `act=climate_temp_series`.

## Safety

- Only known Pine device serials are controlled.
- Prefer naming unit (and room when not “all”).
- Status-only questions never send commands.
