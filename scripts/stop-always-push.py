#!/usr/bin/env python3
"""Stop gate: never end a turn after asking push? or leaving CB commits unpushed."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

REPOS = [
    "cleaningbutton-website",
    "cleaningbutton-api",
    "cleaningbutton-android",
    "R2Lambda",
    "R2IOS",
    "cleaningbutton-ai-code-push",
    "localGrokSkills",
]

ASK_PUSH = re.compile(
    r"(want me to push|shall i push|should i (commit and )?push|"
    r"ready to push when|i can push if you|want me to (commit|deploy)|"
    r"shall i (commit|deploy)|confirm (before )?(i )?push|ok to push\?|"
    r"push (both|them|it|to main)?\?)",
    re.I,
)
# softer: push + question + permission vibe
ASK_PUSH_SOFT = re.compile(
    r"\bpush\b.{0,60}\?",
    re.I,
)
SOFT_WORDS = ("want", "shall", "should", "confirm", "ready", "if you", "ok to")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    reason = data.get("reason") or ""
    # Gate only genuine turn ends; allow empty reason (some runners omit it)
    if reason and reason not in ("end_turn", "null"):
        return 0

    stop_active = bool(data.get("stopHookActive"))
    last = data.get("lastAssistantMessage") or ""
    last_l = last.lower()

    asked = bool(ASK_PUSH.search(last_l))
    if not asked and ASK_PUSH_SOFT.search(last_l):
        asked = any(w in last_l for w in SOFT_WORDS)

    if asked:
        if stop_active:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "Stop",
                            "additionalContext": (
                                "MANDATE: never ask push again. Next turn: just push."
                            ),
                        }
                    }
                )
            )
            return 0
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "HARD MANDATE (user): You asked for push permission. NEVER do that. "
                        "Immediately commit (if needed), git push origin main, watch CI to green. "
                        "Do not ask. Exception only: force-push/destructive or user said not to push."
                    ),
                }
            )
        )
        return 0

    home = os.path.expanduser("~")
    unpushed = []
    for name in REPOS:
        path = os.path.join(home, name)
        if not os.path.isdir(os.path.join(path, ".git")):
            continue
        try:
            out = subprocess.check_output(
                ["git", "-C", path, "rev-list", "--count", "@{u}..HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
            ).strip()
            ahead = int(out or "0")
        except Exception:
            ahead = 0
        if ahead > 0:
            unpushed.append(f"{name}(+{ahead})")

    if unpushed:
        listing = " ".join(unpushed)
        if stop_active:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "Stop",
                            "additionalContext": (
                                f"Still unpushed: {listing} — push now if credentials allow."
                            ),
                        }
                    }
                )
            )
            return 0
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        f"HARD MANDATE: Unpushed commits remain: {listing} — "
                        "run git push on each, then gh run watch until CI green. Do not ask the user."
                    ),
                }
            )
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
