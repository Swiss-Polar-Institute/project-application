#!/bin/bash

coverage erase
coverage run manage.py test --keepdb -v 3
coverage report
echo
echo
