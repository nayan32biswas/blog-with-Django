#!/bin/sh

poetry run coverage run ./app/manage.py test app --noinput
poetry run coverage report -m --skip-covered
