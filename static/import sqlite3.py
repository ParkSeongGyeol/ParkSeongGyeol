import sqlite3

def init_db():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()