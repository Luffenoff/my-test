import os
import sys
import shutil
import sqlite3
from main import app
from extensions import db
from models import User, News, RepairWork, ServicedObject, SystemLog, Contacts

def reset_database():
    with app.app_context():
        # Создаем временную базу данных в памяти
        temp_uri = 'sqlite:///:memory:'
        old_uri = app.config['SQLALCHEMY_DATABASE_URI']
        app.config['SQLALCHEMY_DATABASE_URI'] = temp_uri
        
        # Создаем все таблицы во временной базе
        db.create_all()
        print("Временные таблицы созданы")
        
        try:
            # Создаем администратора
            admin = User(username='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Администратор создан во временной базе")
            
            # Получаем путь к файлу базы данных
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
            db_file = os.path.join(db_path, 'site.db')
            
            # Создаем директорию, если её нет
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            
            # Копируем временную базу в файл
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            
            # Получаем данные из временной базы
            source = sqlite3.connect(':memory:')
            source.row_factory = dict_factory
            
            # Создаем новый файл базы данных
            if os.path.exists(db_file):
                os.remove(db_file)
            
            dest = sqlite3.connect(db_file)
            
            # Копируем схему и данные
            for line in source.iterdump():
                if line != 'BEGIN TRANSACTION;' and line != 'COMMIT;':
                    dest.execute(line)
            
            dest.commit()
            dest.close()
            source.close()
            
            print(f"База данных успешно создана: {db_file}")
            
            # Восстанавливаем оригинальный URI
            app.config['SQLALCHEMY_DATABASE_URI'] = old_uri
            
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")
            sys.exit(1)

if __name__ == '__main__':
    reset_database()