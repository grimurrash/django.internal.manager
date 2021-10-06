# -*- coding: utf-8 -*-
import os
import sys

# Настройка для reg.ru
user_login = ""
project_name = ""
site_name = ""
python_version = "3.9"

# Путь к проекту
sys.path.insert(0, f'/var/www/{user_login}/data/www/{site_name}/{project_name}')
# путь до каталога виртуального окружения
sys.path.insert(1, f'/var/www/{user_login}/data/venv/lib/python{python_version}/site-packages')
# Модуль с настройками
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
