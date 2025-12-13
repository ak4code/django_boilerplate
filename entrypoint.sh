#!/bin/bash
set -e

# Проверка виртуального окружения
echo "Проверка Python окружения:"
echo "Python path: $(which python)"
echo "Python version: $(python --version)"
echo "Virtual env: ${VIRTUAL_ENV:-'Используется PATH для активации venv'}"

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

# Ожидание Redis если он используется
if [ -n "$REDIS_URL" ]; then
    wait_for_service redis 6379 "Redis"
fi

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --no-input

# Сбор статических файлов в продакшене
if [ "$MODE" = "prod" ] || [ "$DEBUG" = "False" ]; then
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
        exec gunicorn core.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers 4 \
            --worker-class gevent \
            --worker-connections 1000 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --timeout 30 \
            --keep-alive 2 \
            --log-level info \
            --access-logfile - \
            --error-logfile -
        ;;
    "celery-worker")
        echo "Запуск Celery Worker..."
        exec celery -A core worker \
            --loglevel=info \
            --concurrency=4 \
            --max-tasks-per-child=1000 \
            --time-limit=300 \
            --soft-time-limit=240
        ;;
    "celery-beat")
        echo "Запуск Celery Beat..."
        # Удаление старого расписания если есть
        rm -f celerybeat.pid
        exec celery -A core beat \
            --loglevel=info \
            --scheduler django_celery_beat.schedulers:DatabaseScheduler
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
