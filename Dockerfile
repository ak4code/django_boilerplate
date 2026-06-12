# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13

FROM ghcr.io/astral-sh/uv:0.11 AS uv


# ============================== builder ==============================
FROM python:${PYTHON_VERSION}-slim-trixie AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

# --locked гарантирует точное соответствие uv.lock (сборка падает при рассинхроне)
ARG INSTALL_DEV=false
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --locked --group dev; \
    else \
        uv sync --locked --no-group dev; \
    fi


# ============================== runtime ==============================
FROM python:${PYTHON_VERSION}-slim-trixie AS runtime

LABEL org.opencontainers.image.title="django-boilerplate" \
      org.opencontainers.image.description="Production-ready Django API boilerplate" \
      org.opencontainers.image.source="https://github.com/ak4code/django_boilerplate"

ARG UID=1000
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /usr/sbin/nologin --uid "${UID}" django \
    && install -d -o django -g django /app /app/staticfiles

ENV VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# venv принадлежит root: приложение не может модифицировать свои зависимости
COPY --from=builder /opt/venv /opt/venv
COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /app

USER django

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=4)"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["dev"]


# ============================= production ============================
FROM runtime AS production

COPY --chown=django:django . .

CMD ["prod"]
