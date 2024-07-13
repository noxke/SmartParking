#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations PKDB
python manage.py migrate PKDB
python -u manage.py runserver_plus 0.0.0.0:8443