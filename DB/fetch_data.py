import sqlite3

DB_PATH = "C:/Users/qkrtj/smart_Distillery/data/database.db"

def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM environment")
    rows = cursor.fetchall()

    print("📊 환경 데이터 목록:")
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    fetch_data()
