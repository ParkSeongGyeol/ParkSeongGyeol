import numpy as np  # NumPy는 배열 계산을 위해 필수적입니다.

class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, initial_estimate):
        """
        칼만 필터 초기화
        - process_variance: 프로세스 노이즈의 분산
        - measurement_variance: 측정 노이즈의 분산
        - initial_estimate: 초기 상태 값
        """
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = initial_estimate
        self.error_covariance = 1.0  # 초기 오차 공분산 값

    def update(self, measurement):
        """
        새 측정 값을 기반으로 상태를 업데이트합니다.
        - measurement: 새 측정 값
        - 반환 값: 업데이트된 상태 값
        """
        # 칼만 이득 계산
        kalman_gain = self.error_covariance / (self.error_covariance + self.measurement_variance)
        # 상태 추정 업데이트
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        # 오차 공분산 업데이트
        self.error_covariance = (1 - kalman_gain) * self.error_covariance + self.process_variance
        return self.estimate
