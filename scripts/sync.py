#!/usr/bin/env python3
"""localGrokSkills sync: pull on Grok launch, commit+push when skills change."""
from __future__ import annotations

import argparse
import fcntl
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK_PATH = os.path.join(ROOT, ".sync.lock")
REPO = "jeromevidaao/localGrokSkills"
REMOTE = "origin"
BRANCH = "main"


def run(
    args: list[str], timeout: int = 60, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )


def gh_token() -> str:
    r = run(["gh", "auth", "token"], timeout=10)
    return (r.stdout or "").strip() if r.returncode == 0 else ""


def git(args: list[str], timeout: int = 40) -> subprocess.CompletedProcess[str]:
    """git, retrying once with a gh token if HTTPS auth flakes after visibility flips."""
    r = run(["git", *args], timeout=timeout)
    if r.returncode == 0:
        return r
    token = gh_token()
    if not token:
        return r
    header = f"AUTHORIZATION: bearer {token}"
    return run(["git", "-c", f"http.extraheader={header}", *args], timeout=timeout)


def acquire_lock() -> int | None:
    fd = os.open(LOCK_PATH, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    return fd


def is_dirty() -> bool:
    r = run(["git", "status", "--porcelain"])
    return bool((r.stdout or "").strip())


def log(msg: str) -> None:
    print(f"localGrokSkills: {msg}", file=sys.stderr)


def cmd_pull() -> int:
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        log("not a git repo — skip pull")
        return 0
    if is_dirty():
        log("local changes present — skip pull (Stop hook will commit)")
        return 0
    try:
        r = git(["pull", "--ff-only", REMOTE, BRANCH], timeout=40)
    except subprocess.TimeoutExpired:
        log("pull timed out (offline?) — fail-open")
        return 0
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().splitlines()
        last = err[-1] if err else "unknown"
        if "AUTHORIZATION: bearer" in last:
            last = "auth failed"
        log(f"pull failed (offline or diverged): {last}")
        return 0
    out = (r.stdout or "").strip()
    if "Already up to date" in out or "Already up-to-date" in out:
        log("up to date")
    else:
        log("pulled latest")
    return 0


def set_visibility(public: bool) -> None:
    vis = "public" if public else "private"
    run(
        [
            "gh",
            "repo",
            "edit",
            REPO,
            "--visibility",
            vis,
            "--accept-visibility-change-consequences",
        ],
        timeout=30,
    )


def cmd_commit_push() -> int:
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        log("not a git repo — skip commit")
        return 0
    if not is_dirty():
        return 0

    run(["git", "add", "-A"])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    c = run(["git", "commit", "-m", f"skills: auto-sync {stamp}"])
    if c.returncode != 0:
        err = (c.stderr or c.stdout or "").strip()
        log(f"commit skipped: {err}")
        return 0

    try:
        set_visibility(True)
    except Exception as exc:
        log(f"visibility public failed: {exc}")

    p = git(["push", REMOTE, BRANCH], timeout=60)
    if p.returncode != 0:
        err = (p.stderr or p.stdout or "").strip().splitlines()
        last = err[-1] if err else "unknown"
        if "AUTHORIZATION: bearer" in last:
            last = "auth failed"
        log(f"push failed: {last}")
        return 0

    time.sleep(4)
    w = run(["gh", "run", "watch", "--exit-status"], timeout=180)
    if w.returncode != 0:
        log("CI not green — leaving repo public so the next turn can fix")
        return 0

    try:
        set_visibility(False)
    except Exception as exc:
        log(f"visibility private failed: {exc}")
        return 0

    log("committed, pushed, CI green, private")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pull", "commit-push"))
    args = parser.parse_args()

    fd = acquire_lock()
    if fd is None:
        log("another sync is running — skip")
        return 0
    try:
        if args.action == "pull":
            return cmd_pull()
        return cmd_commit_push()
    except subprocess.TimeoutExpired:
        log("timed out — fail-open")
        return 0
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


if __name__ == "__main__":
    sys.exit(main())
