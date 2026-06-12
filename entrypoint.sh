#!/bin/bash
set -e

echo "Python: $(python --version) ($(which python))"

# Функция для ожидания готовности сервисов
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"

    echo "Ожидание готовности $service ($host:$port)..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service готов!"
}

# Ожидание зависимостей
if [ -n "$REDIS_URL" ]; then
    wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"
fi

if [ -n "$POSTGRES_HOST" ]; then
    wait_for_service "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}" "PostgreSQL"
fi

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --no-input

# Сбор статических файлов в продакшене
if [ "$1" = "prod" ] || [ "$ENVIRONMENT" = "prod" ]; then
    echo "Сбор статических файлов..."
    python manage.py collectstatic --no-input --clear
fi

# Запуск приложения в зависимости от команды
case "$1" in
    "dev")
        echo "Запуск в режиме разработки..."
        exec python manage.py runserver 0.0.0.0:8000
        ;;
    "prod")
        echo "Запуск в продакшн режиме..."
        exec gunicorn config.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers "${GUNICORN_WORKERS:-4}" \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --timeout 30 \
            --keep-alive 2 \
            --log-level info \
            --access-logfile - \
            --error-logfile -
        ;;
    "shell")
        echo "Запуск Django Shell..."
        exec python manage.py shell
        ;;
    "manage")
        shift
        echo "Выполнение manage.py команды: $@"
        exec python manage.py "$@"
        ;;
    *)
        echo "Выполнение пользовательской команды: $@"
        exec "$@"
        ;;
esac
