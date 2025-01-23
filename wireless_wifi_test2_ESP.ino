#include <WiFi.h>

// Wi-Fi 설정
const char* ssid = "SK_WiFiGIGADD00_2.4G";           // Wi-Fi 이름
const char* password = "JCW4B@4407";   // Wi-Fi 비밀번호
const char* deviceName = "ESP32_Device";       // ESP32 기기 이름


void setup() {
  Serial.begin(115200);
  delay(100); // 시리얼 안정화
  Serial.println("\n--- ESP32 Wi-Fi Connection Test ---");

  // Wi-Fi 연결 시작
  Serial.println("Calling WiFi.begin...");
  WiFi.begin(ssid, password);
  delay(1000);
  Serial.println("WiFi.begin called, waiting for connection...");

  // 연결 상태 확인
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("WiFi Status: ");
    Serial.println(WiFi.status()); // 상태 코드 출력
    delay(1000);
    Serial.print(".");
    attempts++;
    if (attempts > 15) {
      Serial.println("\nFailed to connect to Wi-Fi.");
      ESP.restart();
    }
  }

  Serial.println("\nWi-Fi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 현재 Wi-Fi 상태 출력
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 5000) { // 5초마다 상태 확인
    Serial.println("--- Wi-Fi Status ---");
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    lastPrint = millis();
  }
}
