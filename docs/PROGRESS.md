# PROGRESS.md — StarMeet Development Log

**Started:** 2025-11-28
**Current Phase:** 1 (Infrastructure)
**MVP Target:** Mid-January 2026

---

## PHASE STATUS

| Phase | Name | Status | Target Week |
|-------|------|--------|-------------|
| 1 | Infrastructure | ✅ Complete | Week 1 |
| 2 | Auth & Save | ✅ Complete | Week 2 |
| 3 | Onboarding Wizard | ✅ Complete | Week 3 |
| 4 | Social Core | ⏳ Pending | Week 4 |
| 5 | Matching Engine | ⏳ Pending | Week 5 |
| 6 | Polish & Launch | ⏳ Pending | Week 6 |

---

## WHAT ALREADY EXISTS

**✅ Completed before project start:**

| Component | Status | Location |
|-----------|--------|----------|
| Next.js frontend | ✅ Works | `frontend/` |
| Astro calculator UI | ✅ Works | `frontend/src/app/page.tsx` |
| jyotishganit integration | ✅ Works | `frontend/src/lib/astro/` |
| All 60 vargas calculation | ✅ Verified | — |
| Planets table | ✅ Works | `frontend/src/components/` |
| Houses table | ✅ Works | `frontend/src/components/` |
| Varga selector (D1-D60) | ✅ Works | — |

**Screenshot proof:** Calculator shows correct data for D60-Shashtiamsha

---

## CURRENT SPRINT: Phase 1 (Infrastructure)

### Week 1 Tasks

**Day 1-2: Supabase Setup**
- [x] Create docker-compose.yml with PostgreSQL
- [x] Add Supabase services (Kong, GoTrue, PostgREST, Realtime)
- [x] Create database schema (profiles, messages, matches)
- [ ] Test Supabase Studio access locally

**Day 3-4: Auth Integration**
- [x] Install @supabase/supabase-js in frontend
- [x] Create Supabase client (`wizard/src/lib/supabase/`)
- [x] Implement signup page (`/signup`)
- [x] Implement login page (`/login`)
- [x] Create middleware for protected routes
- [ ] Test auth flow end-to-end

**Day 5: Profile Save**
- [x] Update AstroCalculator to save to Supabase
- [x] Implement INSERT to profiles table
- [x] Link auth.user.id to profile.id
- [x] Create /dashboard page
- [ ] Test: calculate → save → verify in DB

**Блокеры:** Нет

---

## DAILY LOG

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

**Следующие шаги:**
1. Тестирование wizard flow
2. Phase 4: Social Core

---

### 2025-11-28 (Session 2)

**Сделано:**
- ✅ Создан docker-compose.new.yml с Supabase стеком (PostgreSQL, Kong, GoTrue, PostgREST, Realtime)
- ✅ Создана схема БД: profiles, compatibility_cache, matches, messages с RLS
- ✅ Создана Kong конфигурация (supabase/kong.yml)
- ✅ Обновлён nginx.conf для Supabase routing
- ✅ Установлен @supabase/supabase-js и @supabase/ssr
- ✅ Созданы Supabase клиенты (client.ts, server.ts, middleware.ts)
- ✅ Созданы страницы: /login, /signup, /dashboard
- ✅ Создан useAuth hook
- ✅ Обновлён AstroCalculator для сохранения в Supabase вместо файлов
- ✅ Билд проходит успешно

**Созданные файлы:**
```
docker-compose.new.yml
database/schema.sql
supabase/kong.yml
nginx/nginx.new.conf
wizard/src/lib/supabase/client.ts
wizard/src/lib/supabase/server.ts
wizard/src/lib/supabase/middleware.ts
wizard/src/middleware.ts
wizard/src/hooks/useAuth.ts
wizard/src/app/(auth)/login/page.tsx
wizard/src/app/(auth)/signup/page.tsx
wizard/src/app/dashboard/page.tsx
wizard/.env.local
```

**Изменённые файлы:**
```
wizard/src/components/AstroCalculator.tsx
wizard/package.json (added supabase deps)
docs/PROGRESS.md
```

**Следующие шаги:**
1. Запустить docker-compose локально или на сервере
2. Протестировать auth flow
3. Протестировать сохранение профилей

---

### 2025-11-28 (Session 1)

**Сделано:**
- ✅ Полная очистка проекта от Mastodon
- ✅ Создана документация (CLAUDE.md, BLUEPRINT.md, PROGRESS.md)
- ✅ Определена архитектура (Supabase Self-Hosted + FastAPI + Next.js)
- ✅ Верифицирована работа астро-калькулятора (все 60 варг корректны)
- ✅ Создан 6-недельный план разработки

**Скриншот:** Калькулятор показывает D60-Шаштиамша с корректными данными

**Коммиты:**
- `docs: initial project documentation`
- `chore: clean up Mastodon references`

---

## DECISIONS LOG

| Date | Decision | Reason |
|------|----------|--------|
| 2025-11-28 | Supabase Self-Hosted | Полный контроль над схемой, использовать GCP кредиты |
| 2025-11-28 | Keep jyotishganit in frontend | Уже работает, не ломать |
| 2025-11-28 | FastAPI for matching only | Тяжёлые расчёты совместимости в Python |
| 2025-11-28 | Single domain (star-meet.com) | Избежать CORS/cookie проблем |
| 2025-11-28 | Path-based routing | `/api/` → FastAPI, `/supabase/` → Kong |

---

## METRICS

| Metric | Current | Week 2 | Week 4 | Week 6 (MVP) |
|--------|---------|--------|--------|--------------|
| Users | 0 | 10 | 50 | 200 |
| Profiles saved | 0 | 10 | 50 | 200 |
| Charts calculated | ~100 (manual) | 20 | 100 | 500 |
| API response (p95) | — | <2s | <1s | <500ms |

---

## KNOWN ISSUES

*None currently*

---

## DEPENDENCIES TO INSTALL

### Frontend (when starting auth integration)
```bash
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
```

### Backend (when creating FastAPI service)
```bash
pip install fastapi uvicorn psycopg2-binary redis pydantic-settings
```

---

## IMPORTANT LINKS

| Resource | URL |
|----------|-----|
| GCP Console | console.cloud.google.com |
| Domain | star-meet.com |
| Supabase Docs | supabase.com/docs |
| jyotishganit | github.com/nicvit/jyotishganit |

---

## CONTACTS

- **Product Owner:** Вадим Архипов
- **Telegram:** @vadim_arkhipov

---

**END OF PROGRESS.md**
