#!/bin/sh

celery -A config worker -l info &

sleep 10

python manage.py loadscript no_clear

python manage.py runserver 0.0.0.0:8000