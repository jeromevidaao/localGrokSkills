#!/usr/bin/env python3
"""Print performance vs occupancy goals from the weekly S3 report.

Preferred source for "how are we doing with the goals?" — not DDB, not a
raw Hospitable pull unless the host wants fresher detail.

Usage:
  python3 occupancy_vs_goals.py
  python3 occupancy_vs_goals.py --json
  python3 occupancy_vs_goals.py --url https://www.cleaningbutton.com/data/occupancy/latest.json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

DEFAULT_URL = "https://www.cleaningbutton.com/data/occupancy/latest.json"


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "pricing-skill-occupancy"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--json", action="store_true", help="raw JSON dump of summary + meta.season")
    args = ap.parse_args()

    data = fetch(args.url)
    meta = data.get("meta") or {}
    season = meta.get("season") or {}
    units = data.get("summary") or []

    if args.json:
        print(
            json.dumps(
                {
                    "generatedAt": data.get("generatedAt"),
                    "asOfDate": meta.get("asOfDate"),
                    "season": season,
                    "monthlyTargets": meta.get("monthlyTargets"),
                    "summary": units,
                },
                indent=2,
            )
        )
        return 0

    as_of = meta.get("asOfDate") or str(data.get("generatedAt") or "")[:10]
    tlo = season.get("targetLow")
    thi = season.get("targetHigh")
    band = (
        f"{int(round(float(tlo) * 100))}–{int(round(float(thi) * 100))}%"
        if tlo is not None and thi is not None
        else "n/a"
    )
    print(f"Weekly occupancy report — as of {as_of}")
    print(f"Source: {args.url}")
    print(
        f"Season (trailing): {season.get('label') or season.get('key') or 'n/a'} · target {band}"
    )
    if meta.get("startDate") and meta.get("endDate"):
        print(f"Trailing window: {meta['startDate']} → {meta['endDate']}")
    if meta.get("forwardStart") and meta.get("forwardEnd"):
        print(f"Forward window: {meta['forwardStart']} → {meta['forwardEnd']}")
    print()
    print("Units vs goals:")
    for u in units:
        name = u.get("unit") or u.get("name") or "?"
        print(
            f"  - {name}: trail {u.get('trailing30')} / fwd {u.get('forward30')} "
            f"· goal {u.get('target') or band} · level {u.get('level')}"
            + (f" — {u.get('headline')}" if u.get("headline") else "")
        )
        if u.get("topAction"):
            print(f"      top action: {u['topAction']}")
    monthly = meta.get("monthlyTargets") or []
    if monthly:
        print()
        print("Upcoming monthly goals:")
        for m in monthly[:6]:
            cur = " (current)" if m.get("isCurrent") else ""
            lo = m.get("targetLowPct")
            hi = m.get("targetHighPct")
            b = f"{lo}–{hi}%" if lo is not None and hi is not None else m.get("goalText") or ""
            print(f"  - {m.get('monthName') or m.get('monthKey')}: {b}{cur}")
    print()
    print(
        "Goals definition: SEASON_BANDS in jeromevidaao/pricing-tool/report.js (code, not DDB)."
    )
    print(
        "Escalate to Hospitable only if host wants live/fresher than this weekly snapshot."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)
