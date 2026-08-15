# Hospitable Public API v2 — endpoint reference

Source: OpenAPI 3.1 (`openapi-v2.yaml`), title **Hospitable Public API** version **2.0**.  
Base: `https://public.api.hospitable.com/v2`  
Security: HTTP Bearer (`Bearer-Authorization`).

---

## GET /properties

**Summary:** List properties for the account.

**Includes:** `user`, `listings` (needs `listing:read`), `details`, `bookings`

| Param | In | Required | Notes |
|-------|-----|----------|--------|
| `include` | query | no | Relationships to expand |
| `page` | query | no | default 1 |
| `per_page` | query | no | 1–100, default 10 |

**200:** `{ data: Property[], meta: PaginationMeta }`

---

## GET /properties/search

**Summary:** Search properties with availability + pricing.

**Constraints:**

- Up to **3 years** into the future
- Max stay window **90 days**
- Requires customer **Self-hosted Direct** site with properties scoped

**Includes:** `listings` (`listing:read`), `details`

| Param | In | Required | Notes |
|-------|-----|----------|--------|
| `include` | query | no | |
| `start_date` | query | **yes** | date |
| `end_date` | query | **yes** | date |
| `adults` | query | **yes** | integer |
| `children` | query | no | |
| `infants` | query | no | |
| `pets` | query | no | |
| `location` | query | no | `{ latitude, longitude }` |

**200:** `{ data: [{ property, pricing, availability, … }] }` (see OpenAPI for pricing daily breakdown)

---

## GET /properties/{uuid}

**Summary:** One property by UUID.

**Includes:** `user`, `listings` (`listing:read`), `details`, `bookings`

| Param | In | Required |
|-------|-----|----------|
| `uuid` | path | yes |
| `include` | query | no |

**200:** `{ data: Property }`

### Property schema (core fields)

| Field | Notes |
|-------|--------|
| `id` | UUID |
| `name` / `public_name` | Internal vs public |
| `picture` | URI |
| `address` | number, street, city, state, country, postcode, coordinates, display |
| `timezone` | e.g. `+0200` |
| `listed` | boolean |
| `amenities` | string[] |
| `description` / `summary` | |
| `check-in` / `check-out` | default times (note **hyphen** keys) |
| `currency` | e.g. USD / EUR |
| `capacity` | max, bedrooms, beds, bathrooms |
| `room_details` | `[{ type, quantity }]` |
| `house_rules` | pets_allowed, smoking_allowed, events_allowed |
| `listings` | `[{ platform, platform_id, platform_name?, platform_email? }]` |
| `ical_imports` | only when `listings` included |
| `tags` | string[] |
| `property_type` / `room_type` | |
| `calendar_restricted` | if true, **cannot** PUT calendar |
| `parent_child` | parent/child multi-unit relationship |

---

## GET /properties/{uuid}/calendar

**Scopes:** `property:read`, `calendar:read`

| Param | In | Required |
|-------|-----|----------|
| `uuid` | path | yes |
| `start_date` | query | no (date) |
| `end_date` | query | no (date) |

**200:**

```json
{
  "data": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "days": [ /* CalendarDay */ ]
  }
}
```

### CalendarDay

| Field | Notes |
|-------|--------|
| `date` | YYYY-MM-DD |
| `day` | e.g. SUNDAY |
| `min_stay` | integer |
| `status.reason` | `RESERVED` \| `AVAILABLE` \| `BLOCKED` |
| `status.source_type` | USER, VENDOR, PLATFORM, AVAILABILITY_WINDOW, TURNOVER_DAY, ADVANCED_NOTICE, UPSELL, RESERVATION |
| `status.source` | string |
| `status.available` | boolean |
| `price.amount` | integer minor units |
| `price.currency` / `price.formatted` | |
| `closed_for_checkin` / `closed_for_checkout` | boolean |

---

## PUT /properties/{uuid}/calendar

**Scopes:** `property:read`, `calendar:write`  
**Rate limit:** 1000 requests/minute  
**Horizon:** up to **1,095 days (3 years)** future  
**Body limit:** up to **60** date objects (OpenAPI `maxProperties` / community API notes)

```json
{
  "dates": [
    {
      "date": "2024-03-15",
      "price": { "amount": 15000 },
      "available": true,
      "min_stay": 2,
      "closed_for_checkin": false,
      "closed_for_checkout": false
    }
  ]
}
```

**202:** `{ "status": "accepted" }`

Fails for properties with `calendar_restricted: true`.

---

## GET /reservations

**Summary:** List reservations (core of R2 occupancy + revenue).

**Includes:**

| Include | Scope |
|---------|--------|
| `guest` | (default-friendly) |
| `user` | |
| `financials` | **`financials:read`** |
| `listings` | `listing:read` |
| `properties` | `property:read` |
| `review` | `reviews:read` |

**Default date behavior:** if none of `start_date`, `end_date`, `date_query` provided → reservations with **check-in in the next ~2 weeks**.

| Param | In | Required | Notes |
|-------|-----|----------|--------|
| `properties[]` | query | **yes** | Property UUIDs |
| `start_date` | query | no | date — bounds depend on `date_query` |
| `end_date` | query | no | date |
| `include` | query | no | e.g. `financials,guest,properties,listings` |
| `date_query` | query | no | `checkin` (default) or `checkout` |
| `platform_id` | query | no | exact reservation code |
| `conversation_id` | query | no | exact conversation UUID |
| `last_message_at` | query | no | date-time — last message after |
| `page` | query | no | default 1 |
| `per_page` | query | no | 1–100, default 10 |

**200:** `{ data: Reservation[], meta: PaginationMeta }`

### Reservation schema (core)

| Field | Notes |
|-------|--------|
| `id` | UUID |
| `conversation_id` | UUID |
| `platform` | `airbnb` \| `homeaway` \| `booking` \| `direct` \| `manual` |
| `platform_id` | reservation / confirmation code |
| `booking_date` | date-time |
| `arrival_date` / `departure_date` | date (not exact times) |
| `nights` | integer |
| `check_in` / `check_out` | date-time (exact) |
| `last_message_at` | date-time |
| `status` | string — **deprecated** |
| `reservation_status.current` | see below |
| `reservation_status.history` | status + `changed_at` |
| `status_history` | deprecated |
| `guests` | total, adult_count, child_count, infant_count, pet_count |
| `issue_alert` | e.g. guest issue string |
| `stay_type` | `guest_stay` \| `owner_stay` |

**Included when requested:** `guest`, `properties`, `listings`, `financials`, `review`, `user` (shapes not fully expanded in OpenAPI schemas — observe live JSON).

### ReservationStatus

**category:** `request` | `accepted` | `cancelled` | `not accepted` | `unknown` | `checkpoint`

**sub_category:** `pending verification` | `awaiting approval` | `request to book` | `request for payment` | `declined` | `withdrawn` | `expired` | `checkpoint` | `voided`

### Financials (include; CleaningButton definition)

OpenAPI documents `FinancialV2` as `{ amount: int, formatted: string }` building blocks.  
Live `include=financials` (used by R2) has historically returned a **host/guest breakdown**, e.g.:

```text
financials.host.accommodation.amount   # cents
financials.host.host_fees[]            # { label, amount }
financials.host.guest_fees[]           # cleaning fee often here
financials.guest.fees[]                # fallback for cleaning line
```

**R2 net revenue cents** = accommodation + sum(host_fees).  
**Does not include** guest cleaning fees or platform guest charges.

Single-reservation also allows **`financialsV2`** (`financials:read`).

---

## GET /reservations/{uuid}

**Includes:** `guest`, `user`, `financials`, **`financialsV2`**, `listings`, `properties`  
(same scope rules as list)

