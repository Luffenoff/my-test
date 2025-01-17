import os
import sys

# Путь к виртуальному окружению
VIRTUALENV = '/home/c/cd63130/site/venv'

# Путь к интерпретатору Python в виртуальном окружении
if os.path.exists(VIRTUALENV):
    INTERP = os.path.join(VIRTUALENV, 'bin/python')
else:
    # Fallback на системный Python
    INTERP = '/usr/bin/python3'

# Добавляем пути для поиска модулей
sys.path.insert(0, '/home/c/cd63130/site/public_html')
sys.path.insert(0, VIRTUALENV)

# Импортируем приложение
from main import app as application