# 🚀 Быстрое руководство: Astro-VC Platform

**Дата**: 7 ноября 2025
**Статус**: ✅ Проект полностью настроен и готов к разработке!

---

## ✅ Что уже сделано

1. ✅ **Создана полная структура проекта**
   - Backend (Python + FastAPI)
   - Frontend (React + TypeScript + Vite)
   - Документация (STRATEGY.md, ARCHITECTURE.md, README.md)

2. ✅ **GitHub репозиторий создан**
   - URL: https://github.com/Ede-story/astro-vc-platform
   - Публичный репозиторий
   - Initial commit выполнен

3. ✅ **VS Code Workspace настроен**
   - Файл: `~/My-Projects.code-workspace`
   - Содержит оба проекта: EdeStory E-commerce + Astro-VC
   - Должен открыться автоматически в VS Code

---

## 📂 Расположение файлов

```
~/astro-vc-platform/          # Новый проект Astro-VC
~/edestory-platform/          # Существующий проект E-commerce
~/My-Projects.code-workspace  # VS Code Workspace для обоих проектов
```

---

## 🎯 Как начать работу

### Вариант 1: Через VS Code Workspace (Рекомендуется)

1. **Откройте workspace** (если еще не открыт):
   ```bash
   open -a "Visual Studio Code" ~/My-Projects.code-workspace
   ```

2. **В VS Code вы увидите 2 папки:**
   - 🛍️ EdeStory E-commerce
   - 🌟 Astro-VC Platform

3. **Переключение между проектами:**
   - Используйте боковую панель Explorer
   - Или `Cmd+P` и начните вводить имя файла из нужного проекта

### Вариант 2: Отдельные окна VS Code

```bash
# Открыть проект E-commerce
code ~/edestory-platform

# Открыть проект Astro-VC (в новом окне)
code ~/astro-vc-platform
```

---

## 🔧 Настройка окружения

### 1. Backend Setup (Python)

```bash
cd ~/astro-vc-platform/backend

# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate  # macOS/Linux

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env

# Отредактировать .env (опционально)
nano .env
# или
code .env

# Запустить сервер
python -m app.main
# или
uvicorn app.main:app --reload
```

**Backend будет доступен:** http://localhost:8000
**API документация:** http://localhost:8000/docs

### 2. Frontend Setup (React)

```bash
cd ~/astro-vc-platform/frontend

# Установить зависимости
npm install

# Создать .env файл
cp .env.example .env

# Запустить dev server
npm run dev
```

**Frontend будет доступен:** http://localhost:3000

---

## 📚 Полезные команды

### Git Commands

```bash
# Проверить статус
cd ~/astro-vc-platform
git status

# Сделать commit
git add .
git commit -m "feat: add new feature"
git push origin main

# Посмотреть логи
git log --oneline
```

### VS Code Workspace

```bash
# Открыть workspace
open -a "Visual Studio Code" ~/My-Projects.code-workspace

# Или из терминала VS Code
code ~/My-Projects.code-workspace
```

### Переключение между терминалами

В VS Code workspace:
1. Откройте терминал: `Cmd+J` (macOS)
2. Нажмите `+` чтобы создать новый терминал
3. Выберите проект из dropdown (вверху справа в терминале)

---

## 🎨 Работа с Claude AI

### Важно: Контекст проекта

Каждый проект имеет свой **CLAUDE.md** файл:
- `~/edestory-platform/CLAUDE.md` — для E-commerce проекта
- `~/astro-vc-platform/CLAUDE.md` — для Astro-VC проекта

Claude автоматически прочитает правильный CLAUDE.md в зависимости от того, в какой папке вы работаете.

### Примеры запросов

```
# Для Astro-VC проекта
"Используя контекст из CLAUDE.md, создай API endpoint для ректификации"

# Для E-commerce проекта
"Используя контекст из CLAUDE.md, оптимизируй корпоративный сайт"
```

---

## 📁 Структура Astro-VC проекта

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
│   ├── .env.example
│   └── README.md
│
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/          # API clients
│   │   └── types/             # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── .env.example
│   └── README.md
│
├── docs/                       # Documentation
│   ├── STRATEGY.md            # Business strategy
│   └── ARCHITECTURE.md        # Technical architecture
│
├── CLAUDE.md                  # Context for Claude AI
├── README.md                  # Main documentation
├── QUICK_START_GUIDE.md       # This file
└── .gitignore
```

---

## 🔗 Полезные ссылки

### Проект
- **GitHub**: https://github.com/Ede-story/astro-vc-platform
- **Local Backend**: http://localhost:8000
- **Local Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Документация
- [📖 Бизнес-стратегия](docs/STRATEGY.md)
- [🏗️ Техническая архитектура](docs/ARCHITECTURE.md)
- [📝 README](README.md)
- [🤖 CLAUDE.md](CLAUDE.md)

---

## 🆘 Решение проблем

### Проблема: "command not found: python"
**Решение**: Используйте `python3` вместо `python`

### Проблема: VS Code не открывается
**Решение 1**: Откройте VS Code вручную и используйте File → Open Workspace
**Решение 2**: Установите `code` в PATH:
```bash
# Откройте VS Code
# Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"
```

### Проблема: pip install не работает
**Решение**: Убедитесь, что виртуальное окружение активировано:
```bash
source venv/bin/activate
which python  # Должен показать путь внутри venv/
```

### Проблема: npm install не работает
**Решение**: Проверьте версию Node.js:
```bash
node --version  # Должна быть 18+
npm --version   # Должна быть 9+
```

---

## ⏭️ Следующие шаги

1. **Изучите документацию:**
   - [STRATEGY.md](docs/STRATEGY.md) — Понять бизнес-модель
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Понять технологический стек

2. **Настройте окружение:**
   - Установите Python зависимости
   - Установите Node.js зависимости
   - Создайте .env файлы

3. **Начните разработку:**
   - Интеграция VedAstro API
   - Загрузка AstroSage-LLaMA модели
   - Создание первого API endpoint

4. **Тестируйте:**
   - Backend: `pytest tests/`
   - Frontend: `npm run test`

---

## 🎉 Готово!

Проект полностью настроен и готов к разработке.

У вас теперь есть:
- ✅ Отдельный GitHub репозиторий для Astro-VC
- ✅ Полная структура проекта (backend + frontend)
- ✅ Вся документация (стратегия, архитектура, инструкции)
- ✅ VS Code Workspace для удобной работы с обоими проектами
- ✅ Шаблоны конфигурации (.env.example)

**Следующий шаг**: Начните с интеграции VedAstro API!

---

**Создано**: Claude AI (Sonnet 4.5)
**Дата**: 7 ноября 2025
**Версия**: 1.0
