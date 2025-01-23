#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h" // DHT 센서를 사용하는 경우

// Wi-Fi 설정
const char* ssid = "SK_WiFiGIGADD00_2.4G";           // Wi-Fi 이름
const char* password = "JCW4B@4407";   // Wi-Fi 비밀번호

// MQTT 브로커 설정
const char* mqtt_server = "192.168.45.135"; // 브로커 서버 IP
const int mqtt_port = 1883;               // 브로커 포트
const char* mqtt_user = "username";       // 브로커 사용자 이름 (필요 시)
const char* mqtt_password = "password";   // 브로커 비밀번호 (필요 시)

// MQTT 주제(Topic)
const char* topic_temp = "esp32/temperature";
const char* topic_hum = "esp32/humidity";

// DHT 센서 설정
#define DHTPIN 4           // DHT 데이터 핀 (GPIO4 사용 예시)
#define DHTTYPE DHT22      // DHT 센서 유형
DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected");
}

void reconnect() {
  // MQTT 연결
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) { // 인증 필요 시
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Wi-Fi 및 MQTT 초기화
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);

  // DHT 센서 초기화
  dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // DHT 센서 데이터 읽기
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (!isnan(temperature) && !isnan(humidity)) {
    // MQTT 메시지 전송
    char tempStr[8];
    char humStr[8];
    dtostrf(temperature, 1, 2, tempStr);
    dtostrf(humidity, 1, 2, humStr);

    client.publish(topic_temp, tempStr);
    client.publish(topic_hum, humStr);

    Serial.print("Temperature: ");
    Serial.println(tempStr);
    Serial.print("Humidity: ");
    Serial.println(humStr);
  }

  delay(5000); // 데이터 전송 간격
}
