# CLAUDE.md — StarMeet Agent Constitution

**Version:** 7.0 (Supabase Cloud)
**Updated:** 2025-11-29
**Language:** Think in English, report in Russian

---

## 1. PROJECT IDENTITY

**StarMeet** — AI-powered social network for compatibility matching.
**Core:** Vedic astrology (16 vargas) + psychological profiling.
**Goal:** Build verified talent database for venture fund.

**Current State:**
- ✅ Astro calculator WORKS (all 16 vargas calculated correctly)
- ✅ Next.js frontend EXISTS with working UI
- ✅ FastAPI backend DEPLOYED and healthy
- ✅ PostgreSQL + Redis running
- ✅ Supabase Cloud configured (Auth + Database)
- ✅ User authentication (signup/login/logout)
- ✅ Profiles table created with RLS policies
- ✅ 4-step onboarding wizard (birth → profile → calibration → interests)
- ❌ No social features (matching, messaging)

---

## 2. DOCUMENTATION MAP

| Document | Purpose | Path |
|----------|---------|------|
| `CLAUDE.md` | Agent rules, protocols, MCP | `/docs/CLAUDE.md` |
| `BLUEPRINT.md` | Architecture, stack, schemas | `/docs/BLUEPRINT.md` |
| `PROGRESS.md` | Current status, tasks, logs | `/docs/PROGRESS.md` |

**Rule:** Before starting any task, read relevant document section.

---

## 3. CORE RULES

### 3.1 Language Protocol
- **Thinking & Code:** English
- **Comments in code:** English
- **Progress tracking:** Русский
- **Reports to user:** Русский
- **Commit messages:** English (conventional commits)

### 3.2 Honesty & Integrity
- **NO HALLUCINATIONS:** If unsure, STOP and ask. Never invent code/APIs.
- **NO HACKS:** No temporary workarounds unless explicitly requested.
- **VERIFY:** Test every change before reporting completion.

### 3.3 Autonomous Operation
Agent works independently within defined scope:
- Execute tasks without waiting for approval on minor decisions
- Make architectural decisions within BLUEPRINT constraints
- Report blockers immediately, don't wait

---

## 4. DEVELOPMENT WORKFLOW

### 4.1 Environment
```
Development: Local (VS Code + Docker)
Production:  GCP VM mastodon-vm (deploy via gcloud ssh)
```

