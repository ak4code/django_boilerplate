<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:092E20,100:44B78B&height=200&section=header&text=Django%20Boilerplate&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Production-ready%20шаблон%20для%20API-приложений&descSize=18&descAlignY=55)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&pause=1000&color=44B78B&center=true&vCenter=true&width=600&lines=API-first+монолит+на+Django+6;Версионирование+API+через+заголовок+Accept;OpenAPI+%2B+Swagger+UI+из+коробки;Docker+%C2%B7+PostgreSQL+%C2%B7+Redis+%C2%B7+uv)](https://git.io/typing-svg)

[![CI](https://github.com/ak4code/django_boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/ak4code/django_boilerplate/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-8-FF4438?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)

</div>

---

## ✨ Возможности

| | |
| --- | --- |
| 🏗️ **API-first монолит** | Слои: views → services / selectors → models |
| 🔖 **Версионирование через заголовок** | `AcceptHeaderVersioning` — чистые URL без `/v1/` |
| 📖 **OpenAPI из коробки** | Swagger UI и ReDoc (drf-spectacular) |
| ⚙️ **12-factor конфигурация** | Всё через переменные окружения (django-environ) |
| 🔒 **Безопасный production** | HSTS, secure cookies, SSL redirect, whitenoise, gunicorn |
| 👤 **Кастомный пользователь** | Email-логин + `external_id` (UUID) для интеграций |
| 💓 **Health-check** | `/health/` с проверкой БД и Redis — готов для k8s-проб |
| 🧹 **Качество кода** | ruff · bandit · ty · pre-commit · pytest · GitHub Actions |
| 🐳 **Docker** | Multi-stage образ (non-root) + compose с PostgreSQL и Redis |

## 🚀 Быстрый старт

### 🐳 Docker (рекомендуется)

```bash
make env        # создать .env из .env.example
make up         # собрать и запустить postgres + redis + django
make logs       # смотреть логи
```

➜ Приложение: http://localhost:8000 · Swagger UI: http://localhost:8000/api/docs/

### 💻 Локально

```bash
make env
make install    # uv sync --group dev
make migrate
make run
```

> 💡 По умолчанию локально используется SQLite; для PostgreSQL задайте `DATABASE_URL` в `.env`.

## 🔖 Версионирование API

Используется `AcceptHeaderVersioning`: клиент передаёт версию в заголовке `Accept`,
URL остаются стабильными (`/api/users/...` без `/v1/`).

```bash
# ✅ Явно указанная версия
curl http://localhost:8000/api/users/me/ \
  -H 'Accept: application/json; version=v1'

# ✅ Без версии — используется DEFAULT_VERSION (v1)
curl http://localhost:8000/api/users/me/

# ❌ Неподдерживаемая версия → 406 Not Acceptable
curl http://localhost:8000/api/users/me/ \
  -H 'Accept: application/json; version=v999'
```

Версия доступна во view через `request.version`. Список поддерживаемых версий —
`ALLOWED_VERSIONS` в `config/settings/base.py`. Чтобы выпустить `v2`, добавьте версию
в `ALLOWED_VERSIONS` и ветвите логику по `request.version` (или подключайте другой
сериализатор), не меняя URL.

## 🌐 Эндпоинты

| Метод | URL | Описание |
| :---: | --- | --- |
| `POST` | `/api/users/register/` | 📝 Регистрация пользователя |
| `GET` | `/api/users/me/` | 👤 Профиль текущего пользователя |
| `GET` | `/api/schema/` | 📄 OpenAPI-схема |
| `GET` | `/api/docs/` | 📖 Swagger UI |
| `GET` | `/api/redoc/` | 📕 ReDoc |
| `GET` | `/health/` | 💓 Health-check (БД + Redis), 503 при сбое |
| — | `/admin/` | 🛠️ Django admin |

## 🏛️ Архитектура

Монолитное API-ориентированное приложение по стандартам **Twelve-Factor App**.
Бизнес-функционал инкапсулирован в изолированные приложения внутри `apps/` —
каждый модуль проектируется как независимый компонент, что облегчает будущий
вынос в микросервисы.

```mermaid
flowchart LR
    Client([🌍 Клиент]) -->|"Accept: application/json; version=v1"| API

    subgraph Django["🐍 Django Boilerplate"]
        direction LR
        API["🔌 API Layer<br/>(serializers, views)"] --> Domain["🧠 Domain Layer<br/>(services, selectors)"]
        Domain --> Models["🗃️ Models"]
    end

    Models --> PG[("🐘 PostgreSQL")]
    Domain --> RD[("⚡ Redis")]
```

## 📁 Структура проекта

Структура следует лучшим практикам ([HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide),
[cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django)) — три корневых пакета
с чёткими зонами ответственности:

```
├── 📂 apps/                  # Бизнес-приложения (изолированные модули)
│   └── users/
│       ├── api/              # Слой API: serializers, views, urls
│       ├── services.py       # Бизнес-логика (запись)
│       ├── selectors.py      # Бизнес-логика (чтение)
│       ├── models.py
│       └── tests/
├── ⚙️ config/                # Только конфигурация проекта
│   ├── settings/             # base.py + dev.py / prod.py (split-settings)
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── 🧰 core/                  # Переиспользуемый инфраструктурный код
│   ├── health.py             # Health-check view
│   ├── integrations/         # Клиенты внешних сервисов
│   ├── mixins/               # Примеси для моделей (timestamps и т.п.)
│   └── redis/                # Redis-клиент
├── 🐳 Dockerfile             # Multi-stage, non-root
├── 🐳 docker-compose.yml     # postgres + redis + django
└── 📦 pyproject.toml         # Зависимости (uv), ruff, bandit, pytest
```

| Пакет | Ответственность | Правило |
| --- | --- | --- |
| `apps/` | Бизнес-логика | Может импортировать `core/`, но не `config/` |
| `core/` | Инфраструктура, переиспользуемый код | Не знает о бизнес-логике |
| `config/` | Настройки, маршрутизация, WSGI/ASGI | Только конфигурация, без логики |

## 🛠️ Команды

```bash
make install         # 📦 установить зависимости (с dev-группой)
make run             # 🚀 запустить dev-сервер
make migrate         # 🗃️ применить миграции
make makemigrations  # 📝 создать миграции
make superuser       # 👑 создать суперпользователя
make test            # 🧪 запустить тесты
make lint            # 🔍 ruff check + format check + bandit
make format          # ✨ автоформатирование
make up / down       # 🐳 docker compose up/down
```

## ⚙️ Конфигурация

Все настройки — через переменные окружения (см. [`.env.example`](.env.example)).

<details>
<summary><b>📋 Ключевые переменные окружения</b></summary>

<br/>

| Переменная | Назначение | По умолчанию |
| --- | --- | --- |
| `ENVIRONMENT` | `dev` или `prod` (выбор настроек) | `dev` |
| `DJANGO_SECRET_KEY` | Секретный ключ (обязателен) | — |
| `DJANGO_DEBUG` | Режим отладки | `False` (prod), `True` (dev) |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты через запятую | — |
| `DATABASE_URL` | URL базы данных | SQLite |
| `REDIS_URL` | URL Redis для кэша | `redis://redis:6379/1` |
| `DJANGO_LOG_LEVEL` | Уровень логирования | `INFO` |
| `GUNICORN_WORKERS` | Количество воркеров gunicorn | `4` |

</details>

<details>
<summary><b>🔒 Production-развёртывание</b></summary>

<br/>

`ENVIRONMENT=prod` включает: `DEBUG=False`, SSL redirect, HSTS, secure cookies,
JSON-only рендеринг DRF, манифестную статику (whitenoise) и запуск через gunicorn
(`MODE=prod` в docker-compose).

```bash
ENVIRONMENT=prod MODE=prod INSTALL_DEV=false docker compose up -d --build
```

</details>

## 🧹 Качество кода

```bash
uv run pre-commit install   # включить pre-commit хуки
make lint                   # проверка
make test                   # тесты
```

CI (GitHub Actions) запускает линтеры и тесты на каждый push в `main` и pull request.

<div align="center">

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:44B78B,100:092E20&height=120&section=footer)

</div>
