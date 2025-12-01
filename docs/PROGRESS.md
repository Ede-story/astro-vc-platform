# PROGRESS.md — StarMeet Development Log

**Started:** 2025-11-28
**Current Phase:** 3 (Production Deploy)
**MVP Target:** Mid-January 2026
**Production URL:** https://star-meet.com

---

## PHASE STATUS

| Phase | Name | Status | Target Week |
|-------|------|--------|-------------|
| 1 | Infrastructure | ✅ Complete | Week 1 |
| 2 | Auth & Save | ✅ Complete | Week 2 |
| 3 | Onboarding Wizard | ✅ Complete | Week 3 |
| 3.5 | Production Deploy | ✅ Complete | Week 3 |
| 4 | Social Core | ⏳ Pending | Week 4 |
| 5 | Matching Engine | ⏳ Pending | Week 5 |
| 6 | Polish & Launch | ⏳ Pending | Week 6 |

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

### Docker Services (4 containers)
```
starmeet-wizard   → Next.js frontend (port 3001)
starmeet-api      → FastAPI backend (port 8000)
starmeet-redis    → Redis cache (port 6379)
starmeet-nginx    → Nginx gateway (ports 80, 443)
```

---

## WHAT ALREADY EXISTS

**✅ Completed:**

| Component | Status | Location |
|-----------|--------|----------|
| Next.js frontend | ✅ Deployed | `wizard/` |
| Astro calculator UI | ✅ Works | `/join` page |
| Digital Twin Generator | ✅ Works | 16 vargas calculation |
| All 60 vargas calculation | ✅ Verified | starmeet_astro package |
| FastAPI backend | ✅ Deployed | `backend/` |
| Supabase Auth | ✅ Works | Cloud instance |
| User registration | ✅ Works | `/signup` |
| User login | ✅ Works | `/login` |
| Dashboard | ✅ Works | `/dashboard` |
| Onboarding wizard | ✅ Works | `/join` → `/join/result` → `/join/profile` → `/join/interests` |
| SSL/HTTPS | ✅ Works | Let's Encrypt |
| Production deploy | ✅ Works | star-meet.com |

---

## DAILY LOG

### 2025-12-01 (Session 4) - Production Deploy

**Сделано:**
- ✅ Исправлена ошибка "Application error: a client-side exception" на странице логина
- ✅ Добавлены `NEXT_PUBLIC_SUPABASE_*` переменные в wizard/Dockerfile (build-time)
- ✅ Миграция с Supabase Self-Hosted на Supabase Cloud
- ✅ Удалены контейнеры: kong, auth, rest, realtime, db (освобождено ~2GB RAM)
- ✅ Обновлён nginx.conf (удалён /supabase/ route)
- ✅ Обновлён docker-compose.yml (4 сервиса вместо 9)
- ✅ Создан CLAUDE.md с инструкциями по деплою
- ✅ Успешный деплой на star-meet.com

**Ключевой урок:**
> `NEXT_PUBLIC_*` переменные в Next.js должны быть установлены во время **сборки** (build time), а не запуска (runtime). Они "впекаются" в JavaScript бандл.

**Изменённые файлы:**
```
wizard/Dockerfile (added NEXT_PUBLIC_SUPABASE_* vars)
docker-compose.yml (removed self-hosted Supabase)
nginx/nginx.conf (removed /supabase/ route)
CLAUDE.md (deployment guide)
```

