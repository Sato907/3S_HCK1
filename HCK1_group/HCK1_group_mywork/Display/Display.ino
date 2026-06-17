#include "Display.h"

WiFiUDP Udp;

const char SSID[] = "";
const char PASS[] = "";

// 静的IP設定（指揮デバイスの送信先 ferrisWheelIP2 と一致させる）
IPAddress localIP(192, 168, 11, 10);
IPAddress gateway(192, 168, 11, 1);
IPAddress subnet(255, 255, 255, 0);

void setup() {
  displaySetup();

  if (SSID[0] != '\0') {
    WiFi.config(localIP, gateway, subnet);
    while (WiFi.begin(SSID, PASS) != WL_CONNECTED) {
      delay(1000);
    }
  }
  Udp.begin(LOCAL_PORT);
}

void loop() {
  checkUDP();
}