#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn Samsonllc.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
