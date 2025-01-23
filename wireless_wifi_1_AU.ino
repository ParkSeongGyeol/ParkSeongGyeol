#include <DHT.h>

// 핀 정의
#define DHTPIN 8       // DHT22 데이터 핀
#define DHTTYPE DHT22  // DHT22 센서 유형
#define MQ135_PIN A0   // MQ-135 아날로그 핀

// DHT22 센서 객체 생성
DHT dht(DHTPIN, DHTTYPE);

// 시리얼 통신 속도
#define SERIAL_BAUD 9600

void setup() {
  // 센서 초기화
  dht.begin();
  
  // 시리얼 통신 초기화
  Serial.begin(SERIAL_BAUD);    // PC 디버깅용
  Serial1.begin(9600);          // ESP32 통신용
  Serial2.begin(9600);          // MH-Z19E 통신용

  // 초기화 메시지
  Serial.println("System Initialized!");
}

void loop() {
  // DHT22 데이터 읽기
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // MH-Z19E 데이터 읽기
  int co2 = readCO2();

  // MQ-135 데이터 읽기
  int airQuality = analogRead(MQ135_PIN);

  // 데이터 출력
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" °C, Humidity: ");
  Serial.print(humidity);
  Serial.print(" %, CO2: ");
  Serial.print(co2);
  Serial.print(" ppm, Air Quality: ");
  Serial.println(airQuality);

  // 데이터 전송 (ESP32로)
  Serial1.print(temperature);
  Serial1.print(",");
  Serial1.print(humidity);
  Serial1.print(",");
  Serial1.print(co2);
  Serial1.print(",");
  Serial1.println(airQuality);

  // 주기 조절
  delay(2000);
}

// MH-Z19E 센서 CO2 데이터 읽기 함수
int readCO2() {
  byte request[9] = {0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79};
  byte response[9];

  Serial2.write(request, 9);  // 명령 전송
  delay(200);                 // 응답 대기

  if (Serial2.available() >= 9) {
    for (int i = 0; i < 9; i++) {
      response[i] = Serial2.read();
    }

    // 데이터 정렬: 0xFF, 0x86 찾기
    for (int i = 0; i < 7; i++) {
      if (response[i] == 0xFF && response[i + 1] == 0x86) {
        // CO2 데이터 추출
        int high = response[i + 2];
        int low = response[i + 3];
        int ppm = (high << 8) + low;

        // 디버깅 출력
        Serial.print("CO2 Concentration: ");
        Serial.print(ppm);
        Serial.println(" ppm");
        return ppm;
      }
    }

    // 0xFF, 0x86이 없을 경우
    Serial.println("Start bytes not found.");
  } else {
    Serial.println("No response or incomplete response.");
  }
  debugMHZ19E();
  return -1;  // 에러 반환
  

  if (Serial2.available() > 0) {
    Serial2.readBytes(response, 9);
    if (response[0] == 0xFF && response[1] == 0x86) {
      int high = response[2];
      int low = response[3];
      int ppm = (high << 8) + low;
      return ppm;
    }
  }
  return -1; // 오류 발생 시
}

void debugMHZ19E() {
  byte request[9] = {0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79};
  byte response[9];

  Serial2.write(request, 9); // 명령 전송
  delay(100);               // 응답 대기

  if (Serial2.available() >= 9) {
    Serial.println("Response received:");
    for (int i = 0; i < 9; i++) {
      response[i] = Serial2.read();
      Serial.print("Byte ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(response[i], HEX);
    }

    // 유효 응답 확인
    if (response[0] == 0xFF && response[1] == 0x86) {
      int high = response[2];
      int low = response[3];
      int ppm = (high << 8) + low;
      Serial.print("CO2 Concentration: ");
      Serial.print(ppm);
      Serial.println(" ppm");
    } else {
      Serial.println("Invalid response format.");
    }
  } else {
    Serial.println("No response or incomplete response.");
  }
}