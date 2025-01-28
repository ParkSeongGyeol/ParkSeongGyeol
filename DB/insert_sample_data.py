import sqlite3

DB_PATH = "C:/Users/qkrtj/smart_Distillery/data/database.db"

def insert_sample_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
        VALUES ('2025-01-28 15:30:00', 25.5, 60, 410, 1.02, 5.0, 18.0)
    ''')

    conn.commit()
    conn.close()
    print("✅ 샘플 데이터 삽입 완료.")

if __name__ == "__main__":
    insert_sample_data()
