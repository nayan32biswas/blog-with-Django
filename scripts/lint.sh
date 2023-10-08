#!/usr/bin/env bash

set -ex

mypy app
flake8 app
black app --check
isort app scripts --check-only
