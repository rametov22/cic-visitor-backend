#!/usr/bin/env bash
set -euo pipefail

echo ">>> Compiling translations..."
python manage.py compilemessages

echo ">>> Applying database migrations..."
python manage.py migrate --no-input

echo ">>> Checking storage..."
python manage.py wait_for_storage

echo ">>> Collecting static files..."
python manage.py collectstatic --no-input

echo ">>> Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --name "${DJANGO_APP_NAME:-cic-visitor}" \
    --workers "${GUNICORN_WORKERS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT:-30}" \
    --worker-tmp-dir /dev/shm \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
