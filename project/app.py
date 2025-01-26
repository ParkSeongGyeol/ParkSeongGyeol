from flask import Flask
from project.routes import init_routes
from db import init_db
from ai_model import load_ai_model

def create_app():
    # Flask 애플리케이션 생성
    app = Flask(__name__)

    # 데이터베이스 초기화
    init_db()

    # AI 모델 로드
    load_ai_model()

    # 라우트 초기화
    init_routes(app)

    return app  
