# STARMEET TECHNICAL BLUEPRINT
# Version: 6.0 | Status: ASTRO BRAIN - STAGES 1-10 COMPLETE
# Updated: 2025-12-02

---

## PROJECT IDENTITY

**Product:** AI-powered social network for compatibility matching
**Core Tech:** Vedic astrology (20 vargas) + Python calculator (12 stages) + LLM interpretation
**Business Goal:** Build verified talent database for venture fund ($1B+ horizon)
**Current Phase:** Astro Brain implementation (Stages 1-10 complete)

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              STARMEET ASTRO BRAIN                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  User Birth │───►│ jyotishganit│───►│  DIGITAL    │───►│   PYTHON    │      │
│  │    Data     │    │   library   │    │    TWIN     │    │ CALCULATOR  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    │ (12 stages) │      │
│                                                            └──────┬──────┘      │
│                                                                   │             │
│                                                                   ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────┐     │
│  │ personality │◄───│  Minimax M2 │◄───│       CalculatorOutput          │     │
│  │   _report   │    │    (LLM)    │    │  (structured data for LLM)      │     │
│  └──────┬──────┘    └─────────────┘    └─────────────────────────────────┘     │
│         │                                                                       │
│         ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐       │
│  │                         DUAL OUTPUT                                  │       │
│  ├─────────────────────────────┬───────────────────────────────────────┤       │
│  │       PUBLIC OUTPUT         │        PRIVATE OUTPUT                  │       │
│  │  (inspiring user report)    │  (numeric scores for investment fund) │       │
│  └─────────────────────────────┴───────────────────────────────────────┘       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION STATUS

### 12-Stage Calculator Progress

| Stage | Name | Vargas | Status | Tests |
|-------|------|--------|--------|-------|
| 1 | Core Personality | D1 | ✅ Complete | ✅ Passing |
| 2 | Soul Blueprint | D9 | ✅ Complete | ✅ Passing |
| 3 | Yogas & Combinations | D1, D9 | ✅ Complete | ✅ Passing |
| 4 | Wealth Potential | D1, D2, D11 | ✅ Complete | ✅ Passing |
| 5 | Skills & Intelligence | D1, D24 | ✅ Complete | ✅ Passing |
| 6 | Career & Ambition | D1, D10 | ✅ Complete | ✅ Passing |
| 7 | Creativity & Expression | D1, D5 | ✅ Complete | ✅ Passing |
| 8 | Gains & Networking | D1, D11 | ✅ Complete | ✅ Passing |
| 9 | Karmic Depth | D30, D60 | ✅ Complete | ✅ Passing |
| 10 | Timing Analysis | Dasha + Ashtakavarga | ✅ Complete | ✅ Passing |
| 11 | Nakshatra Deep Dive | Nakshatras | ⏳ Pending | — |
| 12 | Jaimini System | Chara Karakas | ⏳ Pending | — |

### Component Status

| Component | Status | Details |
|-----------|--------|---------|
| **GCP VM** | ✅ Running | e2-standard-4, 49GB disk |
| **PostgreSQL 15** | ✅ Healthy | Supabase Cloud |
| **Redis 7** | ✅ Healthy | Docker container |
| **FastAPI** | ✅ Healthy | `/star-api/v1/calculate` |
| **Next.js 14** | ✅ Running | Full onboarding wizard |
| **Supabase Auth** | ✅ Working | Registration/login |
| **Astro Engine** | ✅ Working | 20 vargas, Dasha, Karakas |
| **Astro Brain** | ✅ Stages 1-10 | All tests passing |
| **LLM Integration** | ⏳ Pending | Minimax M2 |

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
| **Calculator** | Python Astro Brain | ✅ Stages 1-10 |
| **AI/LLM** | MiniMax M2 | ⏳ Phase 5 |

---

## FILE STRUCTURE (ACTUAL)

