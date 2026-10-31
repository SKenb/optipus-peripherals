#include <Ethernet.h>
#include "../arduino/OptipusPeripheral/OptipusPeripheral.h"

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
EthernetClient networkClient;
OptipusPeripheral peripheral(networkClient, "192.168.1.10", 8100,
                              "arduino-01", "Arduino prototype");

void setup() {
  Ethernet.begin(mac);
  peripheral.heartbeat();
}

void loop() {
  peripheral.write("buttonState", digitalRead(2) == HIGH ? "true" : "false");
  delay(5000);
}
