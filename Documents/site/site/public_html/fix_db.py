import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def fix_database():
    # Путь к базе данных
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    db_file = os.path.join(db_path, 'site.db')
    
    # Создаем директорию, если её нет
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        print(f"Создана директория: {db_path}")
    
    # Удаляем старую базу данных
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Удалена старая база данных: {db_file}")
    
    try:
        # Создаем новую базу данных
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Создаем таблицу users с нужной структурой
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) NOT NULL UNIQUE,
                password VARCHAR(120) NOT NULL,
                created_at DATETIME NOT NULL,
                last_login DATETIME
            )
        ''')
        
        # Создаем администратора
        password_hash = generate_password_hash('admin')
        created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO users (username, password, created_at)
            VALUES (?, ?, ?)
        ''', ('admin', password_hash, created_at))
        
        # Создаем остальные необходимые таблицы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page VARCHAR(100) NOT NULL,
                ip_address VARCHAR(100) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Сохраняем изменения
        conn.commit()
        print("База данных успешно создана и инициализирована")
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    # Устанавливаем права доступа
    try:
        os.chmod(db_file, 0o666)
        os.chmod(db_path, 0o777)
        print("Права доступа установлены")
    except Exception as e:
        print(f"Ошибка при установке прав доступа: {e}")

if __name__ == '__main__':
    fix_database() 