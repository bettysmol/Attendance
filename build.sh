#!/bin/bash
set -o errexit

echo "=== Starting Build ==="
echo "Python version:"
python --version

echo ""
echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo ""
echo "=== Database Configuration ==="
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL environment variable is NOT set!"
  exit 1
else
  echo "✓ DATABASE_URL is set"
fi

echo ""
echo "=== Waiting for database to be ready ==="
sleep 15

echo ""
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput 2>&1 || true

echo ""
echo "=== Running migrations with retry logic ==="
python manage.py run_migrations

if [ $? -ne 0 ]; then
  echo "ERROR: Migrations failed!"
  exit 1
fi

echo ""
echo "=== Build completed successfully ==="
