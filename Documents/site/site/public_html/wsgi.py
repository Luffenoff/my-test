import os
import sys

# Добавляем путь к приложению и виртуальному окружению
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/c/cd63130/site/env/lib/python3.10/site-packages')

from main import app as application

if __name__ == "__main__":
    application.run()