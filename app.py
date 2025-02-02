from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
import os
import sys
import sqlite3
import json
import paho.mqtt.client as mqtt  # 📌 MQTT 라이브러리 추가
from kalman_filter import KalmanFilter
import joblib
import threading  # 📌 쓰레드 관련 라이브러리 추가

# 📌 db 폴더를 Python 경로에 추가하여 내부 파일을 가져올 수 있도록 설정
sys.path.append(os.path.join(os.path.dirname(__file__), "db"))

# 📌 db 폴더에서 데이터베이스 초기화 함수(init_db) 가져오기
from create_tables import init_db

# Flask 애플리케이션 생성 (템플릿 폴더 명시)
app = Flask(__name__, template_folder="templates")

# 📌 데이터베이스 파일 경로 설정
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "database.db")

# 📌 MQTT 설정 추가
MQTT_BROKER = "localhost"  # Mosquitto 브로커 주소 (로컬 테스트는 localhost)
MQTT_PORT = 1883
MQTT_TOPIC = "smart_Distillery/sensor_data"

# 📌 AI 모델 로드
try:
    ai_model = joblib.load("models/ai_model.pkl")
    model_loaded = True
except FileNotFoundError:
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
    데이터베이스 연결을 생성하여 반환합니다.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
    return conn

# 📌 발효 설정 가져오기
def get_fermentation_settings():
    """
    settings 테이블에서 발효 설정 값을 가져옵니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings WHERE id = 1')
    settings = cursor.fetchone()
    conn.close()

    if settings:
        return dict(settings)  # 딕셔너리 형태로 반환
    return {
        "temperature": 25.0,
        "humidity": 50,
        "co2": 400,
        "sugar": 20.0
    }

# 📌 MQTT 메시지 수신 및 DB 저장
def on_message(client, userdata, msg):
    """
    MQTT 브로커에서 메시지를 수신하면 실행되는 함수.
    JSON 데이터를 디코딩하여 DB에 중복 여부를 확인한 후 저장합니다.
    """
    try:
        # 메시지를 디코딩하고 JSON으로 변환
        payload = msg.payload.decode("utf-8")
        print(f"📥 수신된 메시지: {payload}")  # 디버깅용 로그
        
        data = json.loads(payload)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 각 필드가 None이 아닌지 확인하고 기본값 설정
        temperature = filters["temperature"].update(float(data.get("temperature", 0)))
        humidity = filters["humidity"].update(float(data.get("humidity", 0)))
        co2 = filters["co2"].update(float(data.get("co2", 0)))
        density = float(data.get("density", 0)) if data.get("density") else None
        alcohol = float(data.get("alcohol", 0)) if data.get("alcohol") else None
        sugar = float(data.get("sugar", 0)) if data.get("sugar") else None

        # 데이터베이스 연결
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 중복 데이터 확인: 동일한 타임스탬프와 주요 데이터를 가진 레코드가 있는지 체크
        cursor.execute('''
            SELECT * FROM environment 
            WHERE timestamp = ? AND temperature = ? AND humidity = ? AND co2 = ? AND sugar = ?
        ''', (timestamp, temperature, humidity, co2, sugar))
        
        # 중복이 없을 때만 삽입
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, temperature, humidity, co2, density, alcohol, sugar))
            conn.commit()
            print(f"✅ [MQTT] 데이터 저장 완료: {data}")
        else:
            print("⚠️ [MQTT] 중복 데이터 발견: 저장하지 않음")

        conn.close()

    except json.JSONDecodeError as json_error:
        print(f"❌ [MQTT] JSON 디코딩 오류 발생: {json_error}")
    except Exception as e:
        print(f"❌ [MQTT] 데이터 처리 중 오류 발생: {e}")

# 📌 MQTT 클라이언트 설정
mqtt_client = mqtt.Client()

# 중복 연결 방지: 연결 여부 체크 후 설정
if not mqtt_client.is_connected():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.subscribe(MQTT_TOPIC)

# 📌 메인 페이지 라우트
@app.route('/')
def index():
    """
    메인 페이지를 렌더링합니다.
    """
    settings = get_fermentation_settings()  # 발효 설정 가져오기
    return render_template('index.html', settings=settings)

# 📌 환경 데이터 페이지 라우트
@app.route('/environment')
def environment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM environment ORDER BY timestamp DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    return render_template('environment.html', data=[dict(row) for row in rows])

@app.route('/api/environment', methods=['GET'])
def get_environment_data():
    """
    환경 데이터를 JSON 형식으로 반환하는 API.
    최근 10개 데이터를 가져와서 반환합니다.
    """
    conn = get_db_connection()  # SQLite DB 연결
    cursor = conn.cursor()
    
    # 최신 10개 데이터 가져오기
    cursor.execute('SELECT * FROM environment ORDER BY timestamp DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()

    # 데이터를 JSON 형식으로 변환
    data = [dict(row) for row in rows]
    
    return jsonify(data)  # JSON 응답 반환

# 📌 환경 데이터 저장 API 라우트
@app.route('/api/data', methods=['POST'])
def save_data():
    data = request.json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 📌 칼만 필터 적용
    temperature = filters["temperature"].update(data.get("temperature"))
    humidity = filters["humidity"].update(data.get("humidity"))
    co2 = filters["co2"].update(data.get("co2"))

    # 📌 데이터베이스 저장
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, temperature, humidity, co2, data.get("density"), data.get("alcohol"), data.get("sugar")))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data saved!"}), 200

# 📌 발효 페이지 라우트
@app.route('/fermentation')
def fermentation():
    return render_template('fermentation.html')

# 📌 데이터 로그 페이지 라우트
@app.route('/data-logs')
def data_logs():
    return render_template('data_logs.html')

# 📌 설정 페이지 라우트
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE settings
            SET temperature = ?, humidity = ?, co2 = ?, sugar = ?, alcohol = ?
            WHERE id = 1
        ''', (
            float(request.form['temperature']),
            int(request.form['humidity']),
            int(request.form['co2']),
            float(request.form['sugar']),
            float(request.form['alcohol'])
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    settings = get_fermentation_settings()
    return render_template('settings.html', settings=settings)

# 📌 Flask 실행
if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화
    
    # 📌 MQTT 실행을 별도의 쓰레드에서 실행하여 Flask와 충돌하지 않도록 설정
    mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    app.run(debug=True)  # Flask 서버 실행