#include "Arduino.h"
#include "Wire.h"
#include <cassert>
#include <iostream>
uint32_t testTime = 0;
bool testBeat = false;
FakeSerial Serial;
TwoWire Wire;
#include "../firmware/ZOOP/ZOOP.ino"

int main() {
  setup();
  assert(Serial.output.str().find("ms,ir,contact,bpm") != std::string::npos);
  bleServer->callbacks->onConnect(bleServer);
  testBeat = true;
  optical.samples.push_back(60000);
  testTime = 1200;
  loop();
  assert(haveBeat && rateSamples == 0);
  optical.samples.push_back(60000);
  testTime = 2200;
  loop();
  assert(rateSamples == 1 && rates[0] == 60.0f);
  assert(heartRateMeasurement->notifications == 1);
  assert(heartRateMeasurement->value.size() == 2);
  assert(heartRateMeasurement->value[0] == 0 && heartRateMeasurement->value[1] == 60);
  assert(Serial.output.str().find("60.0,1.000,0.000,0.000") != std::string::npos);
  optical.samples.push_back(60000);
  testTime = 2300;
  loop();
  assert(rateSamples == 0); // Implausible interval invalidates the old estimate.
  optical.samples.push_back(0);
  testTime = 2500;
  loop();
  assert(!contact && rateSamples == 0 && !haveBeat);
  optical.samples.push_back(60000);
  testTime = 2600;
  loop();
  assert(haveBeat);
  testTime = 5601;
  loop();
  assert(!haveBeat && rateSamples == 0 && !contact && opticalStalled);
  assert(Serial.output.str().find("ERROR: optical samples stalled") != std::string::npos);
  optical.samples.push_back(60000);
  testTime = 5700;
  loop();
  assert(!opticalStalled && contact);
  assert(Serial.output.str().find("INFO: optical sampling resumed") != std::string::npos);
  bleServer->callbacks->onDisconnect(bleServer);
  loop();
  assert(bleServer->advertisingStarts == 1);
  Wire.fail = true;
  testTime = 6000;
  loop();
  assert(Serial.output.str().find("ERROR: MPU6050 read failed") != std::string::npos);
  std::cout << "Mock firmware checks passed\n";
}
