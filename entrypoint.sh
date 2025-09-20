#!/usr/bin/env bash
set -e

# wait-for-db helper (optional) - simple loop (replace with robust tool in production)
if [ "$DATABASE_URL" ]; then
  echo "DATABASE_URL set — will attempt migrations"
fi

# migrate
echo "Running migrations..."
python manage.py migrate --noinput

# collectstatic
echo "Collecting static files..."
python manage.py collectstatic --noinput

# create superuser if env vars provided (optional)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput || echo "superuser exists or cannot create"
fi

exec "$@"
