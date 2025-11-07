# 🌟 Astro-VC Platform

**AI-powered VC matching platform using Vedic astrology and LLM**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org)

---

## 📋 О проекте

**Astro-VC** — это глобальная VC-инфраструктура, которая использует гибридный AI (VedAstro + AstroSage-LLaMA) и эзотерические системы для умного мэтчинга:
- Стартапов и инвесторов
- Кофаундеров
- Менторов

**Цель**: Увеличить успешность венчурных инвестиций до >50% за счет подбора "синергетических" команд.

### Ключевые возможности

- ⭐ **AI-скоринг потенциала** (1-10 баллов по 30 критериям)
- 🔮 **Обязательная ректификация** (AI + астролог)
- 🤝 **Мэтчинг кофаундеров** (дополнение слабых сторон)
- 💼 **Формирование синдикатов** (группы из 5 совместимых инвесторов)
- 📊 **Синастрия** (глубокий анализ совместимости)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────┐
│   Frontend (React + TypeScript)         │
│   • Vite • Tailwind CSS • React Query   │
└────────────────┬────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────┐
│   Backend (FastAPI + Python)            │
│   • VedAstro Engine                     │
│   • AstroSage-LLaMA (8B)                │
│   • OpenSearch RAG                      │
│   • PostgreSQL                          │
└─────────────────────────────────────────┘
```

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, VedAstro, AstroSage-LLaMA, OpenSearch
- Frontend: React 18, TypeScript, Vite, Tailwind CSS
- Database: PostgreSQL 15+
- AI: Llama.cpp, OpenSearch для RAG

---

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (опционально для разработки)
- Git

### 1. Клонирование репозитория

```bash
git clone https://github.com/YOUR_USERNAME/astro-vc-platform.git
cd astro-vc-platform
```

### 2. Backend Setup

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # macOS/Linux
# или
venv\\Scripts\\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Отредактировать .env с вашими настройками

# Запустить сервер
python -m app.main
# или
uvicorn app.main:app --reload
```

Backend будет доступен по адресу: http://localhost:8000

API документация: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Установить зависимости
npm install

# Создать .env файл
cp .env.example .env

# Запустить dev server
npm run dev
```

Frontend будет доступен по адресу: http://localhost:3000

---

## 📁 Структура проекта

```
astro-vc-platform/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # REST endpoints
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Business logic
│   │   │   ├── vedastro_engine.py
│   │   │   ├── llm_engine.py
│   │   │   └── opensearch_rag.py
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/          # API clients
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── README.md
│
├── docs/                       # Documentation
│   ├── STRATEGY.md            # Business strategy
│   ├── ARCHITECTURE.md        # Technical architecture
│   └── API.md                 # API documentation
│
├── CLAUDE.md                  # Context for Claude AI
├── .gitignore
└── README.md                  # This file
```

---

## 🔧 Разработка

### Backend Commands

```bash
cd backend

# Запустить сервер с hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запустить тесты
pytest tests/

# Проверка типов
mypy app/

# Форматирование кода
black app/

# Линтинг
flake8 app/
```

### Frontend Commands

```bash
cd frontend

# Dev server
npm run dev

# Build для production
npm run build

# Preview production build
npm run preview

# Тесты
npm run test

# Линтинг
npm run lint
```

---

## 🌐 API Endpoints

### Health Check
```
GET /health
Response: {status: "healthy", version: "0.1.0"}
```

### Rate Potential
```
POST /api/v1/rate-potential
Body: {
  "name": "John Doe",
  "date": "1990-01-15",
  "time": "14:30:00",
  "latitude": 28.7041,
  "longitude": 77.1025,
  "timezone": 5.5,
  "gender": "Male"
}
Response: {
  "success": true,
  "score": 8,
  "explanation": "Strong planetary positions...",
  ...
}
```

Полная документация API: http://localhost:8000/docs

---

## 📚 Документация

- [📖 Стратегия проекта](docs/STRATEGY.md) — Бизнес-план и Go-to-Market
- [🏗️ Техническая архитектура](docs/ARCHITECTURE.md) — Tech Stack и дизайн системы
- [🔌 API Reference](docs/API.md) — Описание всех endpoints
- [🤖 CLAUDE.md](CLAUDE.md) — Контекст для Claude AI

---

## 🧪 Тестирование

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test
```

---

## 📦 Deployment

### Docker

```bash
# Build backend image
cd backend
docker build -t astro-vc-backend .

# Build frontend image
cd frontend
docker build -t astro-vc-frontend .

# Run with docker-compose
docker-compose up
```

### Google Cloud Run

```bash
# Deploy backend
gcloud run deploy astro-vc-backend \\
  --image gcr.io/PROJECT_ID/astro-vc-backend:latest \\
  --region europe-west1 \\
  --memory 8Gi --cpu 4

# Deploy frontend
gcloud run deploy astro-vc-frontend \\
  --image gcr.io/PROJECT_ID/astro-vc-frontend:latest \\
  --region europe-west1
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is proprietary and confidential.

---

## 👥 Team

- **Founder**: Vadim Arhipov
- **Contact**: vadim@edestory.ai

---

## 🔗 Links

- **Website**: Coming soon
- **Documentation**: [docs/](docs/)
- **API Docs**: http://localhost:8000/docs (dev)

---

## 📊 Roadmap

### Q1 2026: MVP (Pre-seed)
- ✅ VedAstro integration
- ✅ AstroSage-LLaMA integration
- ✅ AI-скоринг (30 критериев)
- ✅ Ректификация (AI + астролог)
- ⏳ Первые 10 стартапов

### Q2 2026: Seed Round
- ⏳ Привлечение $1-2M
- ⏳ 50+ стартапов
- ⏳ 200+ инвесторов
- ⏳ Запуск синдикатов

### Q3-Q4 2026: Scale
- ⏳ Автоматизация ректификации
- ⏳ Fine-tuning LLM
- ⏳ Расширение на США и Европу

---

**Версия**: 0.1.0
**Дата**: 7 ноября 2025
**Статус**: В разработке (MVP)
