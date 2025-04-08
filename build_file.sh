#!/bin/bash


# install dependencies
pip install -r requirements.txt

# run django command    
python3 manage.py makemigrations

python3 manage.py migrate
