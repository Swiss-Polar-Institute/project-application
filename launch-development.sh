#!/bin/bash

docker-compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.development.yml down
docker-compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.development.yml up --build

echo "All going well it should be available in http://localhost:1235"
