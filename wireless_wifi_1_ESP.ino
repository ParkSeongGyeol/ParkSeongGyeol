#include <WiFi.h>
#include <PubSubClient.h>

// Wi-Fi 정보
const char* ssid = "SK_WiFiGIGADD00_2.4G";
const char* password = "JCW4B@4407";

// MQTT 서버 정보
const char* mqtt_server = "192.168.45.135"; // 브로커 서버 IP
const int mqtt_port = 1883;                 // 브로커 포트

// Wi-Fi 및 MQTT 클라이언트 객체 생성
WiFiClient espClient;
PubSubClient client(espClient);

// 데이터 저장용 변수
String sensorData;

void setup() {
  // 시리얼 통신 초기화
  Serial.begin(9600);

  // Wi-Fi 연결
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected!");

  // MQTT 연결
  client.setServer(mqtt_server, mqtt_port);
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("MQTT connected!");
    } else {
      delay(2000);
    }
  }
}

void loop() {
  // 아두이노로부터 데이터 수신
  if (Serial.available()) {
    sensorData = Serial.readStringUntil('\n');

    // MQTT로 데이터 전송
    client.publish("home/sensors", sensorData.c_str());
    Serial.println("Data sent: " + sensorData);
  }

  // MQTT 연결 유지
  client.loop();
}
