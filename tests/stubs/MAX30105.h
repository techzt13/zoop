#pragma once
#include "Wire.h"
#include <vector>
#define I2C_SPEED_STANDARD 100000
class MAX30105 {
 public:
  std::vector<uint32_t> samples;
  size_t index = 0;
  bool begin(TwoWire &, int) { return true; }
  void setup(int, int, int, int, int, int) {}
  void setPulseAmplitudeRed(int) {}
  void setPulseAmplitudeIR(int) {}
  void check() {}
  uint8_t available() { return static_cast<uint8_t>(samples.size() - index); }
  uint32_t getFIFOIR() { return samples[index]; }
  void nextSample() { ++index; }
};
