#!/bin/bash

docker-compose -f docker-compose.development.yml up --build -d
docker-compose -f docker-compose.development.yml exec project-application python3 manage.py test
