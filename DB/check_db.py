import os

# 데이터베이스 파일 경로 설정
DB_PATH = "C:/Users/qkrtj/smart_Distillery/data/database.db"

# 데이터베이스 존재 여부 확인
if os.path.exists(DB_PATH):
    print("✅ 데이터베이스 파일이 존재합니다:", DB_PATH)
else:
    print("❌ 데이터베이스 파일이 없습니다. 다시 확인하세요.")
