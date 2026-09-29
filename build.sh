#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python furnishproj/manage.py collectstatic --no-input
python furnishproj/manage.py migrate
