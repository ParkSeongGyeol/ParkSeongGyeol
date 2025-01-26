import sqlite3
from project.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_fermentation_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings WHERE id = 1')
    settings = cursor.fetchone()
    conn.close()
    return dict(settings) if settings else {
        "temperature": 25.0,
        "humidity": 50,
        "co2": 400,
        "sugar": 20.0
    }
