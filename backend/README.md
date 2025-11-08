# Astro-VC Backend

FastAPI backend for Astro-VC Platform with VedAstro integration.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional for development, required for production)
- PostgreSQL 15+ (optional for development)

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Test VedAstro installation**
   ```bash
   python test_vedastro.py
   ```

   Expected output:
   ```
   ✅ VedAstro imported successfully
   ✅ Birth chart calculation successful!
   ✅ Redis connection successful (if Redis is running)
   ```

5. **Run development server**
   ```bash
   uvicorn app.main:app --reload
   ```

   API will be available at: http://localhost:8000
   API docs: http://localhost:8000/docs

## 🐳 Docker Development

### Using Docker Compose (Recommended)

1. **Start all services** (Backend + PostgreSQL + Redis)
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f backend
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

### Services

- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Redis Commander** (GUI): http://localhost:8081

## 📚 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── api/                         # API routes
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── rating.py            # ✅ Rating endpoint (IMPLEMENTED)
│   ├── core/                        # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py               # Settings management
│   │   └── dependencies.py         # FastAPI dependencies
│   ├── models/                      # Pydantic models
│   │   ├── __init__.py
│   │   ├── birth_data.py           # ✅ Birth data input model
│   │   ├── birth_chart.py          # ✅ Birth chart response (NEW)
│   │   └── rating.py               # ✅ Rating response model
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── vedastro_engine.py      # ✅ VedAstro wrapper (NEW)
│   │   └── scoring.py              # ✅ AI scoring system (NEW)
│   │   ├── vedastro_engine.py  # VedAstro integration
│   │   ├── cache.py           # Redis caching
│   │   └── llm_engine.py      # LLM integration
│   └── db/                     # Database
│       ├── __init__.py
│       └── models.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_vedastro_engine.py
│   └── test_api_astrology.py
├── .env.example                # Environment template
├── .env                        # Your environment (gitignored)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image
├── test_vedastro.py           # Installation test
└── README.md                   # This file
```

## 🧪 Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_vedastro_engine.py -v
```

## 🔧 Development Commands

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📖 API Endpoints (Phase 2 - IMPLEMENTED)

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "vedastro_ready": true,
  "redis_ready": true,
  "llm_ready": false
}
```

---

### ✅ Rating API (Potential Scoring)

**Endpoint:** `POST /api/v1/rating`

**Description:** Оценка потенциала основателя стартапа на основе натальной карты (1-10 баллов)

**Request Body:**
```json
{
  "name": "Steve Jobs",
  "date": "1955-02-24",
  "time": "19:15:00",
  "latitude": 37.77,
  "longitude": -122.42,
  "timezone": -8.0,
  "gender": "Male"
}
```

**Response:**
```json
{
  "success": true,
  "score": 8,
  "score_max": 10,
  "explanation": "Potential Score: 8.5/10\n\nTop Strengths:\n  • Sun (Leadership): 8.0/10 - Sun in Pisces, House 10 - authority & power\n  • 10th House (Career): 7.5/10 - 10th house in Aquarius - professional success\n  • Jupiter Placement: 7.0/10 - Jupiter in Cancer, House 2 - expansion & wealth\n\nRecommendations:\n  Excellent potential. High probability of success.",
  "person_name": "Steve Jobs",
  "chart_data": {
    "person_name": "Steve Jobs",
    "birth_datetime": "1955-02-24T19:15:00",
    "planets": {
      "Sun": {
        "name": "Sun",
        "longitude": 335.8,
        "zodiac_sign": "Pisces",
        "house": 10,
        "shadbala": 420.5,
        "is_retrograde": false
      },
      "Moon": { /* ... */ }
    },
    "houses": { /* ... */ },
    "ascendant": "Gemini",
    "current_dasa": {
      "planet": "Jupiter",
      "start_date": "2020-01-01",
      "end_date": "2036-01-01",
      "level": "Maha"
    }
  },
  "error": null
}
```

**Curl Example:**
```bash
curl -X POST http://localhost:8000/api/v1/rating \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "date": "1990-08-15",
    "time": "14:30:00",
    "latitude": 55.75,
    "longitude": 37.62,
    "timezone": 3.0,
    "gender": "Male"
  }'
```

**Scoring Criteria (30 total):**
- **Денежный потенциал (30%):** 2nd house, 11th house, Jupiter, Mercury, Venus
- **Лидерство (25%):** Sun, 10th house, Mars, Ascendant lord
- **Удача и своевременность (20%):** 9th house, Current Dasa, Jupiter/Saturn transits
- **Инновации (15%):** 5th house, Rahu/Ketu axis
- **Стрессоустойчивость (10%):** Moon strength, Saturn maturity

---

### API Info
```http
GET /api/v1/
```

**Full interactive documentation:** http://localhost:8000/docs (Swagger UI)

## 🌐 Environment Variables

Key environment variables:

```bash
# Application
DEBUG=True
PORT=8000

# VedAstro
VEDASTRO_API_KEY=FreeAPIUser  # Use "FreeAPIUser" for free tier

# Redis (optional for dev)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=86400  # 24 hours

# Database (optional for dev)
DATABASE_URL=postgresql://user:password@localhost:5432/astrovc
```

See `.env.example` for full list.

## 🐛 Troubleshooting

### VedAstro import fails

**Error**: `ModuleNotFoundError: No module named 'vedastro'`

**Solution**:
```bash
pip install vedastro==1.0.6
```

### Redis connection error

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution**:
- Check if Redis is running: `redis-cli ping`
- Start Redis: `redis-server` (or use Docker Compose)
- Or disable Redis caching in `.env`: Comment out Redis settings

### Port already in use

**Error**: `[Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

## 📝 Notes

- VedAstro free tier: 5 API calls/minute
- For production, use Redis caching to reduce API calls
- Set `VEDASTRO_API_KEY` to your paid key for unlimited calls

## 🔗 Resources

- [VedAstro Documentation](https://github.com/VedAstro/VedAstro)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Redis Documentation](https://redis.io/docs)
