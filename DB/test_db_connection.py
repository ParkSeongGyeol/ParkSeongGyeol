import sqlite3

# 데이터베이스 파일 경로 설정
DB_PATH = "C:/Users/qkrtj/smart_Distillery/data/database.db"

# SQLite 데이터베이스 연결 테스트
def check_database_connection():
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("📂 현재 데이터베이스의 테이블 목록:")
        if tables:
            for table in tables:
                print(f" - {table[0]}")
        else:
            print("⚠️ 테이블이 없습니다. `create_tables.py`를 실행해 테이블을 생성하세요.")

        conn.close()
    except Exception as e:
        print("❌ 데이터베이스 연결 실패:", e)

# 실행
if __name__ == "__main__":
    check_database_connection()
