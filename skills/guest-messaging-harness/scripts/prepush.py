#!/usr/bin/env python3
"""Load GROK_API_KEY from SSM and run the harness prepush gate.

Never prints the key. Never writes it to disk.
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


def main() -> int:
    root = _harness_root()
    prepush = root / "scripts" / "prepush.js"
    if not prepush.is_file():
        print(f"FAIL: harness prepush not found at {prepush}", file=sys.stderr)
        return 1
    _load_grok_key()
    print(f"guest-messaging-harness prepush → {root}")
    result = subprocess.run(["node", str(prepush)], cwd=str(root))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
