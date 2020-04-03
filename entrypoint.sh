#!/bin/bash -e

/code/wait-for-mysql.sh

python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear

gunicorn ProjectApplication.wsgi:application \
        --bind 0.0.0.0:8085 \
        --workers 3 \
	--log-file=- \
	--error-logfile=- \
	--access-logfile=- \
	--capture-output \
        "$@"
