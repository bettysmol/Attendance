#!/bin/bash
set -o errexit

echo "=== Starting Application ==="
echo "Ensuring DATABASE_URL is set..."

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set!"
  export DATABASE_URL='postgresql://attendance_db_uix1_user:l0PXwUm7kpwSaAB1e0K2L6OcrRdLYXqk@dpg-d5tdj9dactks73a5cv40-a/attendance_db_uix1'
  echo "Set DATABASE_URL to: $DATABASE_URL"
fi

echo ""
echo "=== Running migrations ==="
python manage.py migrate --noinput --verbosity 2

if [ $? -ne 0 ]; then
  echo "ERROR: Migrations failed!"
  exit 1
fi

echo ""
echo "=== Migrations completed successfully ==="
echo "=== Starting Gunicorn ==="

exec gunicorn attendance_system.wsgi:application --workers 1 --bind 0.0.0.0:10000
