#!/bin/bash

VENVPATH=/home/ubuntu/.pyenv/versions/venv;
PYPATH=$VENVPATH/bin/python;
GULPPATH=$VENVPATH/bin/gulp;

source $VENVPATH/bin/activate;
$GULPPATH --gulpfile ../gulpfile.js --cwd ../ dist && \
$PYPATH ./manage.py collectstatic --noinput --settings=genoome.settings.production && \
sudo touch /etc/uwsgi/vassals/genoome.ini && \
sudo chown -R ubuntu:www-data /opt/genoome/genoome/genoome/assets/;
