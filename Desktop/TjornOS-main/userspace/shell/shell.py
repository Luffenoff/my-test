import os
import sys
from cmd import Cmd

class OSShell(Cmd):
    intro = 'Добро пожаловать в МояОС! Введите help для справки.\n'
    prompt = 'МояОС> '

    def do_ls(self, arg):
        """Показать содержимое текущей директории"""
        try:
            files = os.listdir('.' if not arg else arg)
            for f in files:
                print(f)
        except Exception as e:
            print(f"Ошибка: {e}")

    def do_cd(self, arg):
        """Сменить текущую директорию"""
        try:
            os.chdir(arg)
        except Exception as e:
            print(f"Ошибка: {e}")

    def do_exit(self, arg):
        """Выход из оболочки"""
        return True

if __name__ == '__main__':
    OSShell().cmdloop() 