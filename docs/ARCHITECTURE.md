# Техническая архитектура: Astro-VC Platform

**Версия**: 1.0
**Дата**: 7 ноября 2025
**Статус**: Design Document

---

## 📋 Содержание
1. [Обзор системы](#обзор-системы)
2. [Tech Stack](#tech-stack)
3. [Архитектура компонентов](#архитектура-компонентов)
4. [Гибридная AI система](#гибридная-ai-система-vedastro--astrosage-llama)
5. [API Design](#api-design)
6. [База данных](#база-данных)
7. [Deployment](#deployment)
8. [Требования к оборудованию](#требования-к-оборудованию)

---

## Обзор системы

### Neuro-Symbolic AI Platform

Astro-VC — это **Neuro-Symbolic AI система**, объединяющая:
- **Символическое рассуждение** (VedAstro) — детерминированные математические расчеты
- **Нейронные сети** (LLM) — контекстное понимание и интерпретации

```
┌────────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                      │
│  Responsive UI │ Form Validation │ Real-time Updates           │
└────────────────────────┬───────────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────▼───────────────────────────────────────┐
│                   Backend (FastAPI + Python)                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  VedAstro       │  │  AstroSage-LLaMA │  │  OpenSearch  │ │
│  │  Engine         │→ │  Interpreter     │← │  RAG Store   │ │
│  └─────────────────┘  └──────────────────┘  └──────────────┘ │
│         │                      │                     │         │
│         └──────────────────────┼─────────────────────┘         │
│                                │                               │
│  ┌─────────────────────────────▼────────────────────────────┐ │
│  │              PostgreSQL Database                          │ │
│  │  Users │ Birth Data │ Ratings │ Matches │ Syndicates    │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend

```yaml
Language: Python 3.11+
Framework: FastAPI 0.104+

AI/Astrology:
  - VedAstro: Ведическая астрология (API/Python wrapper)
  - AstroSage-LLaMA: 8B модель для интерпретаций
  - llama-cpp-python: Локальный inference
  - Ollama: Альтернативный runtime для LLM

Search & RAG:
  - OpenSearch: Векторный поиск интерпретаций
  - langchain-opensearch: RAG интеграция
  - sentence-transformers: Embeddings

Database:
  - PostgreSQL 15+: Основная база данных
  - Prisma: ORM (опционально)
  - SQLAlchemy: Native Python ORM

Validation & Serialization:
  - Pydantic: Data validation
  - python-dotenv: Environment config

Testing:
  - pytest: Unit & integration tests
  - httpx: Async HTTP client для тестов
```

### Frontend

```yaml
Language: TypeScript 5+
Framework: React 18+
Build Tool: Vite 5+

UI/Styling:
  - Tailwind CSS: Utility-first CSS
  - shadcn/ui: Component library (опционально)
  - Radix UI: Headless components

State Management:
  - React Query (TanStack Query): Server state
  - Zustand: Client state (легкий)

API Client:
  - Axios: HTTP requests
  - TypeScript types from OpenAPI spec

Forms:
  - React Hook Form: Form management
  - Zod: Schema validation

Testing:
  - Vitest: Unit tests
  - Testing Library: Component tests
```

### AI/ML Infrastructure

```yaml
Models:
  - AstroSage-LLaMA-8B-GGUF: ~4GB (квантизованная)
  - VedAstro API: Облачный/локальный

Inference:
  - llama.cpp: C++ библиотека для быстрого inference
  - GPU: CUDA support (опционально)
  - CPU: Fallback для production

Training (Future):
  - Fine-tuning: Hugging Face Transformers
  - Dataset: Проприетарные астрологические интерпретации
  - Hardware: NVIDIA A100 / H100
```

### DevOps

```yaml
Containerization:
  - Docker: Multi-stage builds
  - Docker Compose: Local development

CI/CD:
  - GitHub Actions: Automated tests & deploy
  - Pre-commit hooks: Code quality

Cloud:
  - Google Cloud Platform:
      - Cloud Run: Serverless containers
      - Cloud Storage: Model storage
      - Cloud SQL: PostgreSQL
      - Cloud CDN: Static assets

Monitoring:
  - Prometheus: Metrics
  - Grafana: Dashboards
  - Sentry: Error tracking
```

---

## Архитектура компонентов

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Settings & environment variables
│   │
│   ├── api/                       # REST API endpoints
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── health.py          # Health check endpoint
│   │   │   ├── rating.py          # /rate-potential endpoint
│   │   │   ├── rectification.py   # /rectify endpoint
│   │   │   ├── matching.py        # /match-cofounder endpoint
│   │   │   └── syndicates.py      # /syndicates endpoint
│   │   └── dependencies.py        # Dependency injection
│   │
│   ├── models/                    # Pydantic models
│   │   ├── __init__.py
│   │   ├── birth_data.py          # BirthData model
│   │   ├── rating.py              # Rating response model
│   │   ├── user.py                # User models
│   │   └── matching.py            # Matching models
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── vedastro_engine.py     # VedAstro calculations
│   │   ├── llm_engine.py          # AstroSage-LLaMA integration
│   │   ├── opensearch_rag.py      # RAG for interpretations
│   │   ├── scoring.py             # Scoring logic (30 criteria)
│   │   ├── synastry.py            # Compatibility analysis
│   │   └── rectification.py       # Time rectification AI
│   │
│   ├── core/                      # Core utilities
│   │   ├── __init__.py
│   │   ├── database.py            # Database connection
│   │   ├── logging.py             # Logging setup
│   │   └── cache.py               # Redis cache (optional)
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   └── repositories/          # Data access layer
│   │       ├── user_repo.py
│   │       ├── rating_repo.py
│   │       └── matching_repo.py
│   │
│   └── utils/                     # Helper functions
│       ├── __init__.py
│       ├── validators.py          # Custom validators
│       └── formatters.py          # Data formatters
│
├── tests/                         # Tests
│   ├── test_api.py
│   ├── test_vedastro.py
│   ├── test_llm.py
│   └── test_scoring.py
│
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Poetry config (optional)
├── Dockerfile                     # Docker image
└── README.md
```

### Frontend Structure

```
frontend/
├── src/
│   ├── main.tsx                   # Entry point
│   ├── App.tsx                    # Root component
│   │
│   ├── components/                # Reusable components
│   │   ├── ui/                    # UI primitives (shadcn/ui)
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── ...
│   │   ├── forms/
│   │   │   ├── BirthDataForm.tsx  # Main input form
│   │   │   ├── RectificationForm.tsx
│   │   │   └── LocationPicker.tsx
│   │   ├── results/
│   │   │   ├── RatingDisplay.tsx  # Score visualization
│   │   │   ├── ChartVisualization.tsx
│   │   │   └── MatchList.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── pages/                     # Page components
│   │   ├── Home.tsx
│   │   ├── Rating.tsx
│   │   ├── Matching.tsx
│   │   ├── Dashboard.tsx
│   │   └── Profile.tsx
│   │
│   ├── services/                  # API clients
│   │   ├── api.ts                 # Axios instance
│   │   ├── ratingService.ts       # Rating API
│   │   ├── matchingService.ts     # Matching API
│   │   └── authService.ts         # Authentication
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useRating.ts
│   │   ├── useMatching.ts
│   │   └── useAuth.ts
│   │
│   ├── types/                     # TypeScript types
│   │   ├── api.ts                 # API response types
│   │   ├── models.ts              # Domain models
│   │   └── index.ts
│   │
│   ├── store/                     # State management
│   │   ├── authStore.ts           # Zustand store
│   │   └── uiStore.ts
│   │
│   ├── utils/                     # Helper functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   └── styles/                    # Global styles
│       ├── index.css              # Tailwind imports
│       └── globals.css
│
├── public/                        # Static assets
├── package.json
├── tsconfig.json                  # TypeScript config
├── vite.config.ts                 # Vite config
├── tailwind.config.js             # Tailwind config
└── README.md
```

---

## Гибридная AI система: VedAstro + AstroSage-LLaMA

### Почему Neuro-Symbolic?

```yaml
VedAstro обеспечивает:
  ✅ Точные математические расчеты (позиции планет, дома, аспекты)
  ✅ Детерминированную логику без галлюцинаций
  ✅ Валидацию и структуру данных

AstroSage-LLaMA обеспечивает:
  ✅ Контекстное понимание и объяснения
  ✅ Нумерологический анализ
  ✅ Мягкие интерпретации и рекомендации
  ✅ Оценку потенциала (1-10 баллов)

Вместе они дают:
  ⚡ Надежность + Творчество
  ⚡ Точные данные + Понимание человека
  ⚡ Структурированность + Гибкость
```

### Поток данных

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INPUT: Birth Data                                            │
│    {date, time, latitude, longitude, timezone}                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ 2. VedAstro Engine: Математические расчеты                      │
│    • Позиции планет (Sun, Moon, Mars, Mercury, ...)            │
│    • Дома (1-12 houses)                                         │
│    • Аспекты (conjunctions, oppositions, trines)               │
│    • Shadbala (планетарная сила)                               │
│    • Йоги (специальные комбинации)                             │
│    OUTPUT: Структурированный JSON с астрологическими данными    │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ 3. OpenSearch RAG: Поиск контекста                              │
│    • Векторный поиск релевантных интерпретаций                  │
│    • Извлечение ТОП-3 наиболее релевантных объяснений           │
│    • Контекстуализация для LLM                                  │
│    OUTPUT: Список интерпретаций + embeddings                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ 4. Prompt Engineering: Формирование запроса к LLM               │
│    SYSTEM: "You are an expert Vedic astrologer..."             │
│    USER: Birth chart data + RAG context + Task                 │
│    FORMAT: Structured output (SCORE + EXPLANATION)             │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ 5. AstroSage-LLaMA: AI Интерпретация                           │
│    • Анализ планетарных позиций                                 │
│    • Оценка силы домов                                          │
│    • Учет транзитов                                             │
│    • Нумерологический анализ                                    │
│    • Генерация оценки 1-10                                      │
│    OUTPUT: {score: 8, explanation: "...", strengths: [...]}    │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ 6. Validator: Проверка и форматирование                         │
│    • Валидация score (1-10)                                     │
│    • Проверка длины объяснения                                  │
│    • Извлечение структурированных данных                        │
│    • Логирование для дообучения                                 │
│    OUTPUT: Финальный JSON response                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│ 7. Human Verification (Фаза 1: первые 2-3 года)                │
│    • Штатный астролог проверяет оценку                          │
│    • Корректирует при необходимости                             │
│    • Обратная связь для дообучения LLM                          │
│    • Сохранение в training dataset                              │
└─────────────────────────────────────────────────────────────────┘
```

### Пример кода интеграции

```python
# services/hybrid_astro_engine.py

class HybridAstroEngine:
    def __init__(self, llm_model, vedastro_engine, rag_engine):
        self.llm = llm_model
        self.vedastro = vedastro_engine
        self.rag = rag_engine

    async def rate_human_potential(self, birth_data: BirthData) -> RatingResponse:
        """
        Главный метод: оценивает потенциал человека 1-10
        """
        # ЭТАП 1: VedAstro расчеты
        chart_data = self.vedastro.calculate_birth_chart(birth_data)

        # ЭТАП 2: Извлечение читаемого резюме
        chart_summary = self.vedastro.extract_summary(chart_data)

        # ЭТАП 3: RAG - поиск интерпретаций
        rag_context = await self.rag.search_interpretation(chart_summary)

        # ЭТАП 4: Формирование промпта
        prompt = self._build_prompt(
            name=birth_data.name,
            chart_summary=chart_summary,
            rag_context=rag_context
        )

        # ЭТАП 5: LLM вызов
        llm_response = self.llm(prompt, max_tokens=512, temperature=0.7)

        # ЭТАП 6: Парсинг и валидация
        score, explanation = self._parse_llm_response(llm_response["choices"][0]["text"])

        return RatingResponse(
            success=True,
            score=score,
            score_max=10,
            explanation=explanation,
            chart_data=chart_data,
            person_name=birth_data.name
        )
```

---

## API Design

### REST API Endpoints

```yaml
Health Check:
  GET /health
  Response: {status: "healthy", models_loaded: true}

Rating:
  POST /api/v1/rate-potential
  Body: {name, date, time, latitude, longitude, timezone, gender}
  Response: {success, score, score_max, explanation, chart_data}

Rectification:
  POST /api/v1/rectify
  Body: {name, approximate_time, questionnaire: [...]}
  Response: {rectified_time, confidence, reasoning}

Matching:
  POST /api/v1/match-cofounder
  Body: {startup_id, criteria: {...}}
  Response: {matches: [{user_id, compatibility_score, explanation}]}

Synastry:
  POST /api/v1/synastry
  Body: {person1_id, person2_id, relationship_type}
  Response: {compatibility_score, strengths, challenges}

Syndicates:
  POST /api/v1/syndicates/create
  Body: {startup_id, investor_ids: [5 investors]}
  Response: {syndicate_id, collective_score, synergy_analysis}
```

### OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: Astro-VC API
  version: 1.0.0
  description: AI-powered VC matching platform using astrology

paths:
  /api/v1/rate-potential:
    post:
      summary: Rate human potential
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BirthData'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RatingResponse'

components:
  schemas:
    BirthData:
      type: object
      required: [name, date, time, latitude, longitude, timezone]
      properties:
        name:
          type: string
        date:
          type: string
          format: date
        time:
          type: string
          format: time
        latitude:
          type: number
        longitude:
          type: number
        timezone:
          type: number
        gender:
          type: string
          enum: [Male, Female]
```

---

## База данных

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'startup', 'investor', 'mentor'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Birth data table
CREATE TABLE birth_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    time TIME NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    timezone DECIMAL(4, 2) NOT NULL,
    rectified BOOLEAN DEFAULT FALSE,
    rectification_confidence DECIMAL(3, 2),
    chart_data JSONB, -- Хранение полного расчета VedAstro
    created_at TIMESTAMP DEFAULT NOW()
);

-- Ratings table
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    score INTEGER CHECK (score BETWEEN 1 AND 10),
    explanation TEXT,
    chart_summary JSONB,
    verified_by UUID REFERENCES users(id), -- Астролог, который верифицировал
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Matches table (кофаундеры, менторы)
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user1_id UUID REFERENCES users(id),
    user2_id UUID REFERENCES users(id),
    match_type VARCHAR(50), -- 'cofounder', 'mentor', 'investor'
    compatibility_score DECIMAL(4, 2),
    synastry_data JSONB,
    status VARCHAR(50), -- 'pending', 'accepted', 'rejected'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Syndicates table
CREATE TABLE syndicates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id UUID REFERENCES users(id),
    name VARCHAR(255),
    collective_score DECIMAL(4, 2),
    synergy_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Syndicate members
CREATE TABLE syndicate_members (
    syndicate_id UUID REFERENCES syndicates(id),
    investor_id UUID REFERENCES users(id),
    role VARCHAR(50), -- 'lead', 'member'
    PRIMARY KEY (syndicate_id, investor_id)
);
```

---

## Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

# Download LLM model
RUN mkdir -p /models
# Model будет скачиваться при первом запуске

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Google Cloud Run

```yaml
# deploy.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: astro-vc-backend
spec:
  template:
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/astro-vc-backend:latest
        resources:
          limits:
            memory: 8Gi
            cpu: 4
        env:
        - name: DATABASE_URL
          value: "postgresql://..."
        - name: OPENSEARCH_URL
          value: "https://..."
        - name: MODEL_PATH
          value: "/models/AstroSage-8B-Q8_0.gguf"
```

---

## Требования к оборудованию

### Development

```yaml
Минимум:
  CPU: 4 ядра
  RAM: 8 GB
  Disk: 20 GB SSD
  GPU: Не требуется

Рекомендуется:
  CPU: 8 ядер (Intel i7 / AMD Ryzen 7)
  RAM: 16 GB
  Disk: 50 GB NVMe SSD
  GPU: NVIDIA RTX 3060 (6GB VRAM) - опционально
```

### Production

```yaml
Backend Server:
  CPU: 16 ядер
  RAM: 32 GB
  Disk: 100 GB NVMe SSD
  GPU: NVIDIA A10 (24GB) или CPU-only

Database:
  CPU: 8 ядер
  RAM: 16 GB
  Disk: 200 GB SSD (с автоматическим scaling)

OpenSearch:
  CPU: 8 ядер
  RAM: 16 GB
  Disk: 100 GB SSD
```

---

**Версия**: 1.0
**Последнее обновление**: 7 ноября 2025
**Статус**: Design Document
**Следующий пересмотр**: После MVP
