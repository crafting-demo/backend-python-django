#!/bin/bash

echo '== Update system =='
sudo apt-get update

echo '== Install django =='
pip3 install django

echo '== Install mysql client =='
sudo apt-get install python3-dev build-essential -y
sudo apt-get install libmysqlclient-dev default-libmysqlclient-dev -y
pip3 install mysqlclient

echo '== Install mongodb client =='
python3 -m pip install pymongo

echo '== Install django-cors-headers =='
pip3 install django-cors-headers

echo '== Apply unapplied migration(s) =='
python3 manage.py migrate

echo '== DONE == '
