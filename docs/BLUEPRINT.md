# STARMEET TECHNICAL BLUEPRINT
# Version: 4.0 | Status: MVP DEPLOYED + EXPANSION

## PROJECT IDENTITY

**Product:** AI-powered social network for compatibility matching
**Core Tech:** Vedic astrology (16 vargas) + psychological profiling
**Business Goal:** Build verified talent database for venture fund ($1B+ horizon)
**MVP Target:** 6 weeks to production

---

## CURRENT STATE (as of 2025-12-01)

### What's DEPLOYED and WORKING

| Component | Status | Details |
|-----------|--------|---------|
| **GCP VM** | ✅ Running | e2-standard-4, 49GB disk, 8.6GB used |
| **PostgreSQL 15** | ✅ Healthy | `starmeet-db` container |
| **Redis 7** | ✅ Healthy | `starmeet-redis` container |
| **FastAPI** | ✅ Healthy | `/star-api/v1/calculate` works |
| **Next.js** | ✅ Running | `/join` route, calculator UI |
| **Nginx** | ✅ Running | SSL, routing configured |
| **Astro Engine** | ✅ Working | All 16 vargas, Raman/Lahiri |

### What's NOT YET Implemented

| Component | Status | Priority |
|-----------|--------|----------|
| **Supabase Auth** | ❌ Not deployed | Phase 3 |
| **Profile CRUD** | ❌ No endpoints | Phase 3 |
| **Social Features** | ❌ Not started | Phase 4-5 |

---

## ARCHITECTURE OVERVIEW (CURRENT)

