# CLAUDE.md – StarMeet Project Context & Constitution

**Version:** 5.0 (Pivot to Python Native & Integration Phase)
**Last Updated:** 2025-11-25
**Server:** GCP (`mastodon-vm`) | **OS:** Linux
**Status:** Production Live (Infra Stable, Data isolated)

---

## 1. VISION & GOAL
**StarMeet** is a unified ecosystem merging a Social Network (Mastodon) with Professional Astrology.
**Goal:** Create a "Bridge" between social data and astrological data to enable AI-driven matching.

**Current Architecture (The "Two Engines" Model):**
1.  **Social Core:** Mastodon v4.2 (Ruby on Rails) -> Identity Provider.
2.  **Astro Core:** Streamlit App (Python) + `jyotishganit` Library -> Calculation Engine.
3.  **The Bridge (TODO):** Shared PostgreSQL Database + OAuth.

---

## 2. RULES OF ENGAGEMENT (CRITICAL)

### A. HONESTY & INTEGRITY
* **NO HALLUCINATIONS:** If you cannot find a solution or an API endpoint, **STOP** and report it. Do not invent code/data just to satisfy the prompt.
* **NO CRUTCHES:** Do not build temporary "hacks" (like hardcoded JSONs or math in UI) unless explicitly asked for a prototype.
* **RESOURCE AWARENESS:** We have **32GB free disk space** (after cleanup 2025-11-25). Be mindful with large Docker images or logs.

### B. AUTONOMOUS TESTING (DEFINITION OF DONE)
You are responsible for Quality Assurance. Before marking a task as "Completed", you MUST:
1.  **Check Container Health:** `docker compose ps` (Must be `Up`, not `Restarting`).
2.  **Check Logs:** `docker compose logs --tail=20 <service>` (No Python tracebacks/crashes).
3.  **Verify Connectivity:** Execute `curl -I http://localhost:<port>` inside the server.
* **Rule:** If `curl` returns 500/502/Connection Refused -> **FIX IT** before reporting.

### C. EXECUTION PROTOCOL
* **REMOTE ONLY:** All commands run on GCP via SSH. Never run code on the local macOS terminal.
* **DATA SAFETY:** The volume `vadimarhipov_postgres14` contains PRODUCTION DATA. **NEVER** delete it.

### D. LANGUAGE PROTOCOL
* **THINKING & PLANNING:** Use **English** for internal logic, code comments, and technical reasoning (maximum clarity).
* **REPORTS & COMMUNICATION:** All responses to the user, status reports, and summaries must be in **RUSSIAN**.
* **UI TEXT:** All user-facing text in the Streamlit app must be in **RUSSIAN**.
* *Reason:* The Project Owner speaks Russian, but the codebase logic is in English.

---

## 3. TECHNICAL STACK (APPROVED)

| Component | Technology | Details |
| :--- | :--- | :--- |
| **Social Logic** | Mastodon (Ruby on Rails) | Core v4.2.27. Handles Users/Auth. |
| **Astro Logic** | **Python 3.9 + jyotishganit** | **MIT License.** Native calculations (No external API). |
| **Interface** | Streamlit | Serves UI at `/astro`. |
| **Database** | PostgreSQL 14 | Shared container `mastodon-db`. |
| **Proxy** | Nginx (Alpine) | Routes `/` to Mastodon, `/astro` to Streamlit. |
| **AI Agent** | MiniMax M2 | (Planned integration). |

---

## 4. LIVE INFRASTRUCTURE (SNAPSHOT 2025-11-25)

**Networking:**
* Network Name: `astro-network`
* Subnet: `172.21.0.0/16`
* **Nginx** can see **vedastro-ui** (Verified).

**Containers & Ports:**

| Container Name | Image | Status | Ports |
| :--- | :--- | :--- | :--- |
| `vedastro-ui` | `starmeet/astro-ui:v1.1.0` | Up | `0.0.0.0:8501->8501/tcp` |
| `mastodon-nginx` | `nginx:alpine` | Up | `0.0.0.0:80->80/tcp`, `0.0.0.0:443->443/tcp` |
| `mastodon-web` | `tootsuite/mastodon:v4.2.27` | Up (unhealthy) | `0.0.0.0:3000->3000/tcp` |
| `mastodon-streaming` | `tootsuite/mastodon:v4.2.27` | Up (unhealthy) | `0.0.0.0:4000->4000/tcp` |
| `mastodon-db` | `postgres:14-alpine` | Up (healthy) | `5432/tcp` |
| `mastodon-redis` | `redis:7-alpine` | Up (healthy) | `6379/tcp` |

**Persistence (Volumes):**
* `vadimarhipov_postgres14`: **CRITICAL DB DATA**.
* `vadimarhipov_public-system`: Uploaded files/media.
* `vadimarhipov_mastodon_redis`: Redis data.
* `vadimarhipov_minio_data`: (Service stopped).
* `vadimarhipov_opensearch_data`: (Service stopped).

**Hardware Resources:**
* **RAM:** 15Gi Total, ~1.1Gi Used, 14Gi Available (Excellent)
* **DISK:** 49G Total, 17G Used, **32G Free** (Healthy - after cleanup 2025-11-25)

---

## 5. IMMEDIATE ROADMAP (NEXT STEPS)

We are moving from "Isolated Apps" to "Integrated Ecosystem".

