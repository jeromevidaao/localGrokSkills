---
name: dropbox-directory-map
description: >
  Living map and browsing procedure for a personal Dropbox. Use when locating
  folders, deciding where a Dropbox document belongs, or refreshing the known
  directory tree; verify the live Dropbox because this map is not exhaustive.
---

# Dropbox directory map

This is a personal, living directory map. It records directory paths and safe
browsing/search procedures—not document contents. Treat the live Dropbox as the
source of truth and do not infer folders that are not listed here.

## Known map

Last verified: **2026-09-19** from the personal Dropbox web UI.

### Confirmed top-level folders

- `/0 ID/`
- `/1 Real Estate/`
- `/02 Taxes/`
- `/3 Employment/`
- `/03 Medical/`
- `/4 Immigration/`
- `/6 School/`
- `/7 Postcard/`
- `/08 Credit Card Picture/`
- `/10 Car/`
- `/Archive/`
- `/Picture/`

### Confirmed nested path

- `/0 ID/global entry/`

This nested folder is shared with another Dropbox user. Keep this map at the
folder-path level; do not copy identity-document filenames, numbers, dates, or
other document contents into the skill.

### Suggested or recently surfaced locations

These appeared in Dropbox suggestions/recents but were not independently
confirmed as current top-level folders in the map above:

- `2026`
- `08 Credit Card Picture`
- `chase card image folder`

Do not promote a suggested/recents label into the confirmed map until it is
verified by browsing the personal Dropbox root.

## How to browse and search

1. Open the personal Dropbox root at `https://www.dropbox.com/home` and verify
   that the account/context is **personal**, not work/team Dropbox.
2. Browse the root and use breadcrumbs to record exact folder paths. Preserve
   spelling, capitalization, spaces, and numeric prefixes.
3. For search, use Dropbox personal search (not the work search route):
   `https://www.dropbox.com/search/personal?query=<URL-encoded terms>`
4. Search distinctive folder words first, then open the result and read its
   breadcrumb. Prefer recording the containing folder path over recording
   filenames.
5. If the Dropbox MCP/connector is unavailable, use the browser procedure
   above. The known failure mode is that the official connector may report
   “Dynamic client registration is not supported”; do not invent API results.
6. If a folder is not visible at the root, use personal search and confirm the
   breadcrumb before adding it. Treat suggestions and recents as leads only.

## Maintenance rules

- Update this map whenever a new top-level folder is found or an existing path
  is renamed, moved, or deleted.
- Record the verification date and source for each refresh.
- Add only paths observed in the live personal Dropbox; do not guess categories
  or extrapolate from filenames.
- Keep the skill generic enough to reuse as a template, while retaining the
  known paths above for this personal map.
- Never put secrets, access tokens, account numbers, TSA/KTN numbers, or full
  legal names in this file.
