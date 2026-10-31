#include <WiFi.h>
#include <WiFiClient.h>
#include "../arduino/OptipusPeripheral/OptipusPeripheral.h"

const char* WIFI_SSID = "configure-me";
const char* WIFI_PASSWORD = "configure-me";
const char* OPTIPUS_HOST = "192.168.1.10";
const uint16_t OPTIPUS_PORT = 8100;

WiFiClient networkClient;
OptipusPeripheral peripheral(networkClient, OPTIPUS_HOST, OPTIPUS_PORT,
                              "esp32-01", "ESP32 prototype");

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  peripheral.heartbeat();
}

void loop() {
  const float sensorValue = analogRead(34) / 4095.0f * 3.3f;
  peripheral.write("analogVoltage", sensorValue);
  delay(5000);
}

