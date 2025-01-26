import numpy as np  # NumPy는 배열 계산을 위해 필수적입니다.

class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, initial_estimate):
        """
        칼만 필터 초기화
        :param process_variance: 프로세스 노이즈의 분산 (예: 시스템의 예측 불확실성)
        :param measurement_variance: 측정 노이즈의 분산 (예: 센서 데이터의 신뢰도)
        :param initial_estimate: 초기 상태 값 (초기 추정 값)
        """
        self.process_variance = process_variance  # Q
        self.measurement_variance = measurement_variance  # R
        self.estimate = initial_estimate  # x(0)
        self.error_covariance = 1.0  # 초기 오차 공분산 값 P(0)

    def update(self, measurement):
        """
        새 측정 값을 기반으로 상태를 업데이트합니다.
        :param measurement: 새로운 측정 값 (센서 또는 데이터)
        :return: 업데이트된 상태 값 (예측 값)
        """
        # 1. 칼만 이득 계산
        kalman_gain = self.error_covariance / (self.error_covariance + self.measurement_variance)
        # 2. 상태 추정 업데이트 (추정값 보정)
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        # 3. 오차 공분산 업데이트 (오차 감소)
        self.error_covariance = (1 - kalman_gain) * self.error_covariance + self.process_variance
        return self.estimate

# 테스트 코드 (실행 예제)
if __name__ == "__main__":
    # 초기화 (프로세스 노이즈, 측정 노이즈, 초기 추정 값)
    kf = KalmanFilter(process_variance=0.1, measurement_variance=1.0, initial_estimate=25.0)

    # 가상의 측정 데이터 (예: 온도 측정값)
    measurements = [24.5, 24.8, 25.1, 25.5, 25.3]

    print("Initial estimate:", kf.estimate)
    for i, measurement in enumerate(measurements):
        estimate = kf.update(measurement)
        print(f"Step {i + 1}: Measurement={measurement}, Estimate={estimate:.2f}")
