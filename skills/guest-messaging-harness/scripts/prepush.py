#!/usr/bin/env python3
"""Load GROK_API_KEY from SSM and run the harness prepush gate.

Never prints the key. Never writes it to disk.

Usage:
  python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py
  RUN_LIVE_GROK_UNIT=1 python3 .../prepush.py   # also run live-Grok unit tests

By default (same as CI), prepush sets SKIP_LIVE_GROK_UNIT=1 for `npm test` so
live-Grok *unit* describes are skipped. Full live eval remains the push gate.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SSM_NAME = "/grok/api-key"
DEFAULT_HARNESS = Path.home() / "auto-reply-sqs-harness"


def _harness_root() -> Path:
    env = os.environ.get("HARNESS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    cwd = Path.cwd()
    if (cwd / "eval" / "runner.js").is_file() and (cwd / "src" / "agent.js").is_file():
        return cwd
    return DEFAULT_HARNESS


def _load_grok_key() -> None:
    if os.environ.get("GROK_API_KEY"):
        return
    proc = subprocess.run(
        [
            "aws",
            "ssm",
            "get-parameter",
            "--name",
            SSM_NAME,
            "--with-decryption",
            "--query",
            "Parameter.Value",
            "--output",
            "text",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        print(
            f"FAIL: could not load GROK_API_KEY from SSM {SSM_NAME}.",
            file=sys.stderr,
        )
        if err:
            print(err, file=sys.stderr)
        sys.exit(1)
    key = (proc.stdout or "").strip()
    if not key or key == "None":
        print(f"FAIL: SSM {SSM_NAME} was empty.", file=sys.stderr)
        sys.exit(1)
    os.environ["GROK_API_KEY"] = key
    # Share live Grok eval responses in DDB when prompts unchanged.
    os.environ.setdefault("GROK_EVAL_CACHE", "1")


def _ensure_hooks_path(root: Path) -> None:
    """Force git to use the repo pre-push gate (never discover CI failures first)."""
    desired = "scripts/git-hooks"
    proc = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    current = (proc.stdout or "").strip()
    if current != desired:
        subprocess.run(
            ["git", "config", "core.hooksPath", desired],
            cwd=str(root),
            check=False,
        )
        print(f"Set core.hooksPath={desired} (was {current or 'unset'})")


def _print_help() -> None:
    print(
        """guest-messaging-harness prepush

Loads GROK_API_KEY from SSM /grok/api-key (if unset) and runs harness
scripts/prepush.js: phrase check → npm test → full live eval (when needed).

  SKIP_LIVE_GROK_UNIT=1 is set for npm test by default (same as CI).
  Full live eval is unchanged — that is the push gate.
  Force live-Grok unit tests: RUN_LIVE_GROK_UNIT=1

Env:
  HARNESS_ROOT          Override harness checkout path
  GROK_API_KEY          Skip SSM if already set
  RUN_LIVE_GROK_UNIT=1  Run live-Grok unit describes during npm test
  GROK_EVAL_CACHE       Default 1 (DDB cache for live eval)
"""
    )


def main() -> int:
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        _print_help()
        return 0
    root = _harness_root()
    _ensure_hooks_path(root)
    prepush = root / "scripts" / "prepush.js"
    if not prepush.is_file():
        print(f"FAIL: harness prepush not found at {prepush}", file=sys.stderr)
        return 1
    _load_grok_key()
    # Mirror CI for npm test unless the caller forces live unit.
    # scripts/prepush.js also applies this for `npm run prepush`.
    if os.environ.get("RUN_LIVE_GROK_UNIT") != "1":
        os.environ.setdefault("SKIP_LIVE_GROK_UNIT", "1")
    print(f"guest-messaging-harness prepush → {root}")
    result = subprocess.run(["node", str(prepush)], cwd=str(root))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
