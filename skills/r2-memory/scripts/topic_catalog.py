#!/usr/bin/env python3
"""
When to retrieve R2Memory, and which skill to load.

Single source of truth for Grok + (copied) R2Lambda heuristics.
Do not dump full SKILL.md bodies into context — match a topic, retrieve
short Titan cards, then load only the named skill(s).
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

# Each topic: retrieve Titan, then load only these skills (by name).
# Patterns are case-insensitive. Keep them specific — "he" as a pronoun
# must NOT match HomeExchange.
TOPICS: list[dict[str, Any]] = [
    {
        "id": "memory",
        "title": "Standing prefs / R2Memory / skills",
        "retrieve": True,
        "skills": ["r2-memory", "always-push"],
        "when": "remember, we decided, always, mandate, embeddings, save this, add to skills",
        "pattern": (
            r"\b(remember|recall|we decided|mandate|standing|going forward|from now on|"
            r"save this|add to (?:your )?skills?|r2 ?memory|titan|embedding|"
            r"don't ask|do not ask|never ask|skill(?:s)? failed|skill catalog)\b"
        ),
    },
    {
        "id": "occupancy",
        "title": "Occupancy / guests / nights",
        "retrieve": True,
        "skills": ["hospitable"],
        "when": "who's staying, occupancy, occupied, vacant, check-in/out, block nights, guest name",
        "pattern": (
            r"\b(occupancy|occupied|vacant|who's staying|who is staying|"
            r"guest(?:s)?(?: name)?|check-?in|check-?out|block(?:ed|ing)? nights?|"
            r"reservation|hospitable)\b"
        ),
    },
    {
        "id": "home-exchange",
        "title": "HomeExchange",
        "retrieve": True,
        "skills": ["home-exchange"],
        "when": "HomeExchange, HE listing, HE dest search, GuestPoints, reciprocal, pre-approve",
        "pattern": (
            r"\b(homeexchange|home exchange|he (?:listing|dest(?:ination)?s?|search|calendar)|"
            r"guestpoints|guest points|reciprocal|pre-?approv)\b"
        ),
    },
    {
        "id": "family-travel",
        "title": "Family vacation / school calendar",
        "retrieve": True,
        "skills": ["family-travel", "home-exchange"],
        "when": "Cherry Crest, school break, Oahu, Hawaii trip, SEA-HNL, Christmas vacation",
        "pattern": (
            r"\b(cherry crest|school (?:break|calendar)|winter break|"
            r"oahu|ohau|hawaii trip|sea-?hnl|honolulu flight|"
            r"christmas (?:break|vacation|trip))\b"
        ),
    },
    {
        "id": "harness",
        "title": "Guest auto-reply / parking / eval",
        "retrieve": True,
        "skills": ["guest-messaging-harness"],
        "when": "parking, late checkout, auto-reply, harness, goldens, required phrases, Cassidy",
        "pattern": (
            r"\b(parking|late checkout|auto-?reply|harness|golden|required phrase|"
            r"eval failed|cassidy|post-?checkout|dirty[- ]?linen|isabella)\b"
        ),
    },
    {
        "id": "climate",
        "title": "Kumo / AC / heat",
        "retrieve": True,
        "skills": ["kumo"],
        "when": "AC, heat pump, Kumo, climate, temperature set",
        "pattern": r"\b(kumo|heat ?pump|mini-?split|climate history|air ?con|\bac\b)\b",
    },
    {
        "id": "pricing",
        "title": "Pricing / occupancy goals",
        "retrieve": True,
        "skills": ["pricing"],
        "when": "occupancy goals, SEASON_BANDS, pricing-tool, Sep/Oct fill",
        "pattern": r"\b(pricing-?tool|season_bands|occupancy goals?|base_prices|fill target)\b",
    },
    {
        "id": "billing",
        "title": "AWS cost / bill",
        "retrieve": True,
        "skills": ["aws-account"],
        "when": "AWS bill, cost explorer, cloud spend, account id",
        "pattern": r"\b(aws (?:bill|cost|spend)|cost explorer|cloud spend)\b",
    },
    {
        "id": "pine-cleaning-ical",
        "title": "Pine cleaning iCal / cleaner calendars",
        "retrieve": True,
        "skills": ["pine-cleaning-ical"],
        "when": "Pine cleaning calendar, .ics for Karen, pineCleaningIcal, HE Reserved on cleaning feed",
        "pattern": (
            r"\b(pine[- ]?cleaning[- ]?ical|pineCleaningIcal|"
            r"cleaning (?:calendar|ical|iCal)|pine-apt-(?:1b|2|3)\.ics|"
            r"karen (?:trask|calendar)|cleanforme207)\b"
        ),
    },
    {
        "id": "live-ops",
        "title": "Live ops (Grok skills — R2 assistant retired)",
        "retrieve": True,
        "skills": ["hospitable", "kumo", "pricing", "aws-account", "r2-memory"],
        "when": "ask R2, /r2, live unit status, past-month revenue",
        "pattern": r"\b(\/?r2\b|ask r2|live (?:unit|ops)|past-?month revenue)\b",
    },
    {
        "id": "ship",
        "title": "Commit / push / CI",
        "retrieve": True,
        "skills": ["always-push"],
        "when": "push, CI, public/private repo, shipped, OTA",
        "pattern": r"\b(always (?:commit|push)|git push|watch ci|repo (?:public|private)|want me to push)\b",
    },
]

# Extra memory-language the topic list may miss (parity with the original gate).
_EXTRA_RETRIEVE = [
    r"\b(you said|we (?:said|agreed|talked|discussed)|last time|previously|earlier|"
    r"what did (?:we|i|you)|did we|have we|as i (?:said|told)|you told me|"
    r"from (?:our|the) (?:chat|conversation|thread))\b",
    r"\b(decision|preference|we always|don't forget|do not forget|open (?:todo|item)|backlog)\b",
    r"\b(what was|what were) (?:the |our )?(?:last|previous|prior)\b",
    r"\b(permanently|permanent rule|durable)\b",
    r"\b(first time i|not the first|i (?:already )?said|as (?:we) (?:said|told))\b",
    r"\b(chat_shared|chat_grok|chat_agent|chat_catalog)\b",
]


def match_topics(message: str) -> list[dict[str, Any]]:
    s = message or ""
    if not s.strip():
        return []
    return [t for t in TOPICS if re.search(t["pattern"], s, re.I)]


def skills_for_message(message: str) -> list[str]:
    seen: list[str] = []
    for t in match_topics(message):
        for name in t.get("skills") or []:
            if name not in seen:
                seen.append(name)
    return seen


def needs_retrieval(message: str) -> bool:
    """True when the agent must Titan-retrieve before answering."""
    s = (message or "").strip()
    if not s:
        return False
    if match_topics(s):
        return True
    return any(re.search(p, s, re.I) for p in _EXTRA_RETRIEVE)


def format_topics_table() -> str:
    lines = [
        "id               retrieve  load skills                         when",
        "-" * 88,
    ]
    for t in TOPICS:
        skills = ",".join(t["skills"])
        lines.append(f"{t['id']:<16} {'yes' if t['retrieve'] else 'no':<9} {skills:<35} {t['when']}")
    return "\n".join(lines)


def catalog_source_hash() -> str:
    """Stable hash of topic ids + patterns — used to know when to re-embed."""
    blob = "\n".join(f"{t['id']}|{t['pattern']}|{','.join(t['skills'])}" for t in TOPICS)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
