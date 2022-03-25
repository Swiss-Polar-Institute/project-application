#!/bin/bash

docker-compose -f docker-compose.development.yml down
docker-compose -f docker-compose.development.yml up --build -d

echo
echo "All going well it should be available in http://0.0.0.0:8000/"
echo