```
                         CLOUDFLARE (CDN + SSL + DDoS)
                                    │
┌───────────────────────────────────┴───────────────────────────────────┐
│                        GCP VM (e2-standard-4)                          │
│                        8GB RAM / 4 vCPU / 49GB SSD                     │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                           NGINX                                   │ │
│  │  /              → redirect to /join                               │ │
│  │  /join          → Next.js (:3001)     [Calculator UI]             │ │
│  │  /star-api/     → FastAPI (:8000)     [Astro Engine]              │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   │
│  │  NEXT.JS   │   │  FASTAPI   │   │ POSTGRESQL │   │   REDIS    │   │
│  │   :3001    │   │   :8000    │   │   :5432    │   │   :6379    │   │
│  │            │   │            │   │            │   │            │   │
│  │ Calculator │   │ /v1/calc   │   │ starmeet   │   │ cache      │   │
│  │ UI (works) │   │ (works)    │   │ db         │   │            │   │
│  └────────────┘   └────────────┘   └────────────┘   └────────────┘   │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                    packages/astro_core/                         │   │
│  │                    engine.py - Digital Twin Generator           │   │
│  │                    (16 vargas, Raman/Lahiri, jyotishganit)      │   │
│  └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## TECHNOLOGY STACK

| Layer | Technology | Status |
|-------|------------|--------|
| **Frontend** | Next.js 14 (App Router) | ✅ Deployed |
| **API** | FastAPI (Python 3.11) | ✅ Deployed |
| **Database** | PostgreSQL 15 (Supabase Cloud) | ✅ Running |
| **Cache** | Redis 7 | ✅ Running |
| **Math** | jyotishganit + Swiss Ephemeris | ✅ Working |
| **Auth** | Supabase GoTrue | ✅ Deployed |
| **AI** | MiniMax M2 + pgvector | ⏳ Future |

---

## ASTRO ENGINE SPECIFICATION

### Core Library: jyotishganit

**Repository:** https://github.com/northtara/jyotishganit
**Version:** Latest (pip install)
**Backend:** Swiss Ephemeris (swisseph)

### Library Architecture

```
jyotishganit/
├── calculate_birth_chart()     # Main entry point
├── components/
│   ├── divisional_charts/      # ✅ ИСПОЛЬЗУЕМ (16 vargas)
│   │   ├── hora_from_long()           # D2
│   │   ├── drekkana_from_long()       # D3
│   │   ├── chaturtamsa_from_long()    # D4
│   │   ├── saptamsa_from_long()       # D7
│   │   ├── navamsa_from_long()        # D9
│   │   ├── dasamsa_from_long()        # D10
│   │   ├── dwadasamsa_from_long()     # D12
│   │   ├── shodasamsa_from_long()     # D16
│   │   ├── vimsamsa_from_long()       # D20
│   │   ├── chaturvimsamsa_from_long() # D24
│   │   ├── sapta_vimsamsa_from_long() # D27
│   │   ├── trimsamsa_from_long()      # D30
│   │   ├── khavedamsa_from_long()     # D40
│   │   ├── akshavedamsa_from_long()   # D45
│   │   └── shashtiamsa_from_long()    # D60
│   ├── dasha/                  # ⏳ TODO: Vimshottari Dasha
│   │   └── vimshottari_dasha()
│   ├── shadbala/               # ⏳ TODO: 6-fold strength
│   │   └── calculate_shadbala()
│   ├── ashtakavarga/           # ⏳ TODO: 8-point system
│   │   └── calculate_ashtakavarga()
│   └── panchanga/              # ⏳ TODO: Daily almanac
│       └── calculate_panchanga()
```

### Currently Implemented (engine.py)

| Feature | Status | Description |
|---------|--------|-------------|
| **16 Varga Charts** | ✅ Working | D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60 |
| **Ayanamsa Support** | ✅ Working | Lahiri (default), Raman (+1.43° delta) |
| **Planet Positions** | ✅ Working | 9 planets (Sun-Ketu) with abs/rel longitude |
| **House System** | ✅ Working | 12 houses with signs, lords |
| **Nakshatra** | ✅ Working | 27 nakshatras with pada (1-4) |
| **Dignity** | ✅ Working | Exalted/Moolatrikona/Own/Friend/Neutral/Enemy/Debilitated |
| **Aspects (Drishti)** | ✅ Working | Full planetary aspects (7th, Mars 4/8, Jupiter 5/9, Saturn 3/10) |
| **Conjunctions** | ✅ Working | Planets in same sign |
| **Lordships** | ✅ Working | Houses owned by each planet |

### Missing Features (TODO)

| Feature | Priority | Source | Description |
|---------|----------|--------|-------------|
| **D5 Panchamsha** | 🔴 HIGH | Manual formula | Children, creativity |
| **D6 Shashthamsha** | 🔴 HIGH | Manual formula | Health, enemies |
| **D8 Ashtamsha** | 🔴 HIGH | Manual formula | Longevity, obstacles |
| **D11 Rudramsha** | 🔴 HIGH | Manual formula | Wealth acquisition |
| **Vimshottari Dasha** | 🔴 HIGH | jyotishganit.dasha | Time periods (120 years cycle) |
| **Shadbala** | 🟡 MEDIUM | jyotishganit.shadbala | 6-fold planetary strength |
| **Ashtakavarga** | 🟡 MEDIUM | jyotishganit.ashtakavarga | 8-point system for predictions |
| **Panchanga** | 🟡 MEDIUM | jyotishganit.panchanga | Tithi, Yoga, Karana, Vaara |
| **is_retrograde** | 🟡 MEDIUM | swisseph | Currently always returns false |

### Missing Varga Formulas

#### D5 - Panchamsha (1/5 = 6° per division)
```
For each 6° segment (0-6, 6-12, 12-18, 18-24, 24-30):
- Odd signs (Aries, Gemini, Leo, etc.): Start from Aries
- Even signs (Taurus, Cancer, Virgo, etc.): Start from Sagittarius
Division 1: base_sign
Division 2: base_sign + 1
Division 3: base_sign + 2
Division 4: base_sign + 3
Division 5: base_sign + 4
```

#### D6 - Shashthamsha (1/6 = 5° per division)
```
For each 5° segment:
- Odd signs: Start from sign itself
- Even signs: Start from 7th sign
Division 1: base_sign
Division 2: base_sign + 1
... (cycle through 6 signs)
```

#### D8 - Ashtamsha (1/8 = 3.75° per division)
```
For each 3.75° segment:
- Movable signs (Aries, Cancer, Libra, Capricorn): Start from Aries
- Fixed signs (Taurus, Leo, Scorpio, Aquarius): Start from Sagittarius
- Dual signs (Gemini, Virgo, Sagittarius, Pisces): Start from Leo
```

#### D11 - Rudramsha (1/11 = 2.727° per division)
```
For each 2.727° segment:
- Odd signs: Start from Aries
- Even signs: Start from Scorpio
Cycle through 11 signs for each division
```

### Digital Twin JSON Structure

```json
{
  "meta": {
    "birth_datetime": "1977-10-25T06:28:00",
    "latitude": 61.7,
    "longitude": 30.7,
    "timezone_offset": 3.0,
    "ayanamsa": "Raman",
    "ayanamsa_delta": 1.43,
    "julian_day": 2443449.6444,
    "generated_at": "2025-12-01T..."
  },
  "vargas": {
    "D1": {
      "ascendant": {
        "sign_id": 7,
        "sign_name": "Libra",
        "degrees": 17.84
      },
      "planets": [
        {
          "name": "Sun",
          "sign_id": 7,
          "sign_name": "Libra",
          "absolute_degree": 188.12,
          "relative_degree": 8.12,
          "house_occupied": 1,
          "houses_owned": [11],
          "nakshatra": "Swati",
          "nakshatra_lord": "Rahu",
          "nakshatra_pada": 2,
          "sign_lord": "Venus",
          "dignity_state": "Debilitated",
          "aspects_giving_to": [7],
          "aspects_receiving_from": ["Saturn"],
          "conjunctions": ["Mercury"],
          "is_retrograde": false
        }
        // ... 8 more planets
      ],
      "houses": [
        {
          "house_number": 1,
          "sign_id": 7,
          "sign_name": "Libra",
          "lord": "Venus",
          "occupants": ["Sun", "Mercury"],
          "aspects_received": ["Saturn"]
        }
        // ... 11 more houses
      ]
    },
    "D2": { ... },
    "D9": { ... },
    // ... all 16 vargas
  },
  // FUTURE ADDITIONS:
  "dasha": {
    "current_mahadasha": "Moon",
    "current_antardasha": "Jupiter",
    "periods": [...]
  },
  "shadbala": {
    "Sun": { "total": 458.2, "sthana": 120, "dig": 45, ... },
    // ...
  },
  "ashtakavarga": {
    "Sun": { "D1": [4,5,3,2,...], "total": 48 },
    // ...
  },
  "panchanga": {
    "tithi": { "name": "Shukla Chaturthi", "lord": "Ganesh" },
    "nakshatra": { "name": "Swati", "pada": 2 },
    "yoga": { "name": "Siddhi", "meaning": "Success" },
    "karana": { "name": "Balava" },
    "vaara": { "name": "Tuesday", "lord": "Mars" }
  }
}
```

---

## API ENDPOINTS

### Currently Working

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/star-api/v1/calculate` | POST | Full D1-D60 calculation | ✅ Works |
| `/star-api/health` | GET | Health check | ✅ Works |
| `/star-api/docs` | GET | Swagger UI | ✅ Works |

