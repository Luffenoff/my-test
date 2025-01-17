import sqlite3
import logging
from datetime import datetime

def get_db_connection():
    try:
        conn = sqlite3.connect('instance/site.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise

def create_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_user(username, password, is_admin=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
            (username, password, is_admin)
        )
        conn.commit()
        return cursor.lastrowid

def update_user(user_id, password=None, is_admin=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        updates = []
        values = []
        
        if password is not None:
            updates.append('password = ?')
            values.append(password)
        if is_admin is not None:
            updates.append('is_admin = ?')
            values.append(is_admin)
            
        if updates:
            values.append(user_id)
            query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, values)
            conn.commit()

def get_user(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone() 