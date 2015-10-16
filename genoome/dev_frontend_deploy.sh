#!/bin/bash

PYPATH=/home/ubuntu/.pyenv/versions/dev_venv/bin/python;

cd /opt/dev_genoome/genoome/genoome/ && sudo git checkout -- . && git pull origin dev && $PYPATH ./manage.py collectstatic --noinput --settings=genoome.settings.development && sudo touch /etc/uwsgi/vassals/dev_genoome.ini && sudo chown -R ubuntu:www-data /opt/dev_genoome/genoome/genoome/assets/

echo 'Success';
