from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
import os
import sys
import sqlite3
from kalman_filter import KalmanFilter
import joblib

# 📌 db 폴더를 Python 경로에 추가하여 내부 파일을 가져올 수 있도록 설정
sys.path.append(os.path.join(os.path.dirname(__file__), "db"))

# 📌 db 폴더에서 데이터베이스 초기화 함수(init_db) 가져오기
from create_tables import init_db

# Flask 애플리케이션 생성
app = Flask(__name__)

# 📌 데이터베이스 파일 경로 설정
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "database.db")

# 📌 AI 모델 로드
try:
    # 'models/ai_model.pkl' 파일에서 AI 모델 로드
    ai_model = joblib.load("models/ai_model.pkl")
    model_loaded = True
except FileNotFoundError:
    # AI 모델 파일이 없을 경우 경고 메시지 출력
    print("[WARNING] AI 모델 파일이 'models/ai_model.pkl'에 존재하지 않습니다. 예측 기능은 비활성화됩니다.")
    model_loaded = False

# 📌 칼만 필터 초기화
filters = {
    "temperature": KalmanFilter(0.1, 1.0, 25.0),  # 온도 필터
    "humidity": KalmanFilter(0.1, 1.0, 50.0),    # 습도 필터
    "co2": KalmanFilter(0.1, 1.0, 400.0)         # CO2 필터
}

# 📌 데이터베이스 연결 함수
def get_db_connection():
    """
    데이터베이스 파일에 연결하는 함수.
    - 데이터베이스 경로: data/database.db
    - 반환값: SQLite 연결 객체
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
    return conn

# 📌 발효 설정 가져오기
def get_fermentation_settings():
    """
    settings 테이블에서 발효 설정 값을 가져오는 함수.
    - 반환값: 설정값 딕셔너리 (temperature, humidity, co2, sugar)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings WHERE id = 1')  # ID가 1인 설정값 가져오기
    settings = cursor.fetchone()
    conn.close()

    if settings:
        return dict(settings)  # 딕셔너리 형태로 반환
    # 기본 설정값 반환 (값이 없을 경우)
    return {
        "temperature": 25.0,
        "humidity": 50,
        "co2": 400,
        "sugar": 20.0
    }

# 📌 메인 페이지 라우트
@app.route('/')
def index():
    """
    메인 페이지 라우트.
    - 설정값(settings)을 가져와 index.html에 전달
    """
    settings = get_fermentation_settings()
    return render_template('index.html', settings=settings)

# 📌 환경 데이터 페이지 라우트
@app.route('/environment')
def environment():
    """
    최근 환경 데이터를 조회하여 environment.html로 렌더링.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # 최신 20개의 환경 데이터 가져오기
    cursor.execute('SELECT * FROM environment ORDER BY timestamp DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    return render_template('environment.html', data=[dict(row) for row in rows])

# 📌 환경 데이터 저장 API 라우트
@app.route('/api/data', methods=['POST'])
def save_data():
    """
    환경 데이터를 POST 요청으로 받아 데이터베이스에 저장.
    - JSON 형식의 데이터를 받아 데이터베이스에 삽입.
    """
    data = request.json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간 생성

    # 칼만 필터를 적용하여 노이즈 제거
    temperature = filters["temperature"].update(data.get("temperature"))
    humidity = filters["humidity"].update(data.get("humidity"))
    co2 = filters["co2"].update(data.get("co2"))

    # 데이터베이스에 저장
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, temperature, humidity, co2, data.get("density"), data.get("alcohol"), data.get("sugar")))
    conn.commit()
    conn.close()

    # AI 모델 예측 수행 (모델 로드 상태 확인)
    if model_loaded:
        # 예측을 위한 입력 데이터 구성
        features = [[temperature, humidity, co2, data.get("density"), data.get("alcohol"), data.get("sugar")]]
        prediction = ai_model.predict(features)
    else:
        prediction = [0]  # AI 모델이 없는 경우 기본값 반환

    # 결과 반환
    return jsonify({"message": "Data saved!", "prediction": prediction[0]}), 200

# 📌 발효 페이지 라우트
@app.route('/fermentation')
def fermentation():
    """
    발효 관련 정보를 렌더링.
    """
    return render_template('fermentation.html')

# 📌 데이터 로그 페이지 라우트
@app.route('/data-logs')
def data_logs():
    """
    데이터 로그 정보를 렌더링.
    """
    return render_template('data_logs.html')

# 📌 설정 페이지 라우트
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    발효 설정 페이지 라우트.
    - GET: 현재 설정값을 가져와 렌더링.
    - POST: 설정값을 업데이트하고 저장.
    """
    if request.method == 'POST':
        # POST 요청: 설정값 업데이트
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
        return redirect(url_for('index'))  # 저장 후 메인 페이지로 리디렉션

    # GET 요청: 현재 설정값 가져오기
    settings = get_fermentation_settings()
    return render_template('settings.html', settings=settings)

# 📌 Flask 애플리케이션 실행
if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화 (테이블 생성)
    app.run(debug=True)  # 디버그 모드로 실행
