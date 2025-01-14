// SerLCD + DHT22 + MQ-135로 만든 프로젝트 1

#include <Wire.h>
#include <SerLCD.h> // SparkFun SerLCD 라이브러리
#include <DHT.h>    // DHT 센서 라이브러리

// LCD 설정
SerLCD lcd; // 기본 I2C 주소 0x72

// DHT 설정
#define DHTPIN 8       // DHT 데이터 핀 (DHT22는 8번 핀에 연결)
#define DHTTYPE DHT22  // DHT22 센서 타입
DHT dht(DHTPIN, DHTTYPE);

// MQ-135 설정
#define MQ135PIN A0    // MQ-135 아날로그 출력 핀

// LED 핀 설정
#define RED_LED 9
#define YELLOW_LED 10
#define GREEN_LED 11

void setup() {
  // I2C 초기화
  Wire.begin();
  
  // LCD 초기화
  lcd.begin(Wire); // I2C 통신 설정
  lcd.setBacklight(0, 0, 25); // 파란색 배경 조명
  lcd.setContrast(3);         // 기본 대비 설정
  lcd.clear();
  lcd.print("Air Monitor");

  // DHT 센서 초기화
  dht.begin();

  // LED 핀 설정
  pinMode(RED_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  // 초기 메시지
  delay(2000);
  lcd.clear();
}

void loop() {
  // DHT22 데이터 읽기
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // MQ-135 데이터 읽기
  int mq135Value = analogRead(MQ135PIN);
  
  // 공기질 상태에 따라 LED 제어
  if (mq135Value < 300) {
    // 공기질 좋음
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, LOW);
  } else if (mq135Value < 600) {
    // 공기질 보통
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, HIGH);
    digitalWrite(RED_LED, LOW);
  } else {
    // 공기질 나쁨
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, HIGH);
  }

  // LCD에 정보 출력
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperature, 1); // 온도
  lcd.print("C");

  lcd.setCursor(0, 1);
  lcd.print("Humid: ");
  lcd.print(humidity, 1); // 습도
  lcd.print("%");

  delay(2000); // 2초 대기
  
  lcd.setCursor(0, 2);
  lcd.print("MQ135: ");
  lcd.print(mq135Value); // MQ-135 값
  delay(2000); // 2초 대기
}
