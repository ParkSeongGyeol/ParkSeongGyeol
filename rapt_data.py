import requests
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# matplotlib 백엔드 설정 (Qt 에러 방지)
matplotlib.use('Agg')

# RAPT 인증 서버 URL
TOKEN_URL = "https://id.rapt.io/connect/token"
API_URL = "https://api.rapt.io/api/Hydrometers/GetHydrometers"

# 인증 정보
USERNAME = "YOUR_ID"
PASSWORD = "SECRET_API_KEY"
CLIENT_ID = "rapt-user"

# 토큰 생성 함수
def get_bearer_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("토큰 생성 실패:", response.status_code, response.text)
        return None

# 계산 함수
def calculate_abv(starting_gravity: float, current_gravity: float) -> float:
    return round((starting_gravity - current_gravity) * 131.25, 2)

def calculate_brix(specific_gravity: float) -> float:
    return round((specific_gravity - 1) * 1000 / 4, 2)

def fermentation_progress(current_abv: float, potential_abv: float) -> float:
    return round((current_abv / potential_abv) * 100, 2)

def estimate_remaining_days(current_abv: float, potential_abv: float, fermentation_rate: float) -> int:
    remaining_abv = potential_abv - current_abv
    if fermentation_rate <= 0:
        return 0
    return round(remaining_abv / fermentation_rate)

# 발효 속도의 데이터 출시 함수
def calculate_fermentation_rate(data_points):
    if len(data_points) < 2:
        return 0  # 데이터가 부족하면 0 반환

    # 가장 최근 두 데이터 포인트를 사용하여 발효 속도 계산
    latest = data_points[-1]
    previous = data_points[-2]

    abv_diff = latest["abv"] - previous["abv"]
    time_diff = (latest["time"] - previous["time"]).total_seconds() / 86400  # 일 단위로 시간 차 계산

    if time_diff > 0:
        return round(abv_diff / time_diff, 4)  # 일일 ABV 변화율
    return 0

# 상황을 판단하는 함수
def fermentation_state(data_points):
    latest = data_points[-1]
    initial = data_points[0]
    sg_drop = initial["specific_gravity"] - latest["specific_gravity"]
    brix_drop = initial["brix"] - latest["brix"]

    if sg_drop < 0.005 and brix_drop < 0.5:
        return "발효 시작 (Fermentation Starting)"
    elif 0.005 <= sg_drop < 0.03 and 0.5 <= brix_drop < 5:
        return "중간 발효 단계 (Mid Fermentation)"
    elif sg_drop >= 0.03 and brix_drop >= 5:
        return "발효 거의 완료 (Nearly Completed)"
    else:
        return "추가 숙성 단계 (Post Fermentation)"

# 시각화 함수
def plot_fermentation_state(data_points, current_state):
    times = [point["time"] for point in data_points]
    sg_values = [point["specific_gravity"] for point in data_points]
    brix_values = [point["brix"] for point in data_points]

    plt.figure(figsize=(10, 6))
    plt.plot(times, sg_values, label="Specific Gravity (SG)", marker="o")
    plt.plot(times, brix_values, label="Brix (Sugar Content)", marker="s")
    plt.axhline(y=1.010, color='red', linestyle='--', label="Target SG (1.010)")
    plt.title(f"Fermentation Progress: {current_state}")
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.legend()
    plt.grid()
    #plt.savefig("fermentation_progress.png")  # 그래프를 파일로 저장
    plt.close()

# Bearer 토큰 생성
bearer_token = get_bearer_token()

if bearer_token:
    # API 요청 헤더
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # API 요청 및 데이터 처리
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("수신된 데이터:")
        fermentation_data = []

        for index, hydrometer in enumerate(data, start=1):
            print(f"\nHydrometer {index}:")
            name = hydrometer.get("name", "N/A")
            temperature = hydrometer.get("temperature", 0)
            gravity_raw = hydrometer.get("gravity", 0)
            gravity = round(gravity_raw / 1000, 4)  # raw 값에서 적절한 비중 값 계산

            

            starting_gravity = float(hydrometer.get("activeProfileSession", {}).get("startingGravity", 1.05))

            # ABV 및 Brix 계산
            abv = calculate_abv(starting_gravity, gravity)
            brix = calculate_brix(gravity)

            # 발효 진행 상황 계산
            potential_abv = calculate_abv(starting_gravity, 1.0)
            progress = fermentation_progress(abv, potential_abv)

            # 발효 속도 계산
            fermentation_rate = calculate_fermentation_rate(fermentation_data)

            # 남은 발효 기간 추정
            remaining_days = estimate_remaining_days(abv, potential_abv, fermentation_rate)

            # 출력
            print(f"  이름: {name}")
            print(f"  온도: {temperature}°C")
            print(f"  밀도: {gravity} SG")
            print(f"  알코올 함량(ABV): {abv}%")
            print(f"  당도(Brix): {brix}")
            print(f"  발효 진행률: {progress}%")
            print(f"  예상 남은 발효 기간: {remaining_days}일")

            # 데이터 저장
            fermentation_data.append({
                "time": datetime.now() - timedelta(minutes=len(fermentation_data) * 15),
                "specific_gravity": gravity,
                "brix": brix,
                "abv": abv,
            })

        # 상황 판단
        if fermentation_data:
            current_state = fermentation_state(fermentation_data)

            # 시각화
            plot_fermentation_state(fermentation_data, current_state)
        else:
            print("유효한 발효 데이터를 찾을 수 없습니다.")
    else:
        print(f"데이터 가져오기 실패: {response.status_code} - {response.text}")
else:
    print("Bearer 토큰 생성에 실패했습니다.")
