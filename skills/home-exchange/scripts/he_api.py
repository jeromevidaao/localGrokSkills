#!/usr/bin/env python3
"""HomeExchange API from this laptop.

Auth is always AWS SSM GetParameter (SecureString). The bearer is held in
memory for this process only — never written to disk, never printed, never
accepted as a CLI flag that would land in shell history as a token value.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

REGION = os.environ.get("AWS_REGION", "us-east-1")
HE_API_BASE = os.environ.get("HE_API_BASE", "https://api.homeexchange.com").rstrip("/")
HE_BFF_BASE = os.environ.get("HE_BFF_BASE", "https://bff.homeexchange.com").rstrip("/")
HE_BEARER_SSM = os.environ.get("HE_BEARER_SSM", "/homeexchange/bearer-token")
HE_REFRESH_FN = os.environ.get("HE_TOKEN_REFRESH_FUNCTION", "he-token-refresh")
HE_WEB_VERSION = os.environ.get("HE_WEB_VERSION", "20.32.0-rc.1")
# Jawg/whosonfirst ids the search UI uses for common dests
HE_PLACES = {
    "manhattan": ("whosonfirst:borough:421205771", "Manhattan, NY, USA"),
    "nyc": ("whosonfirst:locality:85977539", "New York, NY, USA"),
    "new-york": ("whosonfirst:locality:85977539", "New York, NY, USA"),
    "newyork": ("whosonfirst:locality:85977539", "New York, NY, USA"),
}
# Public listing page. /home/{id} is a 404. /homes/view/{id} 200s and
# lands on /holiday-home/{id}. Always use this in results and when opening.
HE_LISTING_PATH = "https://www.homeexchange.com/homes/view/{id}"

# Standing (2026-08-16): pay with GuestPoints, not a home swap.
# UI: "available" = GP or reciprocal on those nights; "guest-wanted" = GP-only
# nights. Both accept points. "reciprocal" is swap-only — omit unless asked.
# Do not send only ["guest-wanted"]: that drops AVAILABLE (dual) homes.
HE_EXCHANGE_POINTS = ["available", "guest-wanted"]
HE_EXCHANGE_RECIPROCAL = ["reciprocal"]
HE_GP_CAL_TYPES = frozenset({"AVAILABLE", "available", "NON_RECIPROCAL"})
HE_HOME_ID = os.environ.get("HE_HOME_ID", "3202475")
# Pine HE homes (Apt #3 original; Apt #2 and #1B created 2026-08-15)
HE_HOMES = {
    "apt3": "3202475",
    "apt2": "3285044",
    "apt1b": "3285159",
}

_token: str | None = None


def _aws(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["aws", *args, "--region", REGION],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def ssm_get(name: str) -> str:
    r = _aws(
        [
            "ssm",
            "get-parameter",
            "--name",
            name,
            "--with-decryption",
            "--query",
            "Parameter.Value",
            "--output",
            "text",
        ]
    )
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().replace("\n", " ")[:240]
        raise RuntimeError(f"SSM get {name} failed: {err or 'unknown'}")
    value = (r.stdout or "").strip()
    if not value or value == "None":
        raise RuntimeError(f"SSM {name} is empty")
    return value


def load_bearer(*, force: bool = False) -> str:
    global _token
    if force:
        _token = None
    if _token:
        return _token
    _token = ssm_get(HE_BEARER_SSM).strip()
    return _token


def redact(text: str) -> str:
    if not text:
        return text
    out = text
    if _token and _token in out:
        out = out.replace(_token, "<redacted-bearer>")
    out = out.replace("Bearer ", "Bearer <redacted> ")
    return out


def invoke_token_refresh() -> None:
    out_path = f"/tmp/he-token-refresh-{os.getpid()}.json"
    r = _aws(
        [
            "lambda",
            "invoke",
            "--function-name",
            HE_REFRESH_FN,
            "--cli-binary-format",
            "raw-in-base64-out",
            "--payload",
            '{"source":"localGrokSkills-he-api"}',
            out_path,
        ],
        timeout=90,
    )
    if r.returncode != 0:
        err = redact((r.stderr or r.stdout or "").strip())[:240]
        raise RuntimeError(f"{HE_REFRESH_FN} invoke failed: {err}")
    try:
        os.unlink(out_path)
    except OSError:
        pass
    load_bearer(force=True)


def he_request(
    method: str,
    path: str,
    body: dict[str, Any] | list[Any] | None = None,
    *,
    retry_401: bool = True,
    base: str | None = None,
    extra_headers: dict[str, str] | None = None,
    referer: str = "https://www.homeexchange.com/conversations",
) -> tuple[int, Any]:
    token = load_bearer()
    url = (base or HE_API_BASE).rstrip("/") + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en",
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "he_web_version": HE_WEB_VERSION,
        "origin": "https://www.homeexchange.com",
        "referer": referer,
        "User-Agent": "localGrokSkills-home-exchange/1.0",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        url,
        data=data,
        method=method.upper(),
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = exc.code
        if status == 401 and retry_401:
            invoke_token_refresh()
            return he_request(
                method,
                path,
                body,
                retry_401=False,
                base=base,
                extra_headers=extra_headers,
                referer=referer,
            )
        raise RuntimeError(f"HE {method} {path} HTTP {status}: {redact(raw)[:400]}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"HE {method} {path} network: {exc.reason}") from None

    parsed: Any = None
    if raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": redact(raw)[:800]}
    if status < 200 or status >= 300:
        raise RuntimeError(f"HE {method} {path} HTTP {status}: {redact(raw)[:400]}")
    return status, parsed


def emit(obj: Any, as_json: bool) -> None:
    if as_json:
        json.dump(obj, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return
    if isinstance(obj, str):
        print(obj)
        return
    print(json.dumps(obj, indent=2, default=str))


def cmd_me(_: argparse.Namespace, as_json: bool) -> int:
    _, data = he_request("GET", "/v1/users/me")
    if as_json:
        emit(data, True)
        return 0
    user = data if isinstance(data, dict) else {}
    emit(
        {
            "id": user.get("id") or (user.get("user") or {}).get("id"),
            "email": user.get("email") or (user.get("user") or {}).get("email"),
            "first_name": user.get("first_name") or (user.get("user") or {}).get("first_name"),
        },
        False,
    )
    return 0


def _peer_name(node: dict[str, Any], self_id: str | None) -> str | None:
    inter = node.get("interlocutor") or {}
    if isinstance(inter, dict) and inter.get("first_name"):
        return str(inter["first_name"])
    for key in ("exchanges", "all_exchanges"):
        items = node.get(key) or []
        if not isinstance(items, list):
            continue
        for ex in items:
            guest = (ex or {}).get("guest") or {}
            gid = str(guest.get("id") or "")
            if self_id and gid == str(self_id):
                continue
            if guest.get("first_name"):
                return str(guest["first_name"])
    return None


def _date_range(node: dict[str, Any]) -> str | None:
    items = node.get("exchanges") or node.get("all_exchanges") or []
    if not isinstance(items, list) or not items:
        return None
    first = items[0] or {}
    start = str(first.get("start_on") or "")[:10]
    end = str(first.get("end_on") or "")[:10]
    if start and end:
        return f"{start} → {end}"
    return None


def cmd_conversations(args: argparse.Namespace, as_json: bool) -> int:
    limit = max(1, min(int(args.limit), 50))
    _, me = he_request("GET", "/v1/users/me")
    self_id = None
    if isinstance(me, dict):
        self_id = me.get("id") or (me.get("user") or {}).get("id")
        if self_id is not None:
            self_id = str(self_id)
    _, data = he_request("GET", f"/v3/conversations/me?limit={limit}")
    conv = ((data or {}).get("data") or {}).get("conversations") or {}
    edges = conv.get("edges") or []
    rows = []
    for edge in edges:
        node = (edge or {}).get("node") or edge or {}
        lm = node.get("last_message") or {}
        rows.append(
            {
                "id": str(node["id"]) if node.get("id") is not None else None,
                "peer": _peer_name(node, self_id),
                "dates": _date_range(node),
                "unread": node.get("unread_messages_count") or 0,
                "last_at": (lm.get("send_at") if isinstance(lm, dict) else None)
                or node.get("updated_at"),
                "last_text": (
                    str(lm.get("content") or "")[:160] if isinstance(lm, dict) else ""
                ),
            }
        )
    emit(
        {"total": conv.get("totalCount", len(rows)), "conversations": rows}
        if not as_json
        else data,
        as_json,
    )
    return 0


def cmd_conversation(args: argparse.Namespace, as_json: bool) -> int:
    cid = args.conversation_id
    _, data = he_request("GET", f"/v3/conversations/me/{urllib.parse.quote(cid, safe='')}")
    emit(data, as_json or True)
    return 0


def cmd_messages(args: argparse.Namespace, as_json: bool) -> int:
    cid = urllib.parse.quote(args.conversation_id, safe="")
    _, data = he_request("GET", f"/v3/messages?conversation_id={cid}")
    if as_json:
        emit(data, True)
        return 0
    msgs = (data or {}).get("data", {}).get("messages") or (data or {}).get("messages") or []
    rows = []
    for m in msgs:
        author = (m or {}).get("author") or {}
        rows.append(
            {
                "id": (m or {}).get("id"),
                "at": (m or {}).get("send_at") or (m or {}).get("created_at"),
                "from": author.get("first_name") or author.get("id"),
                "type": (m or {}).get("type"),
                "text": str((m or {}).get("content") or "")[:400],
            }
        )
    emit({"count": len(rows), "messages": rows}, False)
    return 0


def cmd_homes(_: argparse.Namespace, as_json: bool) -> int:
    _, data = he_request("GET", "/v1/homes/me")
    if as_json:
        emit(data, True)
        return 0
    rows = []
    for h in data if isinstance(data, list) else []:
        title = None
        descs = h.get("descriptions") or []
        if descs:
            title = descs[0].get("title")
        rows.append(
            {
                "id": h.get("id"),
                "address": h.get("address"),
                "title": title,
                "capacity": h.get("capacity"),
                "completion": h.get("completion_rate"),
                "images": len(h.get("images") or []),
            }
        )
    emit({"homes": rows}, False)
    return 0


def cmd_home(args: argparse.Namespace, as_json: bool) -> int:
    hid = args.home_id or HE_HOME_ID
    _, data = he_request("GET", f"/v1/homes/{urllib.parse.quote(str(hid), safe='')}")
    emit(data, True if as_json else True)
    return 0


def cmd_request(args: argparse.Namespace, as_json: bool) -> int:
    body = None
    if args.body:
        body = json.loads(args.body)
    _, data = he_request(args.method.upper(), args.path, body)
    emit(data, True)
    return 0


def cmd_calendar(args: argparse.Namespace, as_json: bool) -> int:
    home_id = args.home_id or HE_HOME_ID
    _, data = he_request("GET", f"/v1/homes/{urllib.parse.quote(str(home_id), safe='')}/calendar")
    ranges = data.get("data") if isinstance(data, dict) else data
    if not isinstance(ranges, list):
        ranges = []
    if as_json:
        emit(data, True)
        return 0
    emit({"home_id": str(home_id), "ranges": ranges}, False)
    return 0


def cmd_exchanges(args: argparse.Namespace, as_json: bool) -> int:
    cid = urllib.parse.quote(args.conversation_id, safe="")
    _, data = he_request("GET", f"/v1/exchanges/{cid}/get-exchanges")
    emit(data if as_json else {"exchanges": data if isinstance(data, list) else data}, as_json)
    return 0


def cmd_send(args: argparse.Namespace, as_json: bool) -> int:
    cid = args.conversation_id
    text = args.text
    if not text or not str(text).strip():
        raise RuntimeError("send requires --text")
    conv: Any = int(cid) if str(cid).isdigit() else cid
    _, data = he_request("POST", "/v1/messages", {"content": text, "conversation": conv})
    emit(data if data is not None else {"ok": True}, as_json or True)
    return 0


# BFF createStayRequestV3. 400 if stayType is not one of these strings
# (numeric calendar types like 1 are invalid). GuestPoints = WITH-GP.
HE_STAY_TYPES = {
    "points": "WITH-GP",
    "gp": "WITH-GP",
    "with-gp": "WITH-GP",
    "guestpoints": "WITH-GP",
    "reciprocal": "RECIPROCAL",
    "reciprocal-with-gp": "RECIPROCAL-WITH-GP",
}


def cmd_request_stay(args: argparse.Namespace, as_json: bool) -> int:
    """POST bff /exchange/v3 — new GuestPoints (or swap) request. Write."""
    if not args.yes:
        raise RuntimeError("request-stay is a write: pass --yes")
    text = (args.text or "").strip()
    if not text:
        raise RuntimeError("request-stay requires --text")
    stay = HE_STAY_TYPES.get((args.exchange or "points").strip().lower())
    if not stay:
        raise RuntimeError("exchange must be points | reciprocal | reciprocal-with-gp")

    _, me = he_request("GET", "/v1/users/me")
    verified = (me or {}).get("verified_status")
    guest_id = (me or {}).get("id")
    if verified != 1 and not args.force:
        raise RuntimeError(
            f"HE verified_status={verified} (need 1). Outbound stay requests "
            "are blocked until the account is verified. --force to try anyway."
        )
    if not guest_id:
        raise RuntimeError("GET /v1/users/me has no id")

    hid = int(args.home_id)
    host_id = int(args.host_id) if args.host_id else None
    if host_id is None:
        _, home = he_request("GET", f"/v1/homes/{hid}")
        user = (home or {}).get("user") or {}
        host_id = user.get("id")
        if not host_id:
            raise RuntimeError(f"home {hid} has no user.id")

    adults = max(1, int(args.adults))
    children = max(0, int(args.children))
    babies = max(0, int(args.babies))
    body = {
        "stayType": stay,
        "startDate": args.start_on,
        "endDate": args.end_on,
        "homeId": hid,
        "hostId": int(host_id),
        "guestId": int(guest_id),
        "guestNumber": adults + children + babies,
        "content": text,
    }
    _, data = he_request(
        "POST",
        "/exchange/v3",
        body,
        base=HE_BFF_BASE,
        referer=HE_LISTING_PATH.format(id=hid),
        extra_headers={"X-HE-PAGE-NAME": f"/holiday-home/{hid}"},
    )
    emit(data if data is not None else {"ok": True}, as_json or True)
    return 0


def _place_key(name: str) -> str:
    return (name or "").strip().lower().replace(" ", "-").replace("_", "-")


def resolve_place(place: str, location_id: str | None) -> tuple[dict[str, Any], str, str | None]:
    """Return (location query, label, location_id or None)."""
    if location_id:
        return (
            {"polygon": {"location_id": location_id, "provider": "jawg"}},
            place or location_id,
            location_id,
        )
    key = _place_key(place)
    if key in HE_PLACES:
        loc_id, label = HE_PLACES[key]
        return (
            {"polygon": {"location_id": loc_id, "provider": "jawg"}},
            label,
            loc_id,
        )
    bounds, label = nominatim_bounds(place)
    return ({"bounds": bounds}, label, None)


def nominatim_bounds(place: str) -> tuple[dict[str, Any], str]:
    q = urllib.parse.urlencode({"q": place, "format": "json", "limit": 1})
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{q}",
        headers={
            "User-Agent": "localGrokSkills-home-exchange/1.0 (CleaningButton dest search)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        hits = json.loads(resp.read().decode("utf-8", errors="replace"))
    if not hits:
        raise RuntimeError(
            f"unknown place {place!r} — add to HE_PLACES or pass --location-id"
        )
    hit = hits[0]
    south, north, west, east = (float(x) for x in hit["boundingbox"])
    label = hit.get("display_name") or place
    return (
        {"sw": {"lat": south, "lon": west}, "ne": {"lat": north, "lon": east}},
        label,
    )


def in_manhattan(lat: float | None, lon: float | None, admins: dict[str, Any] | None, title: str) -> bool:
    if lat is None or lon is None:
        return False
    if lon <= -74.02:
        return False
    if lat < 40.70 or lat > 40.882:
        return False
    # Inwood / Washington Heights sit farther east than midtown FDR
    east = -73.91 if lat >= 40.82 else -73.94
    if lon >= east:
        return False
    if lon > -73.955 and lat < 40.76:
        return False
    if isinstance(admins, dict) and (admins.get("admin1") or "").lower() == "new jersey":
        return False
    low = (title or "").lower()
    if any(x in low for x in ("brooklyn", "jersey city", "hoboken", "ridgewood", "long island city")):
        return False
    # do not match "lic " — it hits "public transit"
    return True


def stay_nights(start: str, end: str) -> int | None:
    try:
        y1, m1, d1 = (int(x) for x in start.split("-"))
        y2, m2, d2 = (int(x) for x in end.split("-"))
        from datetime import date

        return (date(y2, m2, d2) - date(y1, m1, d1)).days
    except (TypeError, ValueError):
        return None


def calendar_gp_overlap(home_id: Any, start: str, end: str) -> list[dict[str, Any]]:
    _, cal = he_request("GET", f"/v1/homes/{urllib.parse.quote(str(home_id), safe='')}/calendar")
    ranges = cal.get("data") if isinstance(cal, dict) else cal
    hits: list[dict[str, Any]] = []
    if not isinstance(ranges, list):
        return hits
    for p in ranges:
        s = str((p or {}).get("start_on") or "")[:10]
        e = str((p or {}).get("end_on") or "")[:10]
        if s and e and s < end and e > start:
            hits.append({"start": s, "end": e, "type": (p or {}).get("type")})
    return hits


def bff_search(query: dict[str, Any], offset: int, limit: int, place_label: str, loc_id: str | None) -> Any:
    body: dict[str, Any] = {"search_query": query}
    if loc_id:
        body["last_search"] = {"place": place_label, "place_id": loc_id}
    _, data = he_request(
        "POST",
        f"/search/homes?offset={offset}&limit={limit}",
        body,
        base=HE_BFF_BASE,
        extra_headers={
            "X-SEARCH-API-VERSION": "v2",
            "X-LEGACY-RESPONSE": "true",
            "X-HE-PAGE-NAME": "/search-v2",
        },
        referer="https://www.homeexchange.com/search-v2",
    )
    return data


def cmd_search(args: argparse.Namespace, as_json: bool) -> int:
    location, place_label, loc_id = resolve_place(args.place or "manhattan", args.location_id)
    start = args.start_on
    end = args.end_on
    adults = max(0, int(args.adults))
    children = max(0, int(args.children))
    babies = max(0, int(args.babies))
    limit = max(1, min(int(args.limit), 40))
    offset = max(0, int(args.offset))
    exchange = (args.exchange or "points").strip().lower()
    if exchange in {"points", "gp", "guestpoints", "guest-wanted", "non-reciprocal"}:
        exchange_types: list[str] | None = list(HE_EXCHANGE_POINTS)
    elif exchange in {"reciprocal", "swap"}:
        exchange_types = list(HE_EXCHANGE_RECIPROCAL)
    elif exchange in {"both", "any", "all"}:
        exchange_types = None
    else:
        raise RuntimeError("exchange must be points | reciprocal | both")

    query: dict[str, Any] = {"location": location}
    cal: dict[str, Any] = {}
    if start and end:
        cal["date_ranges"] = [{"from": start, "to": end}]
    if exchange_types:
        cal["exchange_types"] = exchange_types
    if cal:
        query["calendar"] = cal
    size: dict[str, Any] = {}
    if adults or children or babies:
        size["beds"] = {"adults": adults, "children": children, "babies": babies}
    bedrooms = getattr(args, "bedrooms", None)
    if bedrooms is not None and int(bedrooms) > 0:
        size["bedrooms"] = int(bedrooms)
    if size:
        query.setdefault("home", {})["size"] = size
    filters: list[str] = []
    if args.response_rate:
        filters.append("response-rate-above-threshold")
    if filters:
        query["filters"] = filters
    if args.children_welcome and not args.no_children_welcome:
        query.setdefault("home", {}).setdefault("amenities", []).append("children-welcome")

    data = bff_search(query, offset, limit, place_label, loc_id)
    homes = (data or {}).get("homes") or []
    if not isinstance(homes, list):
        homes = []
    nights = stay_nights(start, end) if start and end else None
    place_key = _place_key(args.place or "")
    rows = []
    skipped: list[dict[str, Any]] = []
    for h in homes:
        user = h.get("user") or {}
        loc = h.get("location") or {}
        adm = h.get("translated_admins") if isinstance(h.get("translated_admins"), dict) else {}
        descs = h.get("descriptions") or []
        title = None
        if isinstance(descs, list) and descs:
            en = next(
                (d for d in descs if isinstance(d, dict) and d.get("locale") == "en"),
                descs[0],
            )
            if isinstance(en, dict):
                title = en.get("title")
        lat = loc.get("latitude") if isinstance(loc, dict) else None
        lon = loc.get("longitude") if isinstance(loc, dict) else None
        if args.clip_manhattan or place_key == "manhattan":
            if not in_manhattan(lat, lon, adm, title or ""):
                skipped.append({"id": h.get("id"), "reason": "not_manhattan", "title": title})
                continue
        low_title = (title or "").lower()
        if exchange_types is not None and HE_EXCHANGE_RECIPROCAL[0] not in exchange_types:
            if any(
                x in low_title
                for x in ("no gp", "no gps", "reciprocal only", "reciprocal exchange only")
            ):
                skipped.append({"id": h.get("id"), "reason": "title_rejects_points", "title": title})
                continue
        min_n = h.get("min_nights")
        if nights and isinstance(min_n, int) and min_n > nights:
            skipped.append({"id": h.get("id"), "reason": f"min_nights {min_n}>{nights}", "title": title})
            continue
        overlap: list[dict[str, Any]] | None = None
        if args.verify and start and end and h.get("id") is not None:
            try:
                overlap = calendar_gp_overlap(h.get("id"), start, end)
            except Exception as exc:
                skipped.append({"id": h.get("id"), "reason": f"calendar {exc}", "title": title})
                continue
            gp_ok = [p for p in overlap if p.get("type") in HE_GP_CAL_TYPES]
            if not gp_ok:
                skipped.append(
                    {
                        "id": h.get("id"),
                        "reason": "reciprocal_only_or_closed",
                        "calendar": overlap,
                        "title": title,
                    }
                )
                continue
        hid = h.get("id")
        listing_url = HE_LISTING_PATH.format(id=hid)
        rows.append(
            {
                "id": hid,
                "listing": f"[{hid}]({listing_url})",
                "title": (title or "")[:120],
                "capacity": h.get("capacity"),
                "gp_night": h.get("guestpoint_per_night"),
                "gp_stay": (
                    (h.get("guestpoint_per_night") or 0) * nights
                    if nights and h.get("guestpoint_per_night")
                    else None
                ),
                "min_nights": min_n,
                "exchanges": h.get("exchange_count"),
                "host": user.get("first_name"),
                "resp": user.get("response_rate"),
                "verified": bool(user.get("is_verified") or h.get("is_verified")),
                "lat": lat,
                "lon": lon,
                "calendar": overlap,
                "url": listing_url,
            }
        )
    rows.sort(key=lambda r: (r.get("resp") or 0, r.get("exchanges") or 0), reverse=True)
    out = {
        "place": place_label,
        "location_id": loc_id,
        "exchange": exchange,
        "dates": f"{start} → {end}" if start and end else None,
        "nights": nights,
        "guests": {"adults": adults, "children": children, "babies": babies},
        "bedrooms_min": int(bedrooms) if bedrooms else None,
        "total": (data or {}).get("total"),
        "returned": len(rows),
        "skipped": len(skipped),
        "homes": rows,
    }
    if as_json:
        out["skipped_homes"] = skipped
        emit(out, True)
        return 0
    emit(out, False)
    return 0


def cmd_publish(args: argparse.Namespace, as_json: bool) -> int:
    hid = args.home_id
    _, data = he_request(
        "PATCH",
        f"/v1/homes/{urllib.parse.quote(str(hid), safe='')}",
        {"status": 5, "contact_allowed": 0, "prefers_reciprocal": False},
    )
    emit(
        {
            "id": data.get("id") if isinstance(data, dict) else hid,
            "status": data.get("status") if isinstance(data, dict) else None,
            "completion": data.get("completion_rate") if isinstance(data, dict) else None,
        }
        if not as_json
        else data,
        as_json,
    )
    return 0


def cmd_approve(args: argparse.Namespace, as_json: bool) -> int:
    if not args.yes:
        raise RuntimeError("approve is a write — pass --yes")
    cid = args.conversation_id
    _, current = he_request(
        "GET", f"/v1/exchanges/{urllib.parse.quote(cid, safe='')}/get-exchanges"
    )
    exchanges = current if isinstance(current, list) else (current or {}).get("data") or []
    if not exchanges:
        raise RuntimeError("no exchanges on conversation")
    _, data = he_request(
        "PATCH",
        f"/v1/exchanges/{urllib.parse.quote(cid, safe='')}/approve",
        exchanges,
    )
    emit(data if data is not None else {"ok": True}, as_json or True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="raw JSON")
    p = argparse.ArgumentParser(
        description="HomeExchange API (token from SSM /homeexchange/bearer-token).",
        parents=[common],
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("me", help="GET /v1/users/me", parents=[common])

    c = sub.add_parser("conversations", help="GET /v3/conversations/me", parents=[common])
    c.add_argument("--limit", type=int, default=20)

    c = sub.add_parser("conversation", help="GET /v3/conversations/me/{id}", parents=[common])
    c.add_argument("conversation_id")

    c = sub.add_parser("messages", help="GET /v3/messages?conversation_id=", parents=[common])
    c.add_argument("conversation_id")

    sub.add_parser("homes", help="GET /v1/homes/me", parents=[common])

    c = sub.add_parser("home", help="GET /v1/homes/{id}", parents=[common])
    c.add_argument("home_id", nargs="?", default=None)

    c = sub.add_parser("request", help="raw METHOD PATH (discovery)", parents=[common])
    c.add_argument("method")
    c.add_argument("path")
    c.add_argument("--body", default=None, help="JSON object/array string")

    c = sub.add_parser(
        "search",
        help="POST bff /search/homes (GuestPoints by default)",
        parents=[common],
    )
    c.add_argument("--place", default="manhattan", help="manhattan | nyc | or any city name")
    c.add_argument("--location-id", dest="location_id", default=None)
    c.add_argument("--from", dest="start_on", default=None, help="YYYY-MM-DD")
    c.add_argument("--to", dest="end_on", default=None, help="YYYY-MM-DD checkout")
    c.add_argument("--adults", type=int, default=2)
    c.add_argument("--children", type=int, default=0)
    c.add_argument("--babies", type=int, default=0)
    c.add_argument(
        "--bedrooms",
        type=int,
        default=None,
        help="min bedrooms (omit unless the stay needs it; Manhattan 5-person was 3)",
    )
    c.add_argument("--limit", type=int, default=20)
    c.add_argument("--offset", type=int, default=0)
    c.add_argument(
        "--exchange",
        default="points",
        help="points (default, GuestPoints) | reciprocal | both",
    )
    c.add_argument(
        "--response-rate",
        dest="response_rate",
        action="store_true",
        default=True,
        help="filter response-rate-above-threshold (default on)",
    )
    c.add_argument(
        "--no-response-rate",
        dest="response_rate",
        action="store_false",
    )
    c.add_argument(
        "--verify",
        dest="verify",
        action="store_true",
        default=True,
        help="drop reciprocal-only calendars (default on when dates set)",
    )
    c.add_argument("--no-verify", dest="verify", action="store_false")
    c.add_argument(
        "--children-welcome",
        dest="children_welcome",
        action="store_true",
        default=False,
        help="force children-welcome amenity (also auto when --children>0)",
    )
    c.add_argument(
        "--no-children-welcome",
        dest="no_children_welcome",
        action="store_true",
        default=False,
    )
    c.add_argument(
        "--clip-manhattan",
        dest="clip_manhattan",
        action="store_true",
        default=False,
        help="drop Brooklyn/NJ/Queens leaks (auto when --place manhattan)",
    )

    c = sub.add_parser("calendar", help="GET /v1/homes/{id}/calendar", parents=[common])
    c.add_argument("home_id", nargs="?", default=None)

    c = sub.add_parser(
        "exchanges",
        help="GET /v1/exchanges/{conversationId}/get-exchanges",
        parents=[common],
    )
    c.add_argument("conversation_id")

    c = sub.add_parser("send", help="POST /v1/messages (write)", parents=[common])
    c.add_argument("conversation_id")
    c.add_argument("--text", required=True)

    c = sub.add_parser(
        "request-stay",
        help="POST bff /exchange/v3 new stay request (write)",
        parents=[common],
    )
    c.add_argument("--home", dest="home_id", required=True, help="listing id")
    c.add_argument("--host", dest="host_id", default=None, help="host user id (else GET home)")
    c.add_argument("--from", dest="start_on", required=True, help="YYYY-MM-DD check-in")
    c.add_argument("--to", dest="end_on", required=True, help="YYYY-MM-DD checkout")
    c.add_argument("--adults", type=int, default=2)
    c.add_argument("--children", type=int, default=0)
    c.add_argument("--babies", type=int, default=0)
    c.add_argument(
        "--exchange",
        default="points",
        help="points (WITH-GP, default) | reciprocal | reciprocal-with-gp",
    )
    c.add_argument("--text", required=True, help="first message (no email/links)")
    c.add_argument("--yes", action="store_true", help="required: actually send")
    c.add_argument(
        "--force",
        action="store_true",
        help="send even if verified_status != 1",
    )

    c = sub.add_parser(
        "approve", help="PATCH approve (write; conversation id)", parents=[common]
    )
    c.add_argument("conversation_id")
    c.add_argument("--yes", action="store_true")

    c = sub.add_parser("publish", help="PATCH /v1/homes/{id} status=5 (online)", parents=[common])
    c.add_argument("home_id")
    return p


def main() -> int:
    args = build_parser().parse_args()
    as_json = bool(args.json)
    try:
        if args.cmd == "me":
            return cmd_me(args, as_json)
        if args.cmd == "homes":
            return cmd_homes(args, as_json)
        if args.cmd == "home":
            return cmd_home(args, as_json)
        if args.cmd == "request":
            return cmd_request(args, as_json)
        if args.cmd == "search":
            return cmd_search(args, as_json)
        if args.cmd == "conversations":
            return cmd_conversations(args, as_json)
        if args.cmd == "conversation":
            return cmd_conversation(args, as_json)
        if args.cmd == "messages":
            return cmd_messages(args, as_json)
        if args.cmd == "calendar":
            return cmd_calendar(args, as_json)
        if args.cmd == "exchanges":
            return cmd_exchanges(args, as_json)
        if args.cmd == "send":
            return cmd_send(args, as_json)
        if args.cmd == "request-stay":
            return cmd_request_stay(args, as_json)
        if args.cmd == "approve":
            return cmd_approve(args, as_json)
        if args.cmd == "publish":
            return cmd_publish(args, as_json)
        raise RuntimeError(f"unknown command {args.cmd}")
    except Exception as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
