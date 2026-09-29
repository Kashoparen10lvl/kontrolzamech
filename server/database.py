import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'kontrolzamech.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица объектов
    c.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица замечаний
    c.execute('''
        CREATE TABLE IF NOT EXISTS remarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            place TEXT NOT NULL,
            status TEXT DEFAULT 'Новое',
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (object_id) REFERENCES objects(id)
        )
    ''')
    
    # Создаём тестовые данные
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', 'admin123', 'Администратор'),
            ('ivanov', 'ivan123', 'Сотрудник'),
            ('petrov', 'petr123', 'Сотрудник'),
        ]
        c.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)
        
        objects = [
            ('ЖК «Северный»', 'г. Москва, ул. Примерная, 10'),
            ('Офис на Ленина, 24', 'г. Москва, ул. Ленина, 24'),
        ]
        c.executemany("INSERT INTO objects (name, address) VALUES (?, ?)", objects)
        
        c.execute("SELECT id FROM objects WHERE name = 'ЖК «Северный»'")
        obj_id = c.fetchone()[0]
        remarks = [
            (obj_id, 'Протекает труба в санузле', 'Подъезд 2, этаж 3', 'Новое'),
            (obj_id, 'Не работает освещение', 'Подъезд 1, входная группа', 'На проверке'),
        ]
        c.executemany("INSERT INTO remarks (object_id, title, place, status) VALUES (?, ?, ?, ?)", remarks)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("База данных инициализирована!")
