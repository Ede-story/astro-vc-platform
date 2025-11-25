# StarMeet Platform

**Social Network + Professional Astrology = AI-Driven Matching**

StarMeet is a unified ecosystem that merges a social network (Mastodon) with professional Vedic astrology calculations to enable intelligent user matching.

## Architecture

```
                    +------------------+
                    |     Nginx        |
                    |  (Reverse Proxy) |
                    +--------+---------+
                             |
            +----------------+----------------+
            |                                 |
   +--------v--------+              +---------v--------+
   |   Mastodon      |              |   Streamlit UI   |
   |   (Ruby/Rails)  |              |   (Python)       |
   |   Port 3000     |              |   Port 8501      |
   +--------+--------+              +---------+--------+
            |                                 |
            |         +------------+          |
            +-------->| PostgreSQL |<---------+
                      |   (Shared) |
                      +------------+
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Social Core | Mastodon v4.2.27 (Ruby on Rails) |
| Astro Engine | Python 3.9 + `jyotishganit` (MIT License) |
| Interface | Streamlit |
| Database | PostgreSQL 14 |
| Proxy | Nginx (Alpine) |
| Deployment | Docker Compose on GCP |

## URL Routing

- `https://star-meet.com` → Mastodon (Social Network)
- `https://star-meet.com/astro/` → Astrology UI (Streamlit)

## Quick Start

```bash
# SSH to server
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c

# Start all services
docker compose up -d

# Start Astro UI
docker compose -f docker-compose.astro.yml up -d

# Check status
docker compose ps
```

## Project Structure

```
.
├── CLAUDE.md              # AI agent instructions
├── CURRENT_INFRA.md       # Infrastructure snapshot
├── docker-compose.yml     # Main Mastodon services
├── docker-compose.astro.yml  # Astro UI service
├── nginx/
│   └── nginx.conf         # Reverse proxy config
└── vedastro-ui/
    ├── astro_test_ui.py   # Main Streamlit app
    ├── requirements.txt   # Python dependencies
    └── Dockerfile         # Container build
```

## Roadmap

- [x] Phase 0: Infrastructure (Mastodon + Nginx + PostgreSQL)
- [x] Phase 0.5: Astro UI with `jyotishganit`
- [ ] Phase 1: Connect Streamlit to PostgreSQL
- [ ] Phase 2: OAuth2 (Login with StarMeet)
- [ ] Phase 3: OpenSearch + AI Matching

## License

Proprietary - All rights reserved
