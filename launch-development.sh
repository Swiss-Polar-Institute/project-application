#!/bin/bash

docker-compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.development.yml down
docker-compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.development.yml up --build
