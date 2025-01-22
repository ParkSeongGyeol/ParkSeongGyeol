from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
import sqlite3
import os
from kalman_filter import KalmanFilter
import joblib

#hi
app = Flask(__name__)

# AI 모델 로드
try:
    ai_model = joblib.load("models/ai_model.pkl")
    model_loaded = True
except FileNotFoundError:
    print("[WARNING] AI 모델 파일이 'models/ai_model.pkl'에 존재하지 않습니다. 예측 기능은 비활성화됩니다.")
    model_loaded = False

# 칼만 필터 초기화
filters = {
    "temperature": KalmanFilter(0.1, 1.0, 25.0),
    "humidity": KalmanFilter(0.1, 1.0, 50.0),
    "co2": KalmanFilter(0.1, 1.0, 400.0)
}

# 데이터베이스 연결 함수
def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스 초기화
def init_db():
    if not os.path.exists('data'):
        os.mkdir('data')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 환경 데이터 테이블 생성
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

    # 설정 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity INTEGER,
            co2 INTEGER,
            sugar REAL
        )
    ''')

    # 기본 설정값 추가
    cursor.execute('''
        INSERT OR IGNORE INTO settings (id, temperature, humidity, co2, sugar)
        VALUES (1, 25.0, 50, 400, 20.0)
    ''')

    conn.commit()
    conn.close()

# 발효 설정 가져오기
def get_fermentation_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings WHERE id = 1')
    settings = cursor.fetchone()
    conn.close()
    if settings:
        return dict(settings)
    return {
        "temperature": 25.0,
        "humidity": 50,
        "co2": 400,
        "sugar": 20.0
    }

@app.route('/')
def index():
    settings = get_fermentation_settings()  # 발효 조건 가져오기
    return render_template('index.html', settings=settings)

@app.route('/environment')
def environment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM environment ORDER BY timestamp DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    return render_template('environment.html', data=[dict(row) for row in rows])

@app.route('/api/data', methods=['POST'])
def save_data():
    data = request.json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 칼만 필터 적용
    temperature = filters["temperature"].update(data.get("temperature"))
    humidity = filters["humidity"].update(data.get("humidity"))
    co2 = filters["co2"].update(data.get("co2"))

    # 데이터베이스 저장
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, temperature, humidity, co2, data.get("density"), data.get("alcohol"), data.get("sugar")))
    conn.commit()
    conn.close()

    # AI 모델 예측 (모델이 로드된 경우에만)
    if model_loaded:
        features = [[temperature, humidity, co2, data.get("density"), data.get("alcohol"), data.get("sugar")]]
        prediction = ai_model.predict(features)
    else:
        prediction = [0]  # 모델이 없을 경우 기본값 반환

    return jsonify({"message": "Data saved!", "prediction": prediction[0]}), 200

# 추가된 라우트 (Fermentation, Data Logs, Settings)
@app.route('/fermentation')
def fermentation():
    return render_template('fermentation.html')

@app.route('/data-logs')
def data_logs():
    return render_template('data_logs.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # 설정값 업데이트 처리
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE settings
            SET temperature = ?, humidity = ?, co2 = ?, sugar = ?
            WHERE id = 1
        ''', (
            float(request.form['temperature']),
            int(request.form['humidity']),
            int(request.form['co2']),
            float(request.form['sugar'])
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))  # 저장 후 대시보드로 리디렉션

    # GET 요청 시 설정값 가져오기
    settings = get_fermentation_settings()
    return render_template('settings.html', settings=settings)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
