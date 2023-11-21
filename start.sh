#!/bin/bash
#python manage.py makemigrations \ &&
#python manage.py migrate \ &&
uwsgi --ini /var/www/html/NoBC/uwsgi.ini
tail -f /dev/null