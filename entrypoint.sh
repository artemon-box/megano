#!/bin/sh

celery -A config worker -l info &

sleep 10

if [ "$LOAD_FIXTURES" = "1" ]; then
    python manage.py loadscript with_clear
else
    python manage.py migrate
fi

python manage.py runserver 0.0.0.0:8000