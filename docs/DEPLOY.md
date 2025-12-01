# DEPLOY.md — StarMeet Production Deployment

**Date:** 2025-11-28
**Server:** GCP VM (mastodon-vm)
**Domain:** star-meet.com

---

## Pre-Deploy Checklist

- [x] docker-compose.yml готов (Supabase stack)
- [x] nginx.conf обновлён для Supabase routing
- [x] .env.production создан с секретами
- [x] database/schema.sql готов
- [x] supabase/kong.yml готов
- [ ] Локальное тестирование (опционально)

---

## Шаг 1: Подключение к серверу

```bash
gcloud compute ssh mastodon-vm --zone=europe-southwest1-c
```

---

## Шаг 2: Остановка старого стека

```bash
cd ~
docker compose down
docker system prune -f
```

---

## Шаг 3: Обновление файлов

### Вариант A: Git pull (рекомендуется)

```bash
cd ~/StarMeet-platform
git pull origin main
```

### Вариант B: SCP (если git не настроен)

С локальной машины:
```bash
# Копируем файлы на сервер
gcloud compute scp docker-compose.yml mastodon-vm:~/
gcloud compute scp -r database/ mastodon-vm:~/
gcloud compute scp -r supabase/ mastodon-vm:~/
gcloud compute scp -r nginx/ mastodon-vm:~/
gcloud compute scp .env.production mastodon-vm:~/.env
```

---

## Шаг 4: Создание .env на сервере

```bash
# Скопировать .env.production как .env
cp .env.production .env

# Проверить содержимое
cat .env
```

---

## Шаг 5: Запуск нового стека

```bash
# Создать сеть если её нет
docker network create starmeet-network 2>/dev/null || true

# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps
```

**Ожидаемый результат:**
```
NAME               STATUS    PORTS
starmeet-db        healthy   5432/tcp
starmeet-redis     healthy   6379/tcp
starmeet-kong      running   127.0.0.1:8001->8000/tcp
starmeet-auth      running   9999/tcp
starmeet-rest      running   3000/tcp
starmeet-realtime  running   4000/tcp
starmeet-wizard    healthy   127.0.0.1:3001->3001/tcp
starmeet-nginx     running   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

---

## Шаг 6: Инициализация базы данных

```bash
# Подключиться к PostgreSQL
docker exec -it starmeet-db psql -U postgres -d starmeet

# Внутри psql выполнить:
\i /docker-entrypoint-initdb.d/01-schema.sql

# Проверить таблицы
\dt

# Выйти
\q
```

**Ожидаемые таблицы:**
- profiles
- compatibility_cache
- matches
- messages

---

## Шаг 7: Проверка в браузере

| URL | Ожидание |
|-----|----------|
| https://star-meet.com | Редирект на /join |
| https://star-meet.com/join | Калькулятор |
| https://star-meet.com/login | Форма входа |
| https://star-meet.com/signup | Форма регистрации |
| https://star-meet.com/dashboard | Дашборд (редирект на login если не залогинен) |

---

## Шаг 8: Тест auth flow

1. Открыть https://star-meet.com/signup
2. Создать аккаунт
3. Войти через /login
4. Перейти на /dashboard
5. Открыть калькулятор (/join)
6. Рассчитать карту
7. Нажать "Сохранить профиль"
8. Проверить что профиль появился в /dashboard

---

## Troubleshooting

### Логи сервисов

```bash
# Все логи
docker compose logs -f

# Конкретный сервис
docker compose logs -f starmeet-wizard
docker compose logs -f starmeet-auth
docker compose logs -f starmeet-kong
```

### Перезапуск сервиса

```bash
docker compose restart starmeet-wizard
```

### Пересборка wizard

```bash
docker compose up -d --build wizard
```

### Проверка БД

```bash
docker exec -it starmeet-db psql -U postgres -d starmeet -c "SELECT * FROM profiles LIMIT 5;"
```

### SSL сертификаты

Если сертификаты истекли:
```bash
certbot renew
docker compose restart starmeet-nginx
```

---

## Rollback

Если что-то пошло не так:

```bash
# Вернуть старый docker-compose
mv docker-compose.yml docker-compose.new.yml
mv docker-compose.old.yml docker-compose.yml

# Вернуть старый nginx
mv nginx/nginx.conf nginx/nginx.new.conf
mv nginx/nginx.old.conf nginx/nginx.conf

# Перезапустить
docker compose down
docker compose up -d
```

---

## После успешного деплоя

1. Удалить старые файлы:
```bash
rm docker-compose.old.yml
rm nginx/nginx.old.conf
```

2. Сделать коммит:
```bash
git add -A
git commit -m "feat(deploy): Supabase stack deployed to production"
git push origin main
```

---

**END OF DEPLOY.md**
