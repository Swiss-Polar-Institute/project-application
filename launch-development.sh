#!/bin/bash

docker-compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.development.yml down
echo
echo "All going well it should be available in http://localhost:1235"
echo
docker-compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.development.yml up --build