**Quick Deploy Command:**
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose build --no-cache wizard starmeet-api && docker compose up -d && docker compose ps"
```

---

### 2025-11-28 (Session 3)

**Сделано:**
- ✅ Создан multi-step Onboarding Wizard
- ✅ Step 1: Birth Data с PlaceAutocomplete (Nominatim)
- ✅ Step 1: Time accuracy selector (Точно/Примерно/Не знаю)
- ✅ Dopamine Hit экран с анимированным результатом (Sun/Moon/Asc)
- ✅ Step 2: Profile Info с avatar upload и username validation
- ✅ Step 3: Interests selector (Seeking/Offerings)
- ✅ WizardContext для state management
- ✅ WizardProgress component
- ✅ Билд успешен

**Созданные файлы:**
```
wizard/src/contexts/WizardContext.tsx
wizard/src/components/wizard/WizardProgress.tsx
wizard/src/components/wizard/PlaceAutocomplete.tsx
wizard/src/components/wizard/DopamineHit.tsx
wizard/src/components/wizard/InterestSelector.tsx
wizard/src/app/join/layout.tsx
wizard/src/app/join/page.tsx (Step 1)
wizard/src/app/join/result/page.tsx (Dopamine Hit)
wizard/src/app/join/profile/page.tsx (Step 2)
wizard/src/app/join/interests/page.tsx (Step 3)
```

**User Flow:**
```
/join → birth data → /join/result (dopamine hit) → /join/profile → /join/interests → /dashboard
```

---

### 2025-11-28 (Session 2)

**Сделано:**
- ✅ Создан docker-compose.new.yml с Supabase стеком
- ✅ Создана схема БД: profiles, compatibility_cache, matches, messages с RLS
- ✅ Созданы Supabase клиенты (client.ts, server.ts, middleware.ts)
- ✅ Созданы страницы: /login, /signup, /dashboard
- ✅ Создан useAuth hook
- ✅ Обновлён AstroCalculator для сохранения в Supabase

---

### 2025-11-28 (Session 1)

**Сделано:**
- ✅ Полная очистка проекта от Mastodon
- ✅ Создана документация (CLAUDE.md, BLUEPRINT.md, PROGRESS.md)
- ✅ Определена архитектура
- ✅ Верифицирована работа астро-калькулятора (все 60 варг корректны)

---

## DECISIONS LOG

| Date | Decision | Reason |
|------|----------|--------|
| 2025-11-28 | Supabase Self-Hosted | Полный контроль над схемой |
| **2025-12-01** | **→ Supabase Cloud** | Меньше обслуживания, автобэкапы, освободить RAM |
| 2025-11-28 | Keep jyotishganit in frontend | Уже работает, не ломать |
| 2025-11-28 | FastAPI for matching only | Тяжёлые расчёты совместимости в Python |
| 2025-11-28 | Single domain (star-meet.com) | Избежать CORS/cookie проблем |
| 2025-12-01 | NEXT_PUBLIC_* in Dockerfile | Переменные нужны при build, не runtime |

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

### SSH Access
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c
```

---

## URL ROUTES

| Route | Service | Description |
|-------|---------|-------------|
| / | redirect | → /join |
| /join | wizard | Astro calculator (onboarding step 1) |
| /join/result | wizard | Dopamine hit screen |
| /join/profile | wizard | Profile setup (step 2) |
| /join/interests | wizard | Interests (step 3) |
| /login | wizard | Login page |
| /signup | wizard | Registration |
| /dashboard | wizard | User dashboard |
| /explore | wizard | Browse profiles |
| /star-api/* | starmeet-api | FastAPI backend |
| /health | nginx | Health check |

---

## METRICS

| Metric | Current | Week 4 | Week 6 (MVP) |
|--------|---------|--------|--------------|
| Production URL | ✅ star-meet.com | — | — |
| Users | 0 | 50 | 200 |
| Profiles saved | 0 | 50 | 200 |
| API response (p95) | ~2s | <1s | <500ms |

---

## KNOWN ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| GitHub Dependabot alerts | ⚠️ 25 vulns | 2 critical, need to address |

---

## NEXT STEPS

1. **Phase 4: Social Core**
   - [ ] Profile page (`/profile/[username]`)
   - [ ] Explore page with filters
   - [ ] Like/Connect functionality
   - [ ] Match notifications

2. **Phase 5: Matching Engine**
   - [ ] Compatibility calculation API
   - [ ] Match scoring algorithm
   - [ ] "People like you" recommendations

---

## IMPORTANT LINKS

| Resource | URL |
|----------|-----|
| Production | https://star-meet.com |
| GCP Console | console.cloud.google.com |
| Supabase Dashboard | supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh |
| GitHub | github.com/Ede-story/astro-vc-platform |

---

## CONTACTS

- **Product Owner:** Вадим Архипов
- **Telegram:** @vadim_arkhipov

---

**END OF PROGRESS.md**
