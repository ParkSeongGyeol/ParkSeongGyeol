import sys
import os

# Python 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project.app import create_app

# Flask 애플리케이션 생성
app = create_app()

if __name__ == "__main__":
    # Flask 실행
    app.run(debug=True, host="0.0.0.0", port=5000)
