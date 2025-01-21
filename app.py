from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# SQLite 데이터베이스 연결
def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스 초기화
def init_db():
    if not os.path.exists('data'):
        os.mkdir('data')  # 'data' 폴더 생성
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            co2 INTEGER,
            density REAL,
            alcohol REAL,
            sugar REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fermentation')
def fermentation():
    return render_template('fermentation.html')

@app.route('/environment')
def environment():
    return render_template('environment.html')

@app.route('/data-logs')
def data_logs():
    return render_template('data_logs.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/data', methods=['POST'])
def save_data():
    data = request.json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    co2 = data.get('co2')
    density = data.get('density')
    alcohol = data.get('alcohol')
    sugar = data.get('sugar')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, temperature, humidity, co2, density, alcohol, sugar))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data saved!"}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM environment')
    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    return jsonify(data), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)