#!/bin/bash
set -o errexit

pip install -r requirements.txt

# Wait for database to be ready (PostgreSQL takes a moment to start)
echo "Waiting for database to be ready..."
sleep 10

python manage.py collectstatic --noinput
python manage.py migrate --noinput
