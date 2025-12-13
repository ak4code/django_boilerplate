ARG UID=1000
ARG PYTHON_VERSION=3.13.7

FROM python:${PYTHON_VERSION}-slim-trixie AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash builder
USER builder
WORKDIR /home/builder

COPY --chown=builder:builder --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv venv .venv
ENV PATH="/home/builder/.venv/bin:$PATH"

COPY --chown=builder:builder pyproject.toml uv.lock* ./

ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ] ; then \
        uv sync --group dev ; \
    else \
        uv sync --no-group dev ; \
    fi


FROM python:${PYTHON_VERSION}-slim-trixie AS runtime

RUN apt-get update && apt-get install -y \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash --uid ${UID:-1000} django
USER django
WORKDIR /home/django/app

COPY --from=builder --chown=django:django /home/builder/.venv /home/django/.venv

ENV VIRTUAL_ENV="/home/django/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --chown=django:django . .

RUN mkdir -p /home/django/logs /home/django/www

ENV PYTHONPATH=/home/django/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Entrypoint
COPY --chown=django:django entrypoint.sh /home/django/entrypoint.sh
RUN chmod +x /home/django/entrypoint.sh

ENTRYPOINT ["/home/django/entrypoint.sh"]

CMD ["dev"]
