# Django Boilerplate

Production-ready шаблон для создания API-приложений на Django.

**Стек:** Python 3.13 · Django 6.0 · DRF 3.17 · PostgreSQL · Redis · uv · Docker

## Возможности

- **API-first монолит** с разделением на слои: views → services/selectors → models.
- **Версионирование API через заголовок** (`AcceptHeaderVersioning`) — версия не загрязняет URL.
- **OpenAPI-документация** из коробки (drf-spectacular): Swagger UI и ReDoc.
- **12-factor конфигурация** через переменные окружения (`django-environ`) и разделение настроек dev/prod (`django-split-settings`).
- **Production-настройки по умолчанию**: HSTS, secure cookies, SSL redirect, манифестная статика через whitenoise, gunicorn.
- **Кастомная модель пользователя** с email-логином и `external_id` (UUID) для внешних интеграций.
- **Health-check** (`/health/`) с проверкой БД и Redis — готов для Kubernetes liveness/readiness probes.
- **Качество кода**: ruff (lint + format), bandit, ty, pre-commit, pytest, GitHub Actions CI.
- **Docker**: multi-stage Dockerfile (non-root user), docker-compose с PostgreSQL и Redis.

## Быстрый старт

### Docker (рекомендуется)

```bash
make env        # создать .env из .env.example
make up         # собрать и запустить postgres + redis + django
make logs       # смотреть логи
```

Приложение: http://localhost:8000, Swagger UI: http://localhost:8000/api/docs/

### Локально

```bash
make env
make install    # uv sync --group dev
make migrate
make run
```

По умолчанию локально используется SQLite; для PostgreSQL задайте `DATABASE_URL` в `.env`.

## Версионирование API

Используется `AcceptHeaderVersioning`: клиент передаёт версию в заголовке `Accept`,
URL остаются стабильными (`/api/users/...` без `/v1/`).

```bash
# Явно указанная версия
curl http://localhost:8000/api/users/me/ \
  -H 'Accept: application/json; version=v1'

# Без версии — используется DEFAULT_VERSION (v1)
curl http://localhost:8000/api/users/me/

# Неподдерживаемая версия → 406 Not Acceptable
curl http://localhost:8000/api/users/me/ \
  -H 'Accept: application/json; version=v999'
```

Версия доступна во view через `request.version`. Список поддерживаемых версий —
`ALLOWED_VERSIONS` в `config/settings/base.py`. Чтобы выпустить `v2`, добавьте версию
в `ALLOWED_VERSIONS` и ветвите логику по `request.version` (или подключайте другой
сериализатор), не меняя URL.

## Эндпоинты

| URL | Описание |
| --- | --- |
| `POST /api/users/register/` | Регистрация пользователя |
| `GET /api/users/me/` | Профиль текущего пользователя |
| `GET /api/schema/` | OpenAPI-схема |
| `GET /api/docs/` | Swagger UI |
| `GET /api/redoc/` | ReDoc |
| `GET /health/` | Health-check (БД + Redis), 503 при сбое |
| `/admin/` | Django admin |

## Команды

```bash
make install         # установить зависимости (с dev-группой)
make run             # запустить dev-сервер
make migrate         # применить миграции
make makemigrations  # создать миграции
make superuser       # создать суперпользователя
make test            # запустить тесты
make lint            # ruff check + format check + bandit
make format          # автоформатирование
make up / down       # docker compose up/down
```

## Структура проекта

```
├── apps/                  # Бизнес-модули (изолированные приложения)
│   └── users/
│       ├── api/           # Слой API: serializers, views, urls
│       ├── services.py    # Бизнес-логика (запись)
│       ├── selectors.py   # Бизнес-логика (чтение)
│       ├── models.py
│       └── tests/
├── commons/               # Переиспользуемый код (mixins, redis-клиент)
├── config/                # Конфигурация проекта
│   ├── settings/          # base.py + dev.py / prod.py (split-settings)
│   ├── urls.py
│   └── views.py           # health-check
├── externals/             # Клиенты внешних сервисов
├── docs/styleguide/       # Соглашения по коду
├── Dockerfile             # Multi-stage, non-root
├── docker-compose.yml     # postgres + redis + django
└── pyproject.toml         # Зависимости (uv), ruff, bandit, pytest
```

## Конфигурация

Все настройки — через переменные окружения (см. `.env.example`). Ключевые:

| Переменная | Назначение | По умолчанию |
| --- | --- | --- |
| `ENVIRONMENT` | `dev` или `prod` (выбор настроек) | `dev` |
| `DJANGO_SECRET_KEY` | Секретный ключ (обязателен) | — |
| `DJANGO_DEBUG` | Режим отладки | `False` (prod), `True` (dev) |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты через запятую | — |
| `DATABASE_URL` | URL базы данных | SQLite |
| `REDIS_URL` | URL Redis для кэша | `redis://redis:6379/1` |
| `GUNICORN_WORKERS` | Количество воркеров gunicorn | `4` |

### Production

`ENVIRONMENT=prod` включает: `DEBUG=False`, SSL redirect, HSTS, secure cookies,
JSON-only рендеринг DRF, манифестную статику (whitenoise) и запуск через gunicorn
(`MODE=prod` в docker-compose).

```bash
ENVIRONMENT=prod MODE=prod INSTALL_DEV=false docker compose up -d --build
```

## Архитектура

Проект построен как **монолитное API-ориентированное приложение** (API-first Monolith)
по стандартам **Twelve-Factor App**. Бизнес-функционал инкапсулирован в изолированные
приложения внутри `apps/` — каждый модуль проектируется как независимый компонент,
что облегчает будущий вынос в микросервисы.

Слои:

1. **API (Interface Layer)** — DRF views валидируют ввод/вывод, не содержат бизнес-правил.
2. **Бизнес-логика (Domain Layer)** — services (запись) и selectors (чтение) внутри приложений.
3. **Данные (Persistence Layer)** — PostgreSQL, миграции Django.

Подробнее — в `docs/styleguide/`.

## Качество кода

```bash
uv run pre-commit install   # включить pre-commit хуки
make lint                   # проверка
make test                   # тесты
```

CI (GitHub Actions) запускает линтеры и тесты на каждый push в `main` и pull request.