```
backend/app/astro/
├── __init__.py
├── calculator.py              # ✅ Main AstroBrain class
├── models/
│   ├── __init__.py
│   ├── types.py               # ✅ Planet, Zodiac, Dignity enums
│   └── output.py              # ✅ CalculatorOutput dataclass
├── stages/
│   ├── __init__.py
│   ├── stage_01_core.py       # ✅ Core Personality (D1)
│   ├── stage_02_soul.py       # ✅ Soul Blueprint (D9)
│   ├── stage_03_yogas.py      # ✅ Yoga detection
│   ├── stage_04_wealth.py     # ✅ Wealth analysis
│   ├── stage_05_skills.py     # ✅ Skills & Intelligence
│   ├── stage_06_career.py     # ✅ Career analysis
│   ├── stage_07_creativity.py # ✅ Creativity
│   ├── stage_08_gains.py      # ✅ Gains & Networking
│   ├── stage_09_karmic.py     # ✅ Karmic Depth (D30, D60, Doshas)
│   └── stage_10_timing.py     # ✅ Timing (Dasha, Ashtakavarga)
├── strength/
│   ├── __init__.py
│   └── shadbala.py            # ✅ 6-fold strength
├── formulas/
│   ├── __init__.py
│   └── dignities.py           # ✅ Dignity calculations
├── reference/
│   ├── __init__.py
│   ├── dignities.py           # ✅ Exaltation, Moolatrikona tables
│   ├── yogas.py               # ✅ Yoga definitions
│   └── doshas.py              # ✅ Dosha catalog (8 types)
├── llm/
│   ├── __init__.py
│   ├── prompts.py             # ⏳ System prompts
│   └── client.py              # ⏳ Minimax M2 client
└── tests/
    ├── __init__.py
    ├── fixtures/
    │   └── digital_twin_fixture.json
    ├── test_stages_1_2.py     # ✅ Passing
    ├── test_stage_3.py        # ✅ Passing
    ├── test_stages_4_8.py     # ✅ Passing
    └── test_stages_9_10.py    # ✅ Passing
```

---

## STAGE 9: KARMIC DEPTH

### Dosha Catalog (8 types)

| Dosha | Description | Severity |
|-------|-------------|----------|
| Mangal | Mars in 1,2,4,7,8,12 from Lagna/Moon/Venus | 7.0 |
| Kala Sarpa | All planets between Rahu-Ketu | 8.0 |
| Guru Chandal | Jupiter conjunct Rahu | 6.5 |
| Pitru | Sun afflicted by Saturn/Rahu/Ketu | 6.0 |
| Grahan | Sun/Moon conjunct Rahu/Ketu | 7.5 |
| Shrapit | Saturn conjunct Rahu | 8.5 |
| Kemadrum | No planets 2nd/12th from Moon | 5.0 |
| Daridra | 11th lord in dusthana | 6.0 |

### Output Enums

```python
class KarmicCeilingTier(str, Enum):
    UNLIMITED = "Unlimited"
    VERY_HIGH = "VeryHigh"
    HIGH = "High"
    MODERATE = "Moderate"
    LIMITED = "Limited"
    CONSTRAINED = "Constrained"
    BLOCKED = "Blocked"

class RiskCategory(str, Enum):
    VERY_LOW = "VeryLow"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"
```

---

## STAGE 10: TIMING

### Vimshottari Dasha Periods

```python
DASHA_PERIODS = {
    Planet.KETU: 7,
    Planet.VENUS: 20,
    Planet.SUN: 6,
    Planet.MOON: 10,
    Planet.MARS: 7,
    Planet.RAHU: 18,
    Planet.JUPITER: 16,
    Planet.SATURN: 19,
    Planet.MERCURY: 17
}  # Total: 120 years

DASHA_SEQUENCE = [
    Planet.KETU, Planet.VENUS, Planet.SUN, Planet.MOON,
    Planet.MARS, Planet.RAHU, Planet.JUPITER, Planet.SATURN, Planet.MERCURY
]
```

### Timing Recommendations

```python
class TimingRecommendation(str, Enum):
    INVEST_NOW = "InvestNow"
    FAVORABLE_TIMING = "FavorableTiming"
    WAIT_FOR_BETTER = "WaitForBetter"
    PROCEED_CAUTION = "ProceedCaution"
    DELAY_INVESTMENT = "DelayInvestment"
```

---

## DIGNITIES REFERENCE DATA

### Exaltation & Debilitation

```python
EXALTATION = {
    Planet.SUN: Zodiac.ARIES,
    Planet.MOON: Zodiac.TAURUS,
    Planet.MARS: Zodiac.CAPRICORN,
    Planet.MERCURY: Zodiac.VIRGO,
    Planet.JUPITER: Zodiac.CANCER,
    Planet.VENUS: Zodiac.PISCES,
    Planet.SATURN: Zodiac.LIBRA,
}

DEBILITATION = {
    Planet.SUN: Zodiac.LIBRA,
    Planet.MOON: Zodiac.SCORPIO,
    Planet.MARS: Zodiac.CANCER,
    Planet.MERCURY: Zodiac.PISCES,
    Planet.JUPITER: Zodiac.CAPRICORN,
    Planet.VENUS: Zodiac.VIRGO,
    Planet.SATURN: Zodiac.ARIES,
}
```

