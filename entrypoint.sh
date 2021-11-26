#!/bin/bash

# If any command fails: aborts
set -e
set -o pipefail

/code/wait-for-mysql.sh

python3 manage.py check --deploy --fail-level WARNING
python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear

gunicorn ProjectApplication.wsgi:application \
        --bind 0.0.0.0:8085 \
        --workers 20 \
	--timeout=600 \
	--log-file=- \
	--error-logfile=- \
	--access-logfile=- \
	--capture-output \
        "$@"
