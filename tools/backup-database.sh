#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Syntax error"
	echo $0: usage: $0 output_directory
	echo 'The name of the file will be projects-$DATE-$USER.sql'
	echo
	exit 1
fi

DIRECTORY="$1"

USER=$(whoami)
OUTPUT_NAME=$(date "+projects-%Y%m%d-%H%M%S-$USER.sql")
OUTPUT_FILE="$DIRECTORY/$OUTPUT_NAME"

mysqldump --defaults-file=/etc/mysql/project_application_mysql.conf projects > "$OUTPUT_FILE"

echo
echo "Backup done: $OUTPUT_FILE"
