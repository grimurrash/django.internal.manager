python -m venv djangoenv

source djangoenv/bin/activate

pip install --upgrade pip && pip install django && CFLAGS="-std=c99" pip install mysqlclient

pip install python-telegram-bot --upgrade

pip install gspread

pip install --upgrade google-api-python-client oauth2client

pip install django-environ

pip install django-grappelli

django-admin startproject mcpsmanager

python mcpsmanager/manage.py collectstatic

python mcpsmanager/manage.py migrate