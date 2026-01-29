#!/bin/bash
set -o errexit

pip install -r requirements.txt

# Wait for database to be ready (PostgreSQL takes a moment to start)
echo "Waiting for database to be ready..."
sleep 10

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL not set! Using SQLite fallback."
  echo "Current database setting: $DATABASE_URL"
else
  echo "DATABASE_URL is set. Using PostgreSQL."
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput
