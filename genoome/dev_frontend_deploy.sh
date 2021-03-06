#!/bin/bash

VENVPATH=/home/ubuntu/.pyenv/versions/dev_venv;
PYPATH=$VENVPATH/bin/python;
GULPPATH=$VENVPATH/bin/gulp;

source $VENVPATH/bin/activate;
cd /opt/dev_genoome/genoome/genoome/ && sudo git checkout -- . && \
git pull origin dev && \
cd ../ && \
npm install && \
./node_modules/.bin/bower install && \
cd - && \
$GULPPATH --gulpfile ../gulpfile.js --cwd ../ dist && \
$PYPATH ./manage.py collectstatic --noinput --settings=genoome.settings.development && \
sudo touch /etc/uwsgi/vassals/dev_genoome.ini && \
sudo chown -R ubuntu:www-data /opt/dev_genoome/genoome/genoome/assets/;

echo 'Success';
