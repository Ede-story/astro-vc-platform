# CLAUDE.md – StarMeet Project Context & Constitution

**Version:** 6.0 (All-in-GCP Monolith Architecture)
**Last Updated:** 2025-11-27
**Server:** GCP (`mastodon-vm`) | **OS:** Linux
**Status:** Infrastructure Phase - Preparing Next.js + FastAPI stack

---

## 1. VISION & GOAL
**StarMeet** is a unified ecosystem merging a Social Network (Mastodon) with Professional Astrology.
**Goal:** Create a "Bridge" between social data and astrological data to enable AI-driven matching.

**Architecture (All-in-GCP Monolith):**
```
Nginx (Gateway) -> [Mastodon, Next.js, FastAPI] -> PgBouncer -> PostgreSQL
```

1.  **Social Core:** Mastodon v4.2 (Ruby on Rails) -> Identity Provider
2.  **Wizard UI:** Next.js 14+ (Dockerized on GCP) -> Onboarding Wizard at `/join`
3.  **Astro API:** FastAPI (Python 3.11) -> REST API at `/api`
4.  **Astro Engine:** `jyotishganit` library -> Calculation Core
5.  **Database:** PostgreSQL 14 + PgBouncer (connection pooling)

---

## 2. RULES OF ENGAGEMENT (CRITICAL)

### A. HONESTY & INTEGRITY
* **NO HALLUCINATIONS:** If you cannot find a solution or an API endpoint, **STOP** and report it.
* **NO CRUTCHES:** Do not build temporary "hacks" unless explicitly asked for a prototype.
* **RESOURCE AWARENESS:** We have **32GB free disk space**. Be mindful with large Docker images.

### B. AUTONOMOUS TESTING (DEFINITION OF DONE)
Before marking a task as "Completed", you MUST:
1.  **Check Container Health:** `docker compose ps` (Must be `Up`, not `Restarting`).
2.  **Check Logs:** `docker compose logs --tail=20 <service>` (No tracebacks/crashes).
3.  **Verify Connectivity:** `curl -I http://localhost:<port>` inside the server.
* **Rule:** If `curl` returns 500/502/Connection Refused -> **FIX IT** before reporting.

### C. EXECUTION PROTOCOL
* **REMOTE ONLY:** All commands run on GCP via SSH. Never run code on local macOS terminal.
* **DATA SAFETY:** The volume `vadimarhipov_postgres14` contains PRODUCTION DATA. **NEVER** delete it.

### D. ARCHITECTURE RULES (CRITICAL)
* **Frontend NEVER calculates.** Next.js only renders JSON received from Backend API.
* **All services communicate via internal Docker network `astro-network`.**
* ❌ **NO STREAMLIT** - Deprecated. Legacy code archived in `_ARCHIVE_STREAMLIT_POC/`.
* ❌ **NO VERCEL** - All services run on GCP for zero-latency and unified cookies.

### E. LANGUAGE PROTOCOL
* **THINKING & PLANNING:** Use **English** for internal logic, code comments.
* **REPORTS & COMMUNICATION:** All responses to the user must be in **RUSSIAN**.
* **UI TEXT:** All user-facing text must be in **RUSSIAN**.

---

## 3. TECHNICAL STACK (APPROVED)

| Component | Technology | Port | Route |
| :--- | :--- | :--- | :--- |
| **Gateway** | Nginx (Alpine) | 443 | All traffic |
| **Social Core** | Mastodon v4.2.27 | 3000 | `/` (default) |
| **Wizard UI** | Next.js 14+ (Docker) | 3001 | `/join`, `/_next` |
| **Astro API** | FastAPI (Python 3.11) | 8000 | `/api` |
| **DB Pooler** | PgBouncer | 6432 | Internal |
| **Database** | PostgreSQL 14 | 5432 | Internal |
| **Cache** | Redis 7 | 6379 | Internal |

---

## 4. LIVE INFRASTRUCTURE

**Networking:**
* Network Name: `astro-network`
* Subnet: `172.21.0.0/16`
* All containers on same network for internal communication

**URL Routing (Path-Based):**
| Path | Service | Container |
|------|---------|-----------|
| `/` | Mastodon | `mastodon-web:3000` |
| `/api/v1/streaming/` | Streaming | `mastodon-streaming:4000` |
| `/api/*` | FastAPI | `starmeet-api:8000` |
| `/join/*`, `/_next/*` | Next.js | `starmeet-wizard:3001` |

**Persistence (Volumes):**
* `vadimarhipov_postgres14`: **CRITICAL DB DATA** - NEVER DELETE
* `vadimarhipov_public-system`: User uploads
* `vadimarhipov_redis`: Redis data

**Hardware Resources:**
* **RAM:** 16GB Total (e2-standard-4)
* **DISK:** 49G Total, ~32G Free

---

## 5. PROJECT STRUCTURE

```
StarMeet-platform/
├── CLAUDE.md              # This file (Source of Truth)
├── CURRENT_INFRA.md       # Infrastructure documentation
├── docker-compose.yml     # Main compose file
├── init-astro-db.sql      # Database initialization
├── mastodon/              # Mastodon source (Ruby)
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── core/
│   │   │   └── astro_engine.py  # GOLDEN MATH
│   │   ├── api/
│   │   └── models/
│   └── Dockerfile
├── wizard/                # Next.js application
│   ├── src/
│   └── Dockerfile
├── packages/
│   └── astro_core/        # Shared Python library
└── nginx/
    └── nginx.conf
```

---

## 6. GIT WORKFLOW & SAFETY

**Repository:** `https://github.com/Ede-story/astro-vc-platform`

### A. AUTO-COMMIT RULE
After completing any significant task, execute:
```bash
cd /Users/vadimarhipov/StarMeet-platform
git add .
git commit -m "Task: <short description>"
git push
```

### B. SECRET SAFETY
**NEVER commit:**
* `.env.production`, `.env.*`
* `mastodon/public/system/`
* `*.tar.gz`, `*.dat`

---

## 7. COMMAND CHEATSHEET

```bash
# SSH Connect
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c

# Deploy all services
docker compose up -d

# Deploy specific service
docker compose up -d --build starmeet-api

# Check logs
docker compose logs -f starmeet-api

# Check container status
docker compose ps

# Check disk space
df -h

# PgBouncer stats
docker exec pgbouncer psql -p 6432 -U postgres pgbouncer -c "SHOW POOLS"
```

---

## 8. ROADMAP

### PHASE 1: INFRASTRUCTURE (Current)
- [x] Update documentation (CLAUDE.md, CURRENT_INFRA.md)
- [ ] Add PgBouncer to docker-compose
- [ ] Create `astro_db` database
- [ ] Configure Nginx path-based routing
- [ ] Create folder structure

### PHASE 2: BACKEND API
- [ ] FastAPI scaffold with health endpoints
- [ ] Connect to PostgreSQL via PgBouncer
- [ ] Port `astro_engine.py` (Golden Math)
- [ ] CRUD endpoints for profiles

### PHASE 3: WIZARD UI
- [ ] Next.js scaffold with basePath=/join
- [ ] Multi-step onboarding form
- [ ] API integration
- [ ] Chart visualization

### PHASE 4: INTEGRATION
- [ ] Mastodon OAuth2 integration
- [ ] User linking (Mastodon ID <-> Astro Profile)
- [ ] Matching algorithm

---

## 9. KNOWN ISSUES

* **Mastodon unhealthy:** `mastodon-web` reports unhealthy but responds (502/200 intermittent).

---

## 10. CLEANUP LOG

**2025-11-27:** Streamlit deprecated. Pivoting to Next.js + FastAPI.
**2025-11-25:** VedAstro C# repos deleted (~20GB freed on GCP).