### Natural Friendships

```python
NATURAL_FRIENDS = {
    Planet.SUN: [Planet.MOON, Planet.MARS, Planet.JUPITER],
    Planet.MOON: [Planet.SUN, Planet.MERCURY],
    Planet.MARS: [Planet.SUN, Planet.MOON, Planet.JUPITER],
    Planet.MERCURY: [Planet.SUN, Planet.VENUS],
    Planet.JUPITER: [Planet.SUN, Planet.MOON, Planet.MARS],
    Planet.VENUS: [Planet.MERCURY, Planet.SATURN],
    Planet.SATURN: [Planet.MERCURY, Planet.VENUS]
}
```

---

## DATABASE SCHEMA

### Existing Tables (Supabase Cloud)

```sql
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    username TEXT UNIQUE,
    birth_date DATE NOT NULL,
    birth_time TIME,
    birth_city TEXT,
    birth_lat FLOAT,
    birth_lon FLOAT,
    birth_tz FLOAT,
    ayanamsa TEXT DEFAULT 'raman',
    is_primary BOOLEAN DEFAULT false,
    digital_twin JSONB,
    psych_scores JSONB,
    interests JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Future Tables (Phase 5)

```sql
-- Calculator output storage
CREATE TABLE public.calculator_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    output JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Internal talent assessments
CREATE TABLE internal.talent_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id),
    talent_score FLOAT NOT NULL,
    leadership_score FLOAT,
    creativity_score FLOAT,
    watchlist_tier TEXT,
    calculator_output_id UUID REFERENCES public.calculator_outputs(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API ENDPOINTS

### Currently Working

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/star-api/v1/calculate` | POST | Full D1-D60 calculation | ✅ |
| `/star-api/v1/save` | POST | Save profile with digital_twin | ✅ |
| `/star-api/v1/profiles` | GET | Get user profiles | ✅ |
| `/star-api/health` | GET | Health check | ✅ |

### New Endpoints (Phase 5)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/star-api/v1/analyze` | POST | Run 12-stage calculator |
| `/star-api/v1/report/{id}` | GET | Get personality report |
| `/star-api/v1/report/{id}` | POST | Generate new report via LLM |

---

## IMPLEMENTATION PHASES

### Completed

| Phase | Content | Status |
|-------|---------|--------|
| 1 | Foundation (types, models, Stage 1-2) | ✅ Complete |
| 2 | Core Stage 3 (Yogas) | ✅ Complete |
| 3 | Varga Stages 4-8 | ✅ Complete |
| 4 | Karmic Depth & Timing (Stages 9-10) | ✅ Complete |

### Pending

| Phase | Content | Priority |
|-------|---------|----------|
| 5 | LLM Integration (Minimax M2) | HIGH |
| 6 | Admin Panel | MEDIUM |
| 7 | Social Features | FUTURE |

---

## GOLDEN CODE (DO NOT REWRITE)

| File | Purpose | Status |
|------|---------|--------|
| `packages/astro_core/engine.py` | Digital Twin generator | ✅ WORKING |
| `backend/app/routers/astro.py` | API endpoints | ✅ WORKING |
| `wizard/src/components/AstroCalculator.tsx` | UI component | ✅ WORKING |

---

## COMMANDS REFERENCE

```bash
# Run tests
cd backend
PYTHONPATH=../packages .venv/bin/pytest app/astro/tests/ -v

# Local development
PYTHONPATH=../packages uvicorn app.main:app --reload --port 8000

# Quick deploy
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c \
  --command="cd ~/StarMeet-platform && git pull && docker compose build --no-cache starmeet-api && docker compose up -d"
```

---

## KEY URLS

| URL | Purpose |
|-----|---------|
| https://star-meet.com/join | Onboarding wizard |
| https://star-meet.com/dashboard | User dashboard |
| https://star-meet.com/star-api/health | Health check |
| https://star-meet.com/star-api/docs | Swagger UI |

---

**END OF BLUEPRINT v6.0**
