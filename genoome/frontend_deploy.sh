#!/bin/bash

PYPATH=/home/ubuntu/.pyenv/versions/venv/bin/python;

cd /opt/genoome/genoome/genoome/ && sudo git checkout -- . && git pull origin master && $PYPATH ./manage.py collectstatic --noinput && sudo touch /etc/uwsgi/vassals/genoome.ini && sudo chown -R ubuntu:www-data /opt/genoome/genoome/genoome/assets/

echo 'Success';
