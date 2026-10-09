---
name: dropbox-file-index
description: >-
  Full file index of Jerome's personal Dropbox (paths, types, modified dates)
  as of 2026-10-08. Use to find a Dropbox file fast before browsing; grep
  index.tsv, then verify live.
---
# Dropbox file index

A file-level snapshot of Jerome's **personal** Dropbox: every folder and file path
seen in a browser crawl, with type, last-modified date, and size. It complements
the folder-level skill `dropbox-directory-map` (browse/search procedure, folder map).

- **Last crawl:** 2026-10-08 (personal Dropbox web UI, folder by folder).
- **Counts:** 1,726 entries: **293 folders** and **1,433 files**.
- **Files in this skill folder:**
  - `index.tsv`: machine-readable, header `path<TAB>type<TAB>modified<TAB>size`,
    sorted by path. `type` is `file` or `folder`. `modified` is `YYYY-MM-DD HH:MM`
    (PT), `YYYY-MM-DD`, or `YYYY-MM` when Dropbox showed only a month; blank when
    not shown (folders never show one). `size` is blank for most folders; a leading
    `>` means Dropbox showed a lower bound.
  - `index.md`: the same data, grouped by top-level folder, each folder followed by its files.

The snapshot gets stale. Always confirm in the live Dropbox before you tell anyone a file exists or act on it.

## Look something up

1. Grep the index (in the skill folder, or `skills/dropbox-file-index/` in the
   `localGrokSkills` repo):
   ```bash
   rg -i 'paystub|w-?2' index.tsv
   rg -i '^/02 Taxes/Taxes/2023/' index.tsv
   awk -F'\t' '$2=="file" && $3 ~ /^2026-10/' index.tsv   # modified Oct 2026
   ```
2. Take the containing folder path and open it live in the browser:
   `https://www.dropbox.com/home/<URL-encoded folder path>`
   (for example `/3 Employment/Amazon` becomes `https://www.dropbox.com/home/3%20Employment/Amazon`).
   Use `python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' '/3 Employment/Amazon'`.
3. If it isn't there (moved or renamed), use personal search:
   `https://www.dropbox.com/search/personal?query=<URL-encoded terms>`.
   Make sure you're in the **personal** account, not work or team.
4. Masked names: a few filenames had long account or ID numbers, and those numbers are
   masked in the index (only the last 4 digits kept, e.g. `BE**********2740`). To find
   one, browse its folder or search the last 4 digits. Don't paste the real number
   anywhere.

## Quick lookup (top-level folders)

| Folder | Holds | Subfolders / files |
|---|---|---|
| `/0 ID/` | Identity docs: passports, driver licenses, birth/marriage certs, green card, naturalization, SSN cards, Global Entry, visas, immunization (CIS), profile photos | 16 / 63 |
| `/02 Taxes/` | `Taxes/<year>` (2012–2025): returns, W-2s, 1099s, receipts; also `Will  - PoA` | 49 / 300 |
| `/03 Medical/` | Medical, dental, eyecare, and insurance docs by year (2015–2026) | 9 / 24 |
| `/08 Credit Card Picture/` | Card photos (Amex, Chase Ink for Pineland LLC, Chase Unlimited) | 3 / 8 |
| `/1 Real Estate/` | Bellevue (2023 mortgage approval); New York City (purchase, mortgage, lease, tax, renovation, sale); Portland (AirBnb tax-deduction receipts by month, Pineland LLC, insurance, property taxes, mortgage); Seattle (234 27th Ave, Colpin Wells, To Sell) | 74 / 570 |
| `/10 Car/` | Car insurance (Model X, Costco), WA license-tab payment | 1 / 2 |
| `/3 Employment/` | Amazon (offer, severance, termination letter, last paycheck), Nvidia (offer, I-9, latest paycheck, Fidelity ROE packet), resumes, 2026 WA unemployment | 6 / 14 |
| `/4 Immigration/` | Ruby green card, H1B, I-20 packets | 5 / 243 |
| `/6 School/` | Jerome (IESN diploma and transcripts), Julie (Cherry Crest 2025–26 report card) | 4 / 9 |
| `/7 Postcard/` | Postcards 2013, 2014, 2019 | 3 / 13 |
| `/Archive/` | Old material: Carrito Bleau, ebooks, accent class, Bank (Belgium/USA statements), Camera Uploads, old immigration, leases, paystubs (2014+), Personal Projects, Ruby green card | 99 / 173 |
| `/Picture/` | Trip photos (Maine, Peru, Vietnam & Bangkok, Maui), Julie school, daycare, and passport pictures | 12 / 14 |

The counts are the entries under each folder in `index.tsv` (the folder itself not included).

## Coverage gaps (2026-10-08 crawl)

- **Photo folders summarized** (only about the first 30 rows recorded): `/Archive/Camera Uploads`,
  `/Picture/2016 - Peru`, `/Picture/2016 - peru for llbean`, `/Picture/2015 - maine trips`,
  `/Picture/2016 - Vietnam & Bangkok`, `/Picture/for facebook`, `/Picture/Peru Liem's Photos (1)`,
  `/Picture/2022 - Maui`.
- **Old code and coursework under `/Archive/` summarized**, not listed file by file.
- `/Picture/2022` looked empty.
- `/02 Taxes/Will  - PoA` (the real name has two spaces): listing unreliable.
- `/1 Real Estate/Portland/AirBnb - Tax Deduction/2017/08 - August`: possibly incomplete.
- Crawl crashed in `/Archive/02 Carrito Bleau/state farm/2015` and parts of
  `/Archive/Bank/Belgium/Extrait/...`.
- Not visited: `/Archive/Personal Projects/CHHS-Prototype`, `/Archive/accent class/:ah:`.
- Partial: `/Archive/Bank/Usa/Chase`, `/Archive/paystub/2017/llbean`.

For anything in these folders, browse live instead of trusting the index.

## Refresh the index

The Dropbox MCP connector fails with "Dynamic client registration is not supported",
so re-crawl through the **browser**:

1. Open `https://www.dropbox.com/home` (personal account) and walk each folder in list view.
   For each row, record `name`, `type` (file/folder), `modified`, `size`.
2. Write rows as `<full path>\t<type>\t<modified>\t<size>`. Then dedupe by path, normalize
   (collapse `//`, strip trailing `/`, NFC), drop UI noise or empty names, add any missing
   ancestor folders, and convert dates to `YYYY-MM-DD[ HH:MM]`.
3. Mask any long account or ID number in a filename (keep the last 4 digits).
4. Regenerate `index.tsv` and `index.md`, update the date, counts, and coverage gaps here, then
   commit and push `localGrokSkills` (the repo stays **private**).
5. For huge photo folders, record the first page and list the folder under Coverage gaps.

## Rules

- Filenames are in scope: Jerome approved a full file index (2026-10-08). Document
  **contents** are not. Never put secrets, passwords, account numbers, KTN or passport
  numbers, or SSNs in this skill's prose or index.
- Masked in this snapshot (last 4 kept): Belgian bank IBAN-like strings in
  `/Archive/Bank/Belgium/Extrait/...` (folder and file names), one visa application
  number in `/0 ID/Visa/...`, one IRS record-of-account number in `/02 Taxes/Taxes/2013/...`,
  and one insurance policy number in `/03 Medical/2021/...`. Masked paths won't match
  the live Dropbox character for character.
- Keep `localGrokSkills` private. Never flip it public to push this index.
