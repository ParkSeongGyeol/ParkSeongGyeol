import sqlite3

DB_PATH = "C:/Users/qkrtj/smart_Distillery/data/database.db"

def delete_duplicate_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 중복된 데이터 삭제 (최신 ID만 남기기)
    cursor.execute('''
        DELETE FROM environment
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM environment
            GROUP BY timestamp, temperature, humidity
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 중복 데이터 삭제 완료.")

if __name__ == "__main__":
    delete_duplicate_data()
