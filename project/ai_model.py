import joblib

ai_model = None

def load_ai_model():
    global ai_model
    try:
        ai_model = joblib.load("models/ai_model.pkl")
        print("[INFO] AI 모델 로드 성공!")
    except FileNotFoundError:
        print("[WARNING] AI 모델 파일이 없습니다. 예측 기능 비활성화.")
