#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "dheena_dk7";
const char* password = "12346789";
const char* serverURL = "http://10.236.133.254:5000/data";

#define RXD2 16
#define TXD2 17

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting ESP32...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("Serial2 Started");
}

void loop() {

  if (WiFi.status() == WL_CONNECTED) {

    if (Serial2.available()) {

      String data = Serial2.readStringUntil('\n');
      data.trim();

      if (data.length() > 0) {

        Serial.println("📡 Raw Data: " + data);

        float temp = extractFloat(data, "TEMP:");
        float hum  = extractFloat(data, "HUM:");
        float gas  = extractFloat(data, "GAS:");

        // Only send if valid values found
        if (temp != 0 || hum != 0 || gas != 0) {
          sendToServer(temp, hum, gas);
        } else {
          Serial.println("⚠ Invalid data received (all zero)");
        }
      }
    }
  }

  delay(2000);
}

float extractFloat(String data, String key) {

  int start = data.indexOf(key);
  if (start == -1) return 0.0;

  start += key.length();

  int end = data.indexOf(',', start);
  if (end == -1) {
    end = data.length();
  }

  String valueStr = data.substring(start, end);
  valueStr.trim();

  return valueStr.toFloat();
}

void sendToServer(float temp, float hum, float gas) {

  HTTPClient http;

  Serial.println("Sending data to server...");

  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["temperature"] = temp;
  doc["humidity"] = hum;
  doc["gas"] = gas;

  String payload;
  serializeJson(doc, payload);

  Serial.println("Payload: " + payload);

  int response = http.POST(payload);

  Serial.print("POST Response: ");
  Serial.println(response);

  if (response > 0) {
    String responseBody = http.getString();
    Serial.println("Server Response: " + responseBody);
  } else {
    Serial.println("❌ HTTP Request Failed");
  }

  http.end();
}