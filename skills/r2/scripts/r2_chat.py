#!/usr/bin/env python3
"""Retired. R2Lambda / in-app R2 chat were removed 2026-09-07. Use hospitable / kumo / pricing / aws-account / r2-memory."""

from __future__ import annotations

import sys

RETIRED = """R2 assistant is retired (2026-09-07).
Do not invoke R2Lambda.

Use:
  hospitable   occupancy, guests, calendar, messages
  kumo         AC / heat pump
  pricing      occupancy goals + weekly S3 report
  aws-account  AWS bill
  r2-memory    Titan standing prefs / past Q&A
"""


def main(argv: list[str] | None = None) -> int:
    sys.stderr.write(RETIRED)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
