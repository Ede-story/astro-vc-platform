# CLAUDE.md — StarMeet Agent Constitution

**Version:** 8.0 (Astro Brain)
**Updated:** 2025-12-02
**Language:** Think in English, report in Russian

---

## 1. PROJECT IDENTITY

**StarMeet** — AI-powered social network for compatibility matching.
**Core:** Vedic astrology (20 vargas) + Python calculator (12 stages) + LLM interpretation.
**Goal:** Build verified talent database for venture fund.

**Current State:**
- ✅ Digital Twin Generator (20 vargas, Vimshottari Dasha, Chara Karakas)
- ✅ Astro Brain Calculator: Stages 1-10 COMPLETE
- ✅ Next.js frontend with onboarding wizard
- ✅ FastAPI backend deployed
- ✅ Supabase Cloud (Auth + Database)
- ⏳ Stages 11-12 (Nakshatra, Jaimini) - pending
- ⏳ LLM Integration - pending

---

## 2. ASTRO BRAIN STATUS

### Completed Stages (1-10)

| Stage | Name | File | Status |
|-------|------|------|--------|
| 1 | Core Personality | `stage_01_core.py` | ✅ |
| 2 | Soul Blueprint | `stage_02_soul.py` | ✅ |
| 3 | Yogas | `stage_03_yogas.py` | ✅ |
| 4 | Wealth | `stage_04_wealth.py` | ✅ |
| 5 | Skills | `stage_05_skills.py` | ✅ |
| 6 | Career | `stage_06_career.py` | ✅ |
| 7 | Creativity | `stage_07_creativity.py` | ✅ |
| 8 | Gains | `stage_08_gains.py` | ✅ |
| 9 | Karmic Depth | `stage_09_karmic.py` | ✅ |
| 10 | Timing | `stage_10_timing.py` | ✅ |

### Pending Stages (11-12)

| Stage | Name | Content |
|-------|------|---------|
| 11 | Nakshatra Deep Dive | Nakshatra personality, compatibility |
| 12 | Jaimini System | Chara Karakas analysis |

### Implementation Phases

| Phase | Content | Status |
|-------|---------|--------|
| 1 | Foundation (types, models, Stage 1-2) | ✅ Complete |
| 2 | Core Stage 3 (Yogas) | ✅ Complete |
| 3 | Varga Stages 4-8 (Wealth, Skills, Career, Creativity, Profit) | ✅ Complete |
| 4 | Karmic Depth & Timing (Stages 9-10) | ✅ Complete |
| 5 | LLM Integration | ⏳ Pending |
| 6 | Admin Panel | ⏳ Pending |

---

## 3. DOCUMENTATION MAP

| Document | Purpose | Max Lines |
|----------|---------|-----------|
| `CLAUDE.md` | Agent rules, current status | 500 |
| `BLUEPRINT.md` | Architecture, schemas, reference | ~800 |
| `PROGRESS.md` | Daily log, decisions, metrics | ~300 |

**Rule:** Keep docs synchronized after significant work.

---

## 4. CORE RULES

### 4.1 Language Protocol
- **Code & Comments:** English
- **Progress Reports:** Русский
- **Commit Messages:** English (conventional commits)

### 4.2 Integrity
- **NO HALLUCINATIONS:** If unsure, STOP and ask
- **NO HACKS:** No temporary workarounds
- **VERIFY:** Test every change before reporting

### 4.3 Autonomous Operation
- Execute tasks without waiting for approval on minor decisions
- Make architectural decisions within BLUEPRINT constraints
- Report blockers immediately

---

## 5. PROJECT STRUCTURE

```
StarMeet-platform/
├── docs/
│   ├── CLAUDE.md          # This file
│   ├── BLUEPRINT.md       # Architecture
│   └── PROGRESS.md        # Status tracking
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/astro.py
│   │   └── astro/              # ✅ ASTRO BRAIN
│   │       ├── calculator.py   # Main AstroBrain class
│   │       ├── models/
│   │       │   ├── types.py    # Planet, Zodiac, Dignity enums
│   │       │   └── output.py   # CalculatorOutput dataclass
│   │       ├── stages/
│   │       │   ├── stage_01_core.py     # ✅
│   │       │   ├── stage_02_soul.py     # ✅
│   │       │   ├── stage_03_yogas.py    # ✅
│   │       │   ├── stage_04_wealth.py   # ✅
│   │       │   ├── stage_05_skills.py   # ✅
│   │       │   ├── stage_06_career.py   # ✅
│   │       │   ├── stage_07_creativity.py # ✅
│   │       │   ├── stage_08_gains.py    # ✅
│   │       │   ├── stage_09_karmic.py   # ✅
│   │       │   └── stage_10_timing.py   # ✅
│   │       ├── strength/
│   │       │   └── shadbala.py
│   │       ├── formulas/
│   │       │   └── dignities.py
│   │       ├── reference/
│   │       │   ├── dignities.py
│   │       │   ├── yogas.py
│   │       │   └── doshas.py   # ✅ Dosha catalog
│   │       └── tests/
│   │           ├── fixtures/
│   │           ├── test_stages_1_2.py    # ✅ Passing
│   │           ├── test_stage_3.py       # ✅ Passing
│   │           ├── test_stages_4_8.py    # ✅ Passing
│   │           └── test_stages_9_10.py   # ✅ Passing
│   └── requirements.txt
├── wizard/                # Next.js frontend
│   └── src/
│       ├── app/
│       ├── components/
│       └── lib/
└── packages/
    └── astro_core/        # jyotishganit wrapper
        └── engine.py      # Digital Twin generator
```

---

## 6. KEY TECHNICAL PATTERNS

### 6.1 Planet Object Handling
Planet data can be dict or dataclass. Use helper:
```python
def _get_planet_attr(planet: Any, key: str, default: Any = None) -> Any:
    if hasattr(planet, 'get'):
        return planet.get(key, default)
    return getattr(planet, key, default)
```

### 6.2 Stage Constructor Pattern
Optional parameters with defaults:
```python
def __init__(
    self,
    digital_twin: Dict[str, Any],
    d1_planets: List[Dict[str, Any]],
    optional_param: Optional[Dict] = None
):
    self.optional_param = optional_param or {}
```

### 6.3 Test Running
```bash
cd backend
PYTHONPATH=../packages .venv/bin/pytest app/astro/tests/ -v
```

---

## 7. STAGE 9-10 REFERENCE

### Stage 9: Karmic Depth
- **D30 (Trimshamsha):** Misfortunes, hidden karma
- **D60 (Shashtiamsha):** Past life karma
- **Doshas:** Mangal, Kala Sarpa, Guru Chandal, Pitru, Grahan, Shrapit, Kemadrum, Daridra
- **Output:** `KarmicCeilingTier`, `RiskCategory`, `risk_severity_index`

### Stage 10: Timing
- **Vimshottari Dasha:** 120-year cycle, 9 planets
- **Ashtakavarga:** 8-fold strength system
- **Output:** `DashaRoadmap`, `TimingRecommendation`, `is_golden_period`

### Dasha Periods (years)
```
Ketu:7, Venus:20, Sun:6, Moon:10, Mars:7, Rahu:18, Jupiter:16, Saturn:19, Mercury:17
```

---

## 8. SUPABASE CLOUD

**Project ID:** `lhirxjxwdjlyyztmeceh`
**Region:** `eu-central-1`

**Session Pooler:**
```
postgresql://postgres.lhirxjxwdjlyyztmeceh:0J7QYRgAfoL82vdS@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
```

**Dashboard:** https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh

---

## 9. INFRASTRUCTURE & DEPLOYMENT

### 9.1 GCP Projects

| Project | Purpose |
|---------|---------|
| `rosy-stronghold-467817-k6` | VM, Compute, Static IP |
| `edestory-platform` | Cloud DNS (star-meet.com zone) |

### 9.2 Production VM

| Parameter | Value |
|-----------|-------|
| **Name** | `mastodon-vm` |
| **Zone** | `europe-southwest1-c` (Madrid) |
| **Machine Type** | `e2-highmem-2` (2 vCPU, 16 GB RAM) |
| **OS** | Ubuntu 22.04 LTS |
| **Disk** | 50 GB SSD (persistent-disk-0) |
| **Internal IP** | `10.204.0.3` |
| **Project** | `rosy-stronghold-467817-k6` |

### 9.3 Static IP

| Parameter | Value |
|-----------|-------|
| **Name** | `starmeet-static-ip` |
| **Address** | `34.175.113.16` |
| **Region** | `europe-southwest1` |
| **Network Tier** | PREMIUM |

### 9.4 DNS Configuration

**Domain:** `star-meet.com` (registered in Squarespace)

**Cloud DNS Zone:**
- **Project:** `edestory-platform` (NOT rosy-stronghold!)
- **Zone Name:** `star-meet-com`
- **Nameservers:** `ns-cloud-b1/b2/b3/b4.googledomains.com`

**DNS Records:**
| Name | Type | TTL | Data |
|------|------|-----|------|
| `star-meet.com.` | A | 300 | `34.175.113.16` |
| `www.star-meet.com.` | A | 300 | `34.175.113.16` |

**Update DNS (gcloud):**
```bash
# Важно: zone находится в проекте edestory-platform!
gcloud dns record-sets update star-meet.com. \
  --zone=star-meet-com \
  --project=edestory-platform \
  --type=A --ttl=300 --rrdatas=<NEW_IP>
```

### 9.5 SSH Access
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="<cmd>"
```

### 9.6 Quick Deploy
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose build --no-cache starmeet-api wizard && docker compose up -d && docker compose ps"
```

### 9.7 Production URLs
```
https://star-meet.com/join       — Onboarding
https://star-meet.com/dashboard  — Dashboard
https://star-meet.com/star-api/  — FastAPI
https://star-meet.com/star-api/docs — Swagger UI
```

### 9.8 SSL Certificates
- Let's Encrypt (auto-renewed via certbot)
- Mounted in nginx: `/etc/letsencrypt/live/star-meet.com/`

---

## 10. WORKFLOW

### Commit Protocol
```bash
git add -A
git commit -m "type(scope): description"
git push origin <branch>
```

**Types:** `feat`, `fix`, `refactor`, `docs`, `chore`

### Session End Checklist
- [ ] Code compiles/tests pass
- [ ] Changes committed
- [ ] PROGRESS.md updated
- [ ] Blockers documented

---

## 11. COMMUNICATION

### Status Report
```
📍 СТАТУС СЕССИИ
- Текущая фаза: [Phase]
- Задача: [Task]
- Блокеры: [None / Description]
```

### Task Complete
```
✅ ЗАДАЧА ВЫПОЛНЕНА
- Что сделано: [Description]
- Файлы: [List]
- Следующий шаг: [Next]
```

---

## 12. FORBIDDEN ACTIONS

❌ **NEVER:**
- Delete production data
- Push directly to `main` without review
- Hardcode secrets
- Skip testing before reporting completion
- Rewrite Golden Code (engine.py, AstroCalculator.tsx)

---

## 13. NEXT PRIORITIES

1. **Stage 11:** Nakshatra Deep Dive
2. **Stage 12:** Jaimini System
3. **LLM Integration:** Minimax M2 for personality reports
4. **Admin Panel:** Internal talent dashboard

---

**END OF CLAUDE.md**
