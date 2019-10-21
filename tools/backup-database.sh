#!/bin/bash

OUTPUT_FILE=$(date "+projects-%Y%m%d-%H%M%S.sql")
mysqldump --defaults-file=/etc/mysql/projects.cnf projects > "$OUTPUT_FILE"

echo
echo "Backup done: $OUTPUT_FILE"
