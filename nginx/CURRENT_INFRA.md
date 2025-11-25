# CURRENT_INFRA Checkpoint

**Date:** 2025-11-25
**Server:** Google Cloud Platform (GCP) / mastodon-vm
**Project Path:** `/home/vadimarhipov`

---

## 1. LIVE CONTAINERS (Docker Status)

| Container Name | Image | Status | Ports |
| :--- | :--- | :--- | :--- |
| `vedastro-ui` | `starmeet/astro-ui:v1.1.0` | Up 3 hours | `0.0.0.0:8501->8501/tcp` |
| `mastodon-nginx` | `nginx:alpine` | Up 18 hours | `0.0.0.0:80->80/tcp`, `0.0.0.0:443->443/tcp` |
| `mastodon-web` | `tootsuite/mastodon:v4.2.27` | Up 18 hours (unhealthy) | `0.0.0.0:3000->3000/tcp` |
| `mastodon-streaming` | `tootsuite/mastodon:v4.2.27` | Up 18 hours (unhealthy) | `0.0.0.0:4000->4000/tcp` |
| `mastodon-db` | `postgres:14-alpine` | Up 18 hours (healthy) | `5432/tcp` |
| `mastodon-redis` | `redis:7-alpine` | Up 18 hours (healthy) | `6379/tcp` |

*Note: Mastodon services are currently marked unhealthy but responding (502/200 intermittent).*

---

## 2. NETWORK ARCHITECTURE

**Primary Network:** `astro-network` (Driver: bridge, Subnet: 172.21.0.0/16)

**Connected Services:**
*   `vedastro-ui` (172.21.0.2)
*   `mastodon-nginx` (172.21.0.7)
*   `mastodon-web` (172.21.0.5)
*   `mastodon-streaming` (172.21.0.6)
*   `mastodon-db` (172.21.0.4)
*   `mastodon-redis` (172.21.0.3)

**Visibility Verification:**
*   `mastodon-nginx` CAN see `vedastro-ui` (Same network).

---

## 3. DATA PERSISTENCE (Volumes)

**Critical Database Volume:**
*   **Name:** `vadimarhipov_postgres14`
*   **Mount:** `/var/lib/postgresql/data` (inside container `mastodon-db`)

**Other Volumes:**
*   `vadimarhipov_mastodon_redis`
*   `vadimarhipov_public-system`
*   `vadimarhipov_minio_data` (Present but service stopped?)
*   `vadimarhipov_opensearch_data` (Present but service stopped?)

---

## 4. HARDWARE RESOURCES

**RAM:**
*   **Total:** 15 Gi
*   **Used:** 1.1 Gi
*   **Free:** 10 Gi (Available: 14 Gi)
*   *Status: Excellent. Plenty of room for OpenSearch/AI.*

**DISK:**
*   **Total:** 49 G
*   **Used:** 38 G (78%)
*   **Avail:** 12 G
*   *Status: Critical Watch. Only 12GB free. OpenSearch logs need rotation.*

---

## 5. ARCHITECTURAL SUMMARY

**Astro Stack:**
*   **Library:** `jyotishganit` (Python Native)
*   **Interface:** Streamlit (Python)
*   **Calculation:** Direct execution (No external API container).

**Nginx Configuration:**
*   **Main:** `https://star-meet.com` -> `mastodon-web:3000`
*   **Astro:** `https://star-meet.com/astro/` -> `vedastro-ui:8501`
*   **Config Path:** `~/nginx/nginx.conf` (Mapped to `/etc/nginx/nginx.conf`)

**Project Files:**
*   Root: `/home/vadimarhipov`
*   Compose Files: `docker-compose.yml` (Main), `docker-compose.astro.yml` (Astro UI).
