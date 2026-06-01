# Say it in English — Local Dev Setup

## Быстрый старт

```bash
# 1. Клонировать репо
git clone https://github.com/anpoliakov/say-it-in-English.git
cd say-it-in-English

# 2. Создать .env (из примера)
cp .env.example .env

# 3. Поднять всё
make up
# или: docker compose up --build -d
```

## Адреса

| Сервис | URL |
|---|---|
| Frontend (игра) | http://localhost:3000 |
| API (FastAPI docs) | http://localhost:8000/docs |
| MinIO (S3 UI) | http://localhost:9001 |
| PostgreSQL | localhost:5432 |

## Полезные команды

```bash
make logs          # логи всех контейнеров
make shell-backend # bash внутри backend
make shell-db      # psql внутри postgres
make reset         # снести всё + пересобрать (данные удалятся!)
```

## Структура

```
├── docker-compose.yml
├── .env.example
├── frontend/          # Nginx + index.html (Mini App)
├── backend/           # FastAPI
│   ├── main.py
│   ├── models.py      # SQLAlchemy ORM
│   ├── auth.py        # Dev stub / Telegram initData
│   ├── storage.py     # MinIO wrapper
│   └── routers/
│       ├── words.py   # CRUD слов + загрузка картинок
│       └── users.py
└── postgres/
    └── init.sql
```

## Dev режим (заглушка авторизации)

В `.env` стоит `DEV_MODE=true` — все запросы автоматически идут
от имени dev-пользователя. Не нужен Telegram.

Когда будешь подключать бота:
1. Вставь `TELEGRAM_BOT_TOKEN=...` в `.env`
2. Поставь `DEV_MODE=false`
3. Frontend начнёт передавать `X-Tg-Init-Data` заголовок

## API Endpoints

```
GET    /api/words              — список слов пользователя
POST   /api/words              — добавить слово (+ опционально картинка)
DELETE /api/words/{id}         — удалить слово
PATCH  /api/words/{id}/image   — обновить картинку слова
GET    /api/users/me           — текущий пользователь
GET    /health                 — health check
```
