#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations PKDB
python manage.py migrate PKDB
python -u manage.py runserver_plus --cert-file ./certs/server.crt --key-file ./certs/server.key 0.0.0.0:8443