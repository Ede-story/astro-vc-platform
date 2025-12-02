# PROGRESS.md — StarMeet Development Log

**Started:** 2025-11-28
**Current Phase:** Astro Brain Implementation (Stages 1-10 complete)
**MVP Target:** Mid-January 2026
**Production URL:** https://star-meet.com

---

## PHASE STATUS

### Infrastructure & UI Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | Infrastructure | ✅ Complete |
| 2 | Auth & Save | ✅ Complete |
| 3 | Onboarding Wizard | ✅ Complete |
| 3.5 | Production Deploy | ✅ Complete |

### Astro Brain Phases

| Phase | Content | Status | Tests |
|-------|---------|--------|-------|
| 1 | Foundation (types, models, Stage 1-2) | ✅ Complete | ✅ All pass |
| 2 | Core Stage 3 (Yogas) | ✅ Complete | ✅ All pass |
| 3 | Varga Stages 4-8 (Wealth, Skills, Career, Creativity, Gains) | ✅ Complete | ✅ All pass |
| 4 | Karmic Depth & Timing (Stages 9-10) | ✅ Complete | ✅ All pass |
| 5 | LLM Integration (Minimax M2) | ⏳ Pending | — |
| 6 | Admin Panel | ⏳ Pending | — |

### Future Phases

| Phase | Name | Status |
|-------|------|--------|
| 7 | Social Core | ⏳ Pending |
| 8 | Matching Engine | ⏳ Pending |
| 9 | Polish & Launch | ⏳ Pending |

---

## CURRENT STACK (Production)

| Component | Technology | Location |
|-----------|------------|----------|
| Frontend | Next.js 14 | `wizard/` |
| Backend API | FastAPI | `backend/` |
| Auth & Database | Supabase Cloud | lhirxjxwdjlyyztmeceh.supabase.co |
| Cache | Redis 7 | Docker container |
| Reverse Proxy | Nginx | Docker container |
| Hosting | GCP VM | mastodon-vm (europe-southwest1-c) |
| Calculator | Python Astro Brain | `backend/app/astro/` |

---

## DAILY LOG

### 2025-12-02 (Session 5) - Astro Brain Phase 4 Complete

**Сделано:**
- ✅ Stage 9 (Karmic Depth): D30, D60, 8 типов дош
- ✅ Stage 10 (Timing): Vimshottari Dasha, Ashtakavarga
- ✅ Создан `reference/doshas.py` с каталогом дош
- ✅ Исправлены тесты (23 passing)
- ✅ Обновлена документация (CLAUDE.md, BLUEPRINT.md, PROGRESS.md)

**Ключевые файлы:**
```
backend/app/astro/stages/stage_09_karmic.py
backend/app/astro/stages/stage_10_timing.py
backend/app/astro/reference/doshas.py
backend/app/astro/tests/test_stages_9_10.py
```

**Технический паттерн (важно!):**
```python
# Helper для работы с planet dict/dataclass
def _get_planet_attr(planet: Any, key: str, default: Any = None) -> Any:
    if hasattr(planet, 'get'):
        return planet.get(key, default)
    return getattr(planet, key, default)
```

---

### 2025-12-02 (Session 4) - Astro Brain Phase 3

**Сделано:**
- ✅ Stages 4-8 (Wealth, Skills, Career, Creativity, Gains)
- ✅ Digital Twin Generator: 20 vargas + Vimshottari Dasha + Chara Karakas
- ✅ 7-система Чара Карак
- ✅ Все тесты проходят

---

### 2025-12-01 (Session 3) - Production Deploy

**Сделано:**
- ✅ Миграция с Supabase Self-Hosted на Supabase Cloud
- ✅ Удалены контейнеры: kong, auth, rest, realtime, db
- ✅ Успешный деплой на star-meet.com

**Ключевой урок:**
> `NEXT_PUBLIC_*` переменные в Next.js должны быть установлены во время **сборки** (build time), а не запуска.

---

### 2025-11-28 (Sessions 1-2) - Foundation

**Сделано:**
- ✅ Onboarding Wizard (4 шага)
- ✅ Supabase Auth
- ✅ Profiles table with RLS
- ✅ Digital Twin Generator (16 vargas)

---

## ASTRO BRAIN STAGES SUMMARY

| Stage | Name | Key Output | Status |
|-------|------|------------|--------|
| 1 | Core Personality | PlanetSummary, Dignities | ✅ |
| 2 | Soul Blueprint | D9 Analysis | ✅ |
| 3 | Yogas | Raja/Dhana/Special Yogas | ✅ |
| 4 | Wealth | D2/D11 + Houses 2,5,9,11 | ✅ |
| 5 | Skills | D24 + Mercury/Jupiter | ✅ |
| 6 | Career | D10 + House 10 | ✅ |
| 7 | Creativity | D5 + House 5 | ✅ |
| 8 | Gains | D11 + House 11 | ✅ |
| 9 | Karmic Depth | D30/D60 + 8 Doshas | ✅ |
| 10 | Timing | Dasha + Ashtakavarga | ✅ |
| 11 | Nakshatra | Personality Deep Dive | ⏳ |
| 12 | Jaimini | Chara Karakas | ⏳ |

---

## DECISIONS LOG

| Date | Decision | Reason |
|------|----------|--------|
| 2025-12-01 | Supabase Cloud | Меньше обслуживания, автобэкапы |
| 2025-12-01 | NEXT_PUBLIC_* in Dockerfile | Переменные нужны при build |
| 2025-12-02 | Optional params in Stage constructors | Гибкость при интеграции |
| 2025-12-02 | `_get_planet_attr()` helper | Совместимость dict/dataclass |

---

## INFRASTRUCTURE

### Google Cloud
- **Project**: mastodon-server-461818
- **VM Name**: mastodon-vm
- **Zone**: europe-southwest1-c
- **External IP**: 34.175.197.44
- **Domain**: star-meet.com

### Supabase Cloud
- **URL**: https://lhirxjxwdjlyyztmeceh.supabase.co
- **Dashboard**: https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh

---

## NEXT STEPS

1. **Stage 11:** Nakshatra Deep Dive
2. **Stage 12:** Jaimini System (Chara Karakas)
3. **Phase 5:** LLM Integration (Minimax M2)
4. **Phase 6:** Admin Panel (Talent Dashboard)

---

## IMPORTANT LINKS

| Resource | URL |
|----------|-----|
| Production | https://star-meet.com |
| GCP Console | console.cloud.google.com |
| Supabase Dashboard | supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh |

---

## CONTACTS

- **Product Owner:** Вадим Архипов
- **Telegram:** @vadim_arkhipov

---

**END OF PROGRESS.md**
