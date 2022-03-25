#!/bin/sh

mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /docker-entrypoint-initdb.d/schema.sql