### PHASE 1: DATA PERMANENCE (Current Focus)
* [ ] **Connect Streamlit to Postgres:** Stop saving to `json`. Connect `vedastro-ui` to `mastodon-db`.
* [ ] **Create Schema:** Create a separate database/schema `astro_db` for astrological profiles.
* [ ] **Migration:** Move existing JSON profiles into SQL.

### PHASE 2: UNIFIED AUTH (SSO)
* [ ] **OAuth2:** Allow users to "Login with StarMeet" on the Astro page.
* [ ] **Link:** Match Astro Profile ID <-> Mastodon User ID.

### PHASE 3: INTELLIGENCE & SEARCH
* [ ] **OpenSearch:** Deploy with memory limits (Heap < 512MB).
* [ ] **Indexing:** Push calculated charts (Sun/Moon signs) to Search Index.
* [ ] **Matching:** Python script to find compatible users.

---

## 6. GIT WORKFLOW & SAFETY (CRITICAL)

**Repository:** `https://github.com/Ede-story/astro-vc-platform`
**Structure:** Mono-repo (includes Mastodon source code)

### A. AUTO-COMMIT RULE
After completing any significant task, you **MUST** execute:
```bash
cd /Users/vadimarhipov/StarMeet-platform
git add .
git commit -m "Task: <short description of completed work>"
git push
```
* **Trigger:** Every completed TODO item, bug fix, feature, or config change.
* **Format:** Commit messages start with `Task:`, `Fix:`, `Feat:`, or `Docs:`.

### B. REPOSITORY CONTENTS
| Folder | Contents | Tracked |
|--------|----------|---------|
| `mastodon/` | Full Mastodon v4.2 source (Ruby) | ✅ Yes |
| `vedastro-ui/` | Streamlit Astro App (Python) | ✅ Yes |
| `nginx/` | Reverse proxy configs | ✅ Yes |
| `_ARCHIVE*/` | Legacy files | ❌ Ignored |

### C. SECRET SAFETY (BEFORE EVERY COMMIT)
**NEVER commit these files:**
* `.env.production` — Contains DB passwords, secrets
* `.env.*` — Any environment files
* `mastodon/public/system/` — User uploads
* `*.tar.gz` — Large archives
* `hip_main.dat` — Star catalog (53MB)

**Verification command:**
```bash
git status --porcelain | grep -E "\.env|system/|\.tar\.gz"
# If output is NOT empty -> DO NOT COMMIT, fix .gitignore first
```

### D. .GITIGNORE CHECKLIST
The `.gitignore` file MUST contain:
```
.env*
*.env
mastodon/.env.production
mastodon/public/system/
*.tar.gz
*.dat
_ARCHIVE*/
```

---

## 7. PROJECT STRUCTURE

**Server Path:** `/home/vadimarhipov`

**Key Files:**
* `docker-compose.yml` — Main compose (Mastodon services)
* `docker-compose.astro.yml` — Astro UI compose
* `~/nginx/nginx.conf` — Nginx configuration

**URL Routing:**
* `https://star-meet.com` -> `mastodon-web:3000`
* `https://star-meet.com/astro/` -> `vedastro-ui:8501`

---

## 8. COMMAND CHEATSHEET

```bash
# SSH Connect
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c

# Deploy UI
docker compose up -d --build vedastro-ui

# Restart Nginx
docker compose restart mastodon-nginx

# Check UI Logs
docker compose logs -f vedastro-ui

# Check Container Status
docker compose ps

# Check Disk Space
df -h
```

---

## 9. KNOWN ISSUES

* **Mastodon unhealthy:** `mastodon-web` and `mastodon-streaming` report unhealthy but respond (502/200 intermittent).

---

## 10. CLEANUP LOG

**2025-11-25: Project Sanitation (Phase 1 - edestory-platform)**
- Deleted: VedAstro C#/.NET repos (vedastro-github, vedastro-opensource, vedastro-integration, vedastro-web) — ~5.5GB
- Deleted: VedAstro tar archives (vedastro-bundle.tar.gz, vedastro-light.tar.gz, vedastro-ui.tar.gz) — ~1.9GB
- Deleted on GCP: Old Docker images (vedastro-wrapper, vedastro/api, old mastodon versions, opensearch, minio, neo4j) — ~20GB freed
- Archived to `_ARCHIVE_2025_BEFORE_CLEANUP/`: Legacy docs, old compose files, EdeStory remnants — 394MB
- **Result:** GCP disk 12GB -> 32GB free

**2025-11-25: Deep Cleanup (Phase 2 - Home Directory)**
- Deleted: `astro-vc-platform/` (1.9GB) — Old project with MiniMax M2, Ocelot references
- Deleted: `astro-connect-ai/` (76KB) — MiniMax M2 Modelfiles and analysis
- Deleted: `vedastro-full/` (1.8GB) — Another VedAstro C# clone
- Deleted: `astro-connect-platform/` — Empty scaffold
- Deleted: `ocelot-deployment/`, `ocelot-social-fresh/` (177MB) — Dead Ocelot Social project
- Deleted: `EDEstory-backend/`, `EDEstory-frontend/` (431MB) — Old eCommerce project
- Deleted: `saleor-platform/`, `medusa-official-demo/`, `react-storefront/` (73MB) — eCommerce experiments
- Deleted: Scattered test files (*.json, *.py, *.md reports)
- **Total freed locally:** ~4.5GB
