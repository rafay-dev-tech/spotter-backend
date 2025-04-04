#!/usr/bin/env bash 

set -o errexit

pip install -r requirements.txt

pyhton manage.py collectstatic --no-input 

pyhton manage.py migrate


