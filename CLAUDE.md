# StarMeet Platform - Claude Code Guide

## Quick Deploy Command
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose build --no-cache wizard starmeet-api && docker compose up -d && docker compose ps"
```

---

## Infrastructure Overview

### Google Cloud
- **Project**: mastodon-server-461818
- **VM Name**: mastodon-vm
- **Zone**: europe-southwest1-c
- **External IP**: 34.175.197.44
- **Domain**: star-meet.com

### SSH Access
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c
```

### SSH with Command
```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="<command>"
```

---

## Docker Services (4 containers)

| Service | Container Name | Port | Image |
|---------|---------------|------|-------|
| Frontend (Next.js) | starmeet-wizard | 3001 | starmeet/wizard:latest |
| Backend (FastAPI) | starmeet-api | 8000 | starmeet/api:latest |
| Cache | starmeet-redis | 6379 | redis:7-alpine |
| Gateway | starmeet-nginx | 80, 443 | nginx:alpine |

### Docker Commands on Server
```bash
# View all containers
docker compose ps

# View logs
docker compose logs -f wizard
docker compose logs -f starmeet-api
docker compose logs -f nginx

# Restart specific service
docker compose restart wizard
docker compose restart starmeet-api
docker compose restart nginx

# Rebuild and restart
docker compose build --no-cache wizard && docker compose up -d wizard
docker compose build --no-cache starmeet-api && docker compose up -d starmeet-api

# Full restart
docker compose down && docker compose up -d
```

---

## Supabase Cloud

- **URL**: https://lhirxjxwdjlyyztmeceh.supabase.co
- **Dashboard**: https://supabase.com/dashboard/project/lhirxjxwdjlyyztmeceh
- **Anon Key**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxoaXJ4anh3ZGpseXl6dG1lY2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQzNDU2NzUsImV4cCI6MjA3OTkyMTY3NX0.RQXVSSlneqGwxA3Cta7mizmkKrI9qfZyr-v7JlULU08

**IMPORTANT**: `NEXT_PUBLIC_*` variables must be set at **build time** in Dockerfile, not runtime!

---

## Project Structure

```
StarMeet-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   └── routers/
│   │       └── astro.py    # Astro calculations API
│   ├── Dockerfile
│   └── requirements.txt
├── wizard/                  # Next.js frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/
│   │   └── lib/supabase/   # Supabase client
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf          # Reverse proxy config
├── packages/               # Shared Python packages
│   └── starmeet_astro/     # Astro calculation library
├── docker-compose.yml
└── CLAUDE.md               # This file
```

---

## Deployment Checklist

### 1. Before Deploy
- [ ] Test locally: `npm run dev` (wizard) and `uvicorn` (backend)
- [ ] Commit and push to main branch

### 2. Deploy Commands
```bash
# Option A: Quick deploy (pull + rebuild + restart)
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose build --no-cache wizard starmeet-api && docker compose up -d && docker compose ps"

# Option B: Frontend only
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose build --no-cache wizard && docker compose up -d wizard"

# Option C: Backend only
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose build --no-cache starmeet-api && docker compose up -d starmeet-api"

# Option D: Config only (nginx)
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="cd ~/StarMeet-platform && git pull origin main && docker compose restart nginx"
```

### 3. After Deploy
```bash
# Verify services are running
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="docker compose ps"

# Check for errors
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="docker compose logs --tail=50 wizard"
```

### 4. Test Endpoints
```bash
curl -s https://star-meet.com/health
curl -s https://star-meet.com/star-api/health
curl -s -o /dev/null -w "%{http_code}" https://star-meet.com/login
curl -s -o /dev/null -w "%{http_code}" https://star-meet.com/join
```

---

## URL Routes

| Route | Service | Description |
|-------|---------|-------------|
| / | redirect | → /join |
| /join | wizard | Astro calculator |
| /login | wizard | Login page |
| /signup | wizard | Registration |
| /dashboard | wizard | User dashboard |
| /star-api/* | starmeet-api | FastAPI backend |
| /health | nginx | Health check |

---

## Common Issues & Fixes

### 1. "Application error: a client-side exception"
**Cause**: Missing `NEXT_PUBLIC_*` env vars at build time
**Fix**: Add vars to `wizard/Dockerfile` builder stage, rebuild

### 2. Next.js build fails with Supabase error
**Cause**: Static generation trying to use Supabase at build time
**Fix**: Use server/client component pattern:
```tsx
// page.tsx (server component)
export const dynamic = 'force-dynamic';
import ClientComponent from './ClientComponent';
export default function Page() { return <ClientComponent />; }

// ClientComponent.tsx (client component)
'use client';
// ... use Supabase here
```

### 3. API returning 404
**Cause**: Missing nginx route
**Fix**: Add location block in `nginx/nginx.conf`

### 4. Container not starting
```bash
# Check logs
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="docker compose logs wizard"

# Check health
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c --command="docker compose ps"
```

---

## Local Development

### Frontend (wizard)
```bash
cd wizard
npm install
npm run dev  # http://localhost:3001
```

### Backend (starmeet-api)
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=/path/to/packages uvicorn app.main:app --reload --port 8000
```

### Environment Variables (wizard/.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=https://lhirxjxwdjlyyztmeceh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## SSL Certificates

Certificates are managed by Certbot and stored at:
- `/etc/letsencrypt/live/star-meet.com/fullchain.pem`
- `/etc/letsencrypt/live/star-meet.com/privkey.pem`

Renewal is automatic via cron job.

---

## Useful Aliases (add to server ~/.bashrc)

```bash
alias dc="docker compose"
alias dps="docker compose ps"
alias dlogs="docker compose logs -f"
alias drestart="docker compose restart"
alias drebuild="docker compose build --no-cache"
```
