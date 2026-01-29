#!/bin/bash
set -o errexit

echo "=== Starting Build ==="
echo "Python version:"
python --version

echo "\n=== Installing dependencies ==="
pip install -r requirements.txt

echo "\n=== Database Configuration ==="
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL environment variable is NOT set!"
  echo "This will cause SQLite to be used instead of PostgreSQL."
  exit 1
else
  echo "✓ DATABASE_URL is set"
  echo "Database: $(echo $DATABASE_URL | cut -d'@' -f2)"
fi

echo "\n=== Waiting for database to be ready ==="
sleep 15

echo "\n=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "\n=== Running migrations ==="
python manage.py migrate --noinput

echo "\n=== Build completed successfully ==="