### Request Format (calculate)
```json
{
  "date": "1977-10-25",
  "time": "06:28",
  "lat": 61.70,
  "lon": 30.69,
  "timezone": 3.0,
  "ayanamsa": "raman"  // or "lahiri"
}
```

### Response Format
```json
{
  "success": true,
  "detected_timezone": { ... },
  "digital_twin": {
    "meta": {
      "birth_datetime": "1977-10-25T06:28:00",
      "ayanamsa": "Raman",
      "ayanamsa_delta": 1.43,
      ...
    },
    "vargas": {
      "D1": { "ascendant": {...}, "planets": [...], "houses": [...] },
      "D2": { ... },
      ...
      "D60": { ... }
    }
  }
}
```

### TODO Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/star-api/v1/profiles` | GET | List all profiles |
| `/star-api/v1/profiles` | POST | Create new profile |
| `/star-api/v1/profiles/:id` | GET | Get profile by ID |
| `/star-api/v1/profiles/:id` | PUT | Update profile |
| `/star-api/v1/profiles/:id` | DELETE | Delete profile |

---

## DATABASE SCHEMA

### profiles (TO CREATE)
```sql
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,

    -- Birth Data
    birth_date DATE NOT NULL,
    birth_time TIME,
    birth_place TEXT,
    birth_latitude FLOAT,
    birth_longitude FLOAT,
    birth_timezone FLOAT,

    -- Ayanamsa
    ayanamsa TEXT DEFAULT 'raman',

    -- Calculated Chart (JSONB)
    digital_twin JSONB,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_profiles_created_at ON profiles(created_at DESC);
```

