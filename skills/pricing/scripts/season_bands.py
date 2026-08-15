#!/usr/bin/env python3
"""Print SEASON_BANDS occupancy goals from local pricing-tool or GitHub.

Usage:
  python3 season_bands.py
  python3 season_bands.py --month 9
  python3 season_bands.py --github   # requires gh auth or GITHUB_TOKEN
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

LOCAL = Path.home() / "pricing-tool" / "report.js"
REPO = "jeromevidaao/pricing-tool"
PATH = "report.js"


def extract_season_bands(src: str) -> str:
    m = re.search(r"const\s+SEASON_BANDS\s*=\s*\{", src)
    if not m:
        raise SystemExit("SEASON_BANDS not found in source")
    start = m.start()
    i = src.index("{", m.start())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                if end < len(src) and src[end] == ";":
                    end += 1
                return src[start:end]
    raise SystemExit("unclosed SEASON_BANDS object")


def parse_bands(block: str) -> dict:
    """Best-effort parse of the JS object into a simple dict."""
    bands = {}
    # peak: { ... months: [6, 7, 8], targetLow: 0.8, targetHigh: 0.95 ... }
    for name, body in re.findall(
        r"(\w+)\s*:\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", block
    ):
        if name in ("label",):
            continue
        months = re.search(r"months\s*:\s*\[([^\]]+)\]", body)
        tlo = re.search(r"targetLow\s*:\s*([0-9.]+)", body)
        thi = re.search(r"targetHigh\s*:\s*([0-9.]+)", body)
        label = re.search(r"label\s*:\s*['\"]([^'\"]+)['\"]", body)
        if not (months and tlo and thi):
            continue
        bands[name] = {
            "label": label.group(1) if label else name,
            "months": [int(x.strip()) for x in months.group(1).split(",") if x.strip()],
            "targetLow": float(tlo.group(1)),
            "targetHigh": float(thi.group(1)),
        }
    return bands


def load_local() -> str:
    if not LOCAL.is_file():
        raise FileNotFoundError(str(LOCAL))
    return LOCAL.read_text(encoding="utf-8")


def load_github() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            token = subprocess.check_output(
                ["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            token = None
    if not token:
        # fall back to SSM like R2
        try:
            token = subprocess.check_output(
                [
                    "aws",
                    "ssm",
                    "get-parameter",
                    "--name",
                    "/ai-code-push/github-token",
                    "--with-decryption",
                    "--query",
                    "Parameter.Value",
                    "--output",
                    "text",
                    "--region",
                    "us-east-1",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            token = None
    if not token:
        raise SystemExit("No GitHub token (gh auth, GITHUB_TOKEN, or SSM)")

    url = f"https://api.github.com/repos/{REPO}/contents/{PATH}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "pricing-skill-season-bands",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    if data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8")
    raise SystemExit("unexpected GitHub contents payload")


def main() -> int:
    ap = argparse.ArgumentParser(description="Print pricing-tool SEASON_BANDS")
    ap.add_argument("--github", action="store_true", help="Force GitHub API (not local)")
    ap.add_argument("--month", type=int, help="Calendar month 1-12")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    source = "github" if args.github else "local"
    try:
        src = load_github() if args.github else load_local()
        if not args.github:
            source = f"local:{LOCAL}"
    except FileNotFoundError:
        src = load_github()
        source = "github"

    block = extract_season_bands(src)
    bands = parse_bands(block)

    if args.json:
        print(json.dumps({"source": source, "repo": REPO, "bands": bands}, indent=2))
        return 0

    print(f"# SEASON_BANDS from {source}")
    print(f"# repo https://github.com/{REPO}  path {PATH}")
    print()
    for name, b in bands.items():
        lo = int(round(b["targetLow"] * 100))
        hi = int(round(b["targetHigh"] * 100))
        print(
            f"{name:10} months={b['months']}  "
            f"target={lo}–{hi}%  ({b['targetLow']}–{b['targetHigh']})  {b['label']}"
        )

    if args.month:
        hit = None
        for name, b in bands.items():
            if args.month in b["months"]:
                hit = (name, b)
                break
        print()
        if hit:
            name, b = hit
            lo = int(round(b["targetLow"] * 100))
            hi = int(round(b["targetHigh"] * 100))
            print(f"Month {args.month} → {name} ({b['label']}): {lo}–{hi}% goal")
        else:
            print(f"Month {args.month}: no band matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
