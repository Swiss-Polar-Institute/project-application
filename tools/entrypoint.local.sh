#!/bin/bash

# If any command fails: aborts
set -e
set -o pipefail

/code/wait-for-mysql.sh

python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear
python3 manage.py runserver 0.0.0.0:8000