### Future Tables
- **compatibility_cache**: Pre-calculated compatibility scores
- **users**: Supabase auth users (when auth is added)

---

## PROJECT STRUCTURE

```
StarMeet-platform/
├── docs/
│   ├── CLAUDE.md          # Agent constitution
│   ├── BLUEPRINT.md       # This file
│   └── PROGRESS.md        # Status tracking
├── backend/               # ✅ WORKING
│   ├── app/
│   │   ├── main.py        # FastAPI app
│   │   ├── routers/
│   │   │   └── astro.py   # /v1/calculate endpoint
│   │   └── models/
│   ├── requirements.txt
│   └── Dockerfile
├── wizard/                # ✅ WORKING
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   └── AstroCalculator.tsx
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
├── packages/
│   └── astro_core/        # ✅ WORKING
│       ├── __init__.py
│       └── engine.py      # Digital Twin generator
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── init-astro-db.sql
└── .env
```

---

## DOCKER COMPOSE (Current MVP)

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: starmeet-db
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: starmeet
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d starmeet"]

  redis:
    image: redis:7-alpine
    container_name: starmeet-redis
    command: redis-server --appendonly yes --maxmemory 256mb

  fastapi:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: starmeet-api
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/starmeet
      REDIS_URL: redis://redis:6379/0
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      db: { condition: service_healthy }

  nextjs:
    build: ./wizard
    container_name: starmeet-wizard
    environment:
      NEXT_PUBLIC_API_URL: ${SITE_URL}/star-api
    ports:
      - "127.0.0.1:3001:3001"

  nginx:
    image: nginx:alpine
    container_name: starmeet-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro

volumes:
  postgres-data:
  redis-data:
```

---

## NGINX CONFIG (Current)

```nginx
upstream nextjs { server starmeet-wizard:3001; }
upstream fastapi { server starmeet-api:8000; }

server {
    listen 443 ssl http2;
    server_name star-meet.com;

    ssl_certificate /etc/letsencrypt/live/star-meet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/star-meet.com/privkey.pem;

    # Root redirect to /join
    location = / {
        return 302 /join;
    }

    # FastAPI (Astro Engine)
    location /star-api/ {
        proxy_pass http://fastapi/;
        proxy_read_timeout 120s;
    }

    # Next.js (Calculator UI)
    location /join {
        proxy_pass http://nextjs;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## IMPLEMENTATION ROADMAP

| Phase | Week | Deliverable | Status |
|-------|------|-------------|--------|
| **1. Infrastructure** | 1 | GCP + Docker + Nginx + SSL | ✅ Complete |
| **2. Astro Engine** | 2 | FastAPI + 16 vargas calculation | ✅ Complete |
| **3. Profiles** | 3 | DB schema + CRUD endpoints + UI | 🔄 In Progress |
| **4. Auth** | 3 | Supabase GoTrue integration | ⏳ Pending |
| **5. Social Core** | 4 | Matching algorithm | ⏳ Pending |
| **6. Polish** | 5-6 | UI improvements, performance | ⏳ Pending |

---

## COMMANDS REFERENCE

```bash
# GCP SSH Access
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="<cmd>"

# Docker Operations (on server)
docker compose up -d
docker compose ps
docker compose logs -f starmeet-api
docker compose down

# Rebuild single service
docker compose up -d --build fastapi

# Database shell
docker exec -it starmeet-db psql -U postgres -d starmeet

# API Test
curl -X POST https://star-meet.com/star-api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"date":"1977-10-25","time":"06:28","lat":61.70,"lon":30.69,"timezone":3.0,"ayanamsa":"raman"}'
```

---

## KEY URLS

| URL | Purpose |
|-----|---------|
| https://star-meet.com/join | Calculator UI |
| https://star-meet.com/star-api/health | Health check |
| https://star-meet.com/star-api/docs | Swagger UI |
| https://star-meet.com/star-api/v1/calculate | Calculate endpoint |

---

**END OF BLUEPRINT**
