import sqlite3

DB_PATH = "C:/Users/qkrtj/smart_Distillery/data/database.db"

def fetch_data():
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 환경 데이터 가져오기
        cursor.execute("SELECT * FROM environment")
        rows = cursor.fetchall()

        print("📊 환경 데이터 목록:")
        if rows:
            for row in rows:
                print(f"ID: {row[0]}, Timestamp: {row[1]}, Temperature: {row[2]} °C, "
                      f"Humidity: {row[3]} %, CO2: {row[4]} ppm, Density: {row[5]}, "
                      f"Alcohol: {row[6]} %, Sugar: {row[7]} Brix")
        else:
            print("⚠️ 데이터가 존재하지 않습니다.")

    except sqlite3.Error as e:
        print(f"❌ 데이터베이스 오류 발생: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fetch_data()