| Param | In | Required |
|-------|-----|----------|
| `uuid` | path | yes |
| `include` | query | no |

**200:** `{ data: Reservation }`

---

## GET /reservations/{uuid}/messages

**Scope:** `message:read`

**200:** `{ data: Message[] }`

### Message fields

| Field | Notes |
|-------|--------|
| `platform` / `platform_id` | channel ids |
| `conversation_id` / `reservation_id` | |
| `content_type` | e.g. text/plain |
| `body` | text |
| `attachments` | `[{ type: image, url }]` |
| `sender_type` | host / guest |
| `sender_role` | host, co-host, teammate, … |
| `sender` | first_name, full_name, locale, pictures |
| `user` | id, email, name |
| `created_at` | |
| `source` | `public_api` \| `platform` \| `AI` \| `automated` \| `hospitable` |
| `integration` | partner name (PAT only) |
| `sent_reference_id` | correlates with POST send |

---

## POST /reservations/{uuid}/messages

**Scope:** `message:write` — **request from team-platform@hospitable.com**  
**Rate limits:** 2/min per reservation; 50 messages / 5 minutes total

```json
{
  "body": "Hello! Check-in is at 3pm.\nParking behind the building.",
  "images": ["https://example.com/photo.jpg"]
}
```

| Field | Rules |
|-------|--------|
| `body` | required; **no HTML**; `\n` for line breaks |
| `images` | optional; max **3**; max **5MB** each; URI |

**202:** `{ data: { sent_reference_id } }`

---

## GET /properties/{uuid}/reviews

**Scope:** `reviews:read`  
**Sources:** Airbnb + Direct  
**Includes:** `guest`, `reservations`

| Param | In | Required | Notes |
|-------|-----|----------|--------|
| `uuid` | path | yes | property UUID |
| `page` | query | no | default 1 |
| `per_page` | query | no | 1–**50**, default 10 |
| `include` | query | no | e.g. `guest` |

### Review schema

| Field | Notes |
|-------|--------|
| `id` | UUID |
| `platform` | `airbnb` \| `direct` |
| `public.rating` | 1–5 |
| `public.review` / `public.response` | text |
| `private.feedback` | private text |
| `private.detailed_ratings` | cleanliness, communication, location, checkin, accuracy, value |
| `guest` | first_name, last_name, language (when included) |
| `can_respond` | boolean (when present) |

---

## POST /reviews/{uuid}/respond

**Scope:** `reviews:write`

```json
{ "response": "Thank you for staying with us!" }
```

**200:** `{ data: Review }`  
**403:** already responded, or outside response window

---

## GET /user

Authenticated user + billing address fields:

`id`, `email`, `name`, `business`, `company`, `vat`, `tax_id`,  
`street_line1`, `street_line2`, `postal_code`, `city`, `region`, `country`

---

## PaginationMeta

Typical Laravel-style: `current_page`, `from`, `last_page`, `path`, `per_page`, `to`, `total` (see OpenAPI).

---

## Webhooks (documented events)

| Event action | Data schema |
|--------------|-------------|
| `reservation.created` | Reservation |
| `reservation.updated` | Reservation |
| `property.updated` / `property.merged` | Property |
| `message.created` | Message |
| `review.created` | Review |

Envelope: `id`, `action`, `data`, `created`, `version`.

---

## Error schema

```json
{
  "status_code": 400,
  "reason_phrase": "…",
  "message": "The given data was invalid."
}
```

---

## CleaningButton Pine map (quick)

```
20904545 → c899481f-2e5b-402d-80c4-3167fd824d96  #1B
20150380 → 114663c5-0709-4eff-a868-fa9ebd6ed42d  #2
24259977 → 60fc0321-c8be-46f4-8edd-8f5cd2c6c7bd  #3
```

Always pass these as `properties[]` for list reservations used by R2.
