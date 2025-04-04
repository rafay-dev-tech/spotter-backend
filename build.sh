#!/usr/bin/env bash 

set -o errexit

pip install -r requirements.txt

pyhton3 manage.py collectstatic --no-input 

pyhton3 manage.py migrate


