#!/bin/sh

set -ex

python ./app/manage.py makemigrations
python ./app/manage.py migrate
