#include "Display.h"

WiFiUDP Udp;

const char SSID[] = "";
const char PASS[] = "";

void setup() {
  displaySetup();

  if (SSID[0] != '\0') {
    while (WiFi.begin(SSID, PASS) != WL_CONNECTED) {
      delay(1000);
    }
  }
  Udp.begin(LOCAL_PORT);
}

void loop() {
  checkUDP();
}