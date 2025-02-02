import sqlite3
import os

# 데이터베이스 파일 경로 설정
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "database.db")

def init_db():
    """
    데이터베이스 초기화 함수.
    - 데이터베이스 파일이 없으면 생성.
    - 필요한 테이블(environment, settings)을 생성.
    """
    # 데이터베이스 파일이 저장될 폴더 생성
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.mkdir(os.path.dirname(DB_PATH))

    # 데이터베이스 연결
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 환경 데이터 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
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
            temperature REAL NOT NULL,
            humidity INTEGER NOT NULL,
            co2 INTEGER NOT NULL,
            sugar REAL NOT NULL,
            alcohol REAL NOT NULL DEFAULT 5.0  -- 알코올 농도 기본값 추가
        )
    ''')

    # 기본 설정값 삽입 (중복 방지)
    cursor.execute('''
        INSERT OR IGNORE INTO settings (id, temperature, humidity, co2, sugar, alcohol)
        VALUES (1, 25.0, 50, 400, 20.0, 5.0)  -- 알코올 초기값 포함
    ''')

    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화가 완료되었습니다.")

# 스크립트 실행 시 데이터베이스 초기화
if __name__ == "__main__":
    init_db()
