#!/bin/bash

docker-compose -f docker-compose.yml -f docker-compose.live.yml down
docker-compose -f docker-compose.yml -f docker-compose.live.yml up --build -d