**GCP Access:**
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="<cmd>"
```

### 4.2 Branch Strategy
```
main        — production ready
dev         — integration branch
feature/*   — new features
fix/*       — bug fixes
```

### 4.3 Daily Commit Protocol

**MANDATORY:** Commit all changes at end of each work session.
```bash
# Before ending session:
1. git add -A
2. git status (review changes)
3. git commit -m "type(scope): description"
4. git push origin <branch>
```

**Commit Types:**
- `feat` — new feature
- `fix` — bug fix
- `refactor` — code restructure
- `docs` — documentation
- `chore` — maintenance

**Example:**
```bash
git commit -m "feat(astro): add preview endpoint for birth data"
git commit -m "fix(auth): resolve token refresh issue"
git commit -m "docs(blueprint): update API specification"
```

### 4.4 Session End Checklist
Before ending work session:
- [ ] All files saved
- [ ] Code compiles/runs without errors
- [ ] Changes committed with proper message
- [ ] PROGRESS.md updated with today's work
- [ ] Any blockers documented

---

## 5. QUALITY GATES

### 5.1 Definition of Done
Task is complete ONLY when:
1. Code works locally (tested)
2. No console errors/warnings
3. Changes committed
4. PROGRESS.md updated

### 5.2 Testing Protocol
```bash
# Backend (FastAPI)
cd backend && pytest

# Frontend (Next.js)
cd wizard && npm run build

# Docker
docker compose up -d
docker compose ps  # All services "Up"
docker compose logs --tail=20 <service>  # No errors
```

### 5.3 Pre-Deploy Checklist
Before requesting deployment:
- [ ] All tests pass
- [ ] No hardcoded secrets
- [ ] Environment variables documented
- [ ] Docker builds successfully
- [ ] Tested with production-like data

---

## 6. MCP SERVERS (Available Tools)

Agent has access to ~30 MCP servers in VS Code. Key ones:

| MCP Server | Purpose | Usage |
|------------|---------|-------|
| `supabase` | Database & Auth | Direct access to Supabase Cloud |
| `terminal` | Execute shell commands | Run docker, git, npm, python scripts |
| `filesystem` | File operations | Read/write project files |
| `git` | Version control | Commits, branches, history |
| `postgres` | Database | Direct SQL queries |
| `docker` | Containers | Build, run, logs |
| `fetch` | HTTP requests | API testing |
| `puppeteer` | Browser automation | E2E testing |
| `sequential-thinking` | Complex reasoning | Multi-step problems |

**Usage Rule:** Prefer MCP tools over manual CLI when available.

**Priority:** For Docker operations, file system tasks, and shell commands - actively use `terminal` MCP.

---

## 6.1 SUPABASE CLOUD ACCESS

**Project:** StarMeet
**Project ID:** `lhirxjxwdjlyyztmeceh`
**Region:** `eu-central-1`
**Owner:** 288vadim@gmail.com

### Connection Strings

**Session Pooler (recommended for Node.js/serverless):**
```
postgresql://postgres.lhirxjxwdjlyyztmeceh:0J7QYRgAfoL82vdS@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
```

**Direct Connection:**
```
postgresql://postgres:0J7QYRgAfoL82vdS@db.lhirxjxwdjlyyztmeceh.supabase.co:5432/postgres
```

### API Keys

| Key | Value | Usage |
|-----|-------|-------|
| **Project URL** | `https://lhirxjxwdjlyyztmeceh.supabase.co` | Frontend config |
| **Anon Key** | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxoaXJ4anh3ZGpseXl6dG1lY2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQzNDU2NzUsImV4cCI6MjA3OTkyMTY3NX0.RQXVSSlneqGwxA3Cta7mizmkKrI9qfZyr-v7JlULU08` | Public (frontend) |
| **Service Role Key** | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxoaXJ4anh3ZGpseXl6dG1lY2VoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDM0NTY3NSwiZXhwIjoyMDc5OTIxNjc1fQ.RxAnfPkMH3Sx8kKp2tYwYPOWsMof93amhiMYp-8OjQA` | Backend only (bypasses RLS) |
| **DB Password** | `0J7QYRgAfoL82vdS` | Direct DB access |

### Quick SQL Access (Node.js)
```javascript
const { Client } = require('pg');
const client = new Client({
  connectionString: 'postgresql://postgres.lhirxjxwdjlyyztmeceh:0J7QYRgAfoL82vdS@aws-1-eu-central-1.pooler.supabase.com:5432/postgres',
  ssl: { rejectUnauthorized: false }
});
await client.connect();
// Run queries...
await client.end();
```

### MCP Server Config (in ~/.claude.json)
The Supabase MCP server is configured with:
- `SUPABASE_URL`: Project URL
- `SUPABASE_SERVICE_ROLE_KEY`: For admin operations

### Dashboard Links
- [SQL Editor](https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh/sql/new)
- [Table Editor](https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh/editor)
- [Auth Users](https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh/auth/users)
- [Database Settings](https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh/settings/database)
- [API Keys](https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh/settings/api)

---

## 6.2 BRAND DESIGN SYSTEM

### Typography
| Font | Usage | Weight |
|------|-------|--------|
| **Montserrat** | Primary font (all UI) | 400, 500, 600, 700 |

CSS Implementation:
```css
font-family: var(--font-montserrat), system-ui, sans-serif;
```

### Color Palette

#### Primary Colors
| Name | HEX | Usage |
|------|-----|-------|
| **Brand Graphite** | `#2f3538` | Primary buttons, headers, text |
| **Brand Graphite Hover** | `#3d4448` | Hover state for graphite |
| **Brand Green (Dark)** | `#6B9B37` | Links, accents, text highlights |
| **Brand Green Hover** | `#5a8a2d` | Hover state for green links |
| **Brand Green (Light/Button)** | `#B5C76E` | CTA buttons (e.g., "Найти людей") |
| **Brand Green Button Hover** | `#A4B85D` | Hover state for green buttons |

#### CSS Variables (globals.css)
```css
:root {
  --color-brand-green: #6B9B37;
  --color-brand-green-hover: #5a8a2d;
  --color-brand-graphite: #2f3538;
  --color-brand-graphite-hover: #3d4448;
  --font-montserrat: 'Montserrat', sans-serif;
}
```

#### Tailwind Classes (tailwind.config.js)
```javascript
colors: {
  brand: {
    green: '#6B9B37',
    'green-hover': '#5a8a2d',
    graphite: '#2f3538',
    'graphite-hover': '#3d4448',
  }
}
```

### Button Styles

| Type | Background | Hover | Usage |
|------|------------|-------|-------|
| **Primary (Graphite)** | `#2f3538` | `#3d4448` | Main actions, forms |
| **CTA (Green)** | `#B5C76E` | `#A4B85D` | Call-to-action (Найти людей) |
| **Secondary** | `white` + border | `gray-50` | Secondary actions |
| **Link** | transparent | — | Text links (`#6B9B37`) |

### Usage Examples
```tsx
// Primary button (graphite)
className="bg-brand-graphite text-white hover:bg-brand-graphite-hover"

// CTA button (light green)
style={{ backgroundColor: '#B5C76E' }}
onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#A4B85D'}

// Link (dark green)
className="text-brand-green hover:text-brand-green-hover"
```

---

## 7. PROJECT STRUCTURE

```
StarMeet-platform/
├── docs/
│   ├── CLAUDE.md          # This file
│   ├── BLUEPRINT.md       # Architecture
│   └── PROGRESS.md        # Status tracking
├── backend/               # ✅ FastAPI - WORKING
│   ├── app/
│   │   ├── main.py
│   │   ├── core/          # Astro engine wrapper
│   │   ├── routers/       # API endpoints
│   │   │   └── astro.py   # /v1/calculate
│   │   ├── services/
│   │   └── models/
│   ├── requirements.txt
│   └── Dockerfile
├── wizard/                # ✅ Next.js - WORKING
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # AstroCalculator.tsx
│   │   ├── lib/
│   │   └── hooks/
│   ├── package.json
│   └── Dockerfile
├── packages/
│   └── astro_core/        # ✅ Python astro library - WORKING
│       ├── __init__.py
│       └── engine.py      # Digital Twin generator (16 vargas)
├── nginx/
│   └── nginx.conf         # Routing config
├── docker-compose.yml
├── init-astro-db.sql
└── .env
```

---

## 8. COMMUNICATION PROTOCOL

### 8.1 Status Updates
At start of each session, report:
```
📍 СТАТУС СЕССИИ
- Текущая фаза: [Phase X]
- Задача: [Current task]
- Блокеры: [None / Description]
```

### 8.2 Task Completion
After completing task:
```
✅ ЗАДАЧА ВЫПОЛНЕНА
- Что сделано: [Description]
- Файлы изменены: [List]
- Коммит: [Hash or "pending"]
- Следующий шаг: [Next task]
```

### 8.3 Blocker Report
When blocked:
```
🚫 БЛОКЕР
- Проблема: [Description]
- Пробовал: [What was attempted]
- Нужно: [What's needed to proceed]
```

---

## 9. FORBIDDEN ACTIONS

❌ **NEVER:**
- Delete production data volumes
- Push directly to `main` branch without review
- Hardcode secrets in code
- Skip testing before completion report
- Make changes outside project scope
- Use deprecated/removed technologies (Mastodon, Firebase, etc.)

---

## 10. EXISTING CODE CONTEXT

### Golden Code (DO NOT REWRITE)

| File | Purpose | Status |
|------|---------|--------|
| `packages/astro_core/engine.py` | Digital Twin generator | ✅ WORKING |
| `backend/app/routers/astro.py` | API endpoint | ✅ WORKING |
| `wizard/src/components/AstroCalculator.tsx` | UI component | ✅ WORKING |

**Key Functions:**
- `generate_digital_twin()` — Calculates all 16 vargas
- Supports Raman (default) and Lahiri ayanamsa
- Returns full JSON with planets, houses, aspects, nakshatras

### What Needs to Be Added

1. **Profile CRUD** — Save/load calculated charts
2. **Database Schema** — profiles table
3. **Supabase Auth** — User registration/login
4. **Social Features** — Matching, messaging (future)

---

## 11. QUICK REFERENCE

### Key Commands
```bash
# Development
docker compose up -d
docker compose logs -f <service>
docker compose down

# Git
git status
git add -A
git commit -m "type(scope): message"
git push

# Testing
cd backend && python -m pytest
cd wizard && npm test
```

### Key URLs (Production)
```
https://star-meet.com/join       — Frontend (Calculator)
https://star-meet.com/star-api/  — FastAPI
https://star-meet.com/star-api/docs — Swagger UI
https://star-meet.com/star-api/health — Health check
```

### Key Ports (Local)
```
3001  — Next.js (wizard)
8000  — FastAPI
5432  — PostgreSQL
6379  — Redis
```

### API Endpoints
```
POST /star-api/v1/calculate  — Calculate full chart (WORKS)
GET  /star-api/health        — Health check (WORKS)

# TODO:
GET    /star-api/v1/profiles      — List profiles
POST   /star-api/v1/profiles      — Create profile
GET    /star-api/v1/profiles/:id  — Get profile
PUT    /star-api/v1/profiles/:id  — Update profile
DELETE /star-api/v1/profiles/:id  — Delete profile
```

---

**END OF CLAUDE.md**
