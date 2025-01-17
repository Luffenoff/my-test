import os
import sqlite3
from main import app, db
from models import User

def migrate_database():
    with app.app_context():
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'site.db')
        
        # Создаем соединение с базой данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Создаем временную таблицу с новой структурой
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    password VARCHAR(120) NOT NULL,
                    created_at DATETIME,
                    last_login DATETIME
                )
            ''')
            
            # Копируем данные из старой таблицы
            try:
                cursor.execute('''
                    INSERT INTO users_new (id, username, password, created_at)
                    SELECT id, username, password, created_at FROM users
                ''')
            except sqlite3.OperationalError:
                print("Копирование данных не удалось - возможно, старая таблица пуста")
            
            # Удаляем старую таблицу
            cursor.execute('DROP TABLE IF EXISTS users')
            
            # Переименовываем новую таблицу
            cursor.execute('ALTER TABLE users_new RENAME TO users')
            
            # Создаем администратора, если его нет
            cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            if not cursor.fetchone():
                admin = User(username='admin')
                admin.set_password('admin')
                created_at = admin.created_at.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                    (admin.username, admin.password, created_at)
                )
            
            conn.commit()
            print("Миграция успешно завершена")
            
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при миграции: {e}")
        
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database() 