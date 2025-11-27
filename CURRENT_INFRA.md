# CURRENT_INFRA - StarMeet Infrastructure Checkpoint

**Date:** 2025-11-27
**Server:** Google Cloud Platform (GCP) / mastodon-vm (e2-standard-4)
**Project Path:** `/home/vadimarhipov`
**Architecture:** All-in-GCP Monolith

---

## 1. TARGET ARCHITECTURE

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    NGINX (443)                      │
                    │              star-meet.com Gateway                  │
                    └────────┬───────────┬───────────────┬───────────────┘
                             │           │               │
                    ┌────────▼───┐ ┌─────▼─────┐ ┌───────▼───────┐
                    │ Mastodon   │ │  Next.js  │ │   FastAPI     │
                    │   (3000)   │ │  (3001)   │ │   (8000)      │
                    │     /      │ │  /join    │ │   /api        │
                    └────────────┘ └───────────┘ └───────┬───────┘
                                                         │
                                                ┌────────▼────────┐
                                                │   PgBouncer     │
                                                │    (6432)       │
                                                └────────┬────────┘
                                                         │
                    ┌────────────────────────────────────┴────────────────┐
                    │                   PostgreSQL (5432)                 │
                    │         mastodon_production + astro_db              │
                    └─────────────────────────────────────────────────────┘
```

---

## 2. SERVICE PORT MAPPING

| Service | Container Name | Internal Port | External Route |
|---------|----------------|---------------|----------------|
| Nginx Gateway | `mastodon-nginx` | 80, 443 | All traffic |
| Mastodon Web | `mastodon-web` | 3000 | `/` (default) |
| Mastodon Streaming | `mastodon-streaming` | 4000 | `/api/v1/streaming/` |
| **Next.js Wizard** | `starmeet-wizard` | 3001 | `/join/*`, `/_next/*` |
| **FastAPI** | `starmeet-api` | 8000 | `/api/*` (except streaming) |
| **PgBouncer** | `pgbouncer` | 6432 | Internal only |
| PostgreSQL | `mastodon-db` | 5432 | Internal only |
| Redis | `mastodon-redis` | 6379 | Internal only |
| Sidekiq | `mastodon-sidekiq` | - | Background jobs |

---

## 3. CURRENT LIVE CONTAINERS

| Container | Image | Status | Notes |
|-----------|-------|--------|-------|
| `mastodon-nginx` | `nginx:alpine` | Up | Gateway |
| `mastodon-web` | `tootsuite/mastodon:v4.2.27` | Up (unhealthy) | Works, 502 intermittent |
| `mastodon-streaming` | `tootsuite/mastodon:v4.2.27` | Up (unhealthy) | Works |
| `mastodon-sidekiq` | `tootsuite/mastodon:v4.2.27` | Up | Background |
| `mastodon-db` | `postgres:14-alpine` | Up (healthy) | **CRITICAL DATA** |
| `mastodon-redis` | `redis:7-alpine` | Up (healthy) | Cache |

**TODO (Not yet deployed):**
- `starmeet-wizard` (Next.js)
- `starmeet-api` (FastAPI)
- `pgbouncer` (Connection Pooling)

---

## 4. NETWORK CONFIGURATION

**Primary Network:** `astro-network`
- Driver: bridge
- Subnet: `172.21.0.0/16`
- All services must connect to this network

**Internal DNS (Docker):**
- Services can reach each other by container name
- Example: `http://mastodon-web:3000`, `http://starmeet-api:8000`

---

## 5. DATA PERSISTENCE

### Critical Volumes (NEVER DELETE)

| Volume Name | Mount Point | Purpose |
|-------------|-------------|---------|
| `vadimarhipov_postgres14` | `/var/lib/postgresql/data` | **ALL DATABASE DATA** |
| `vadimarhipov_public-system` | `/mastodon/public/system` | User uploads |
| `vadimarhipov_redis` | `/data` | Redis cache |

### Database Schema (Planned)

```sql
-- Existing (Mastodon)
DATABASE: mastodon_production

-- New (Astro)
DATABASE: astro_db
  └── TABLE: astro_profiles
        ├── id (UUID, PK)
        ├── mastodon_user_id (BIGINT, FK -> mastodon accounts.id)
        ├── birth_date (TIMESTAMP WITH TIME ZONE)
        ├── birth_location (JSONB: {lat, lon, city})
        ├── chart_data (JSONB: {d1, d9, ...})
        ├── created_at (TIMESTAMP)
        └── updated_at (TIMESTAMP)
```

---

## 6. HARDWARE RESOURCES

**Instance:** e2-standard-4
- **vCPU:** 4
- **RAM:** 16 GB
- **DISK:** 49 GB Total, ~32 GB Free

**Resource Budget:**
| Service | Expected RAM | Notes |
|---------|--------------|-------|
| Mastodon (web+streaming+sidekiq) | ~2 GB | Current |
| PostgreSQL | ~512 MB | Current |
| Redis | ~128 MB | Current |
| Next.js | ~256 MB | Planned |
| FastAPI | ~256 MB | Planned |
| PgBouncer | ~32 MB | Planned |
| **Total Expected** | ~3.5 GB | Well within 16 GB |

---

## 7. NGINX ROUTING RULES

**Priority Order (Top to Bottom):**

1. `/api/v1/streaming/` → `mastodon-streaming:4000` (WebSocket)
2. `/api/*` → `starmeet-api:8000` (FastAPI REST)
3. `/join/*` → `starmeet-wizard:3001` (Next.js pages)
4. `/_next/*` → `starmeet-wizard:3001` (Next.js assets/HMR)
5. `/` → `mastodon-web:3000` (Default - Mastodon)

**Important Headers:**
```nginx
# For WebSocket/SSE support
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## 8. ENVIRONMENT VARIABLES

### FastAPI (starmeet-api)
```env
DATABASE_URL=postgresql://postgres:mastodon_secure_password@pgbouncer:6432/astro_db
REDIS_URL=redis://mastodon-redis:6379/1
DEBUG=false
```

### Next.js (starmeet-wizard)
```env
NEXT_PUBLIC_API_URL=https://star-meet.com/api
```

### PgBouncer
```env
DATABASES_HOST=mastodon-db
DATABASES_PORT=5432
DATABASES_USER=postgres
DATABASES_PASSWORD=mastodon_secure_password
MAX_CLIENT_CONN=200
DEFAULT_POOL_SIZE=20
```

---

## 9. DEPLOYMENT COMMANDS

```bash
# SSH to server
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c

# Deploy infrastructure (db, pgbouncer, nginx)
docker compose up -d mastodon-db pgbouncer mastodon-nginx

# Deploy backend API
docker compose up -d --build starmeet-api

# Deploy frontend wizard
docker compose up -d --build starmeet-wizard

# View logs
docker compose logs -f starmeet-api starmeet-wizard

# Check all containers
docker compose ps

# PgBouncer stats
docker exec pgbouncer psql -p 6432 -U postgres pgbouncer -c "SHOW POOLS"
```

---

## 10. MIGRATION CHECKLIST

- [x] Documentation updated (CLAUDE.md v6.0)
- [ ] PgBouncer added to docker-compose.yml
- [ ] init-astro-db.sql created
- [ ] Nginx config updated for path-based routing
- [ ] Folder structure created (backend/, wizard/, packages/)
- [ ] FastAPI scaffold deployed
- [ ] Next.js scaffold deployed
- [ ] Integration tested
