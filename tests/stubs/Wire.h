#pragma once
#include "Arduino.h"
struct TwoWire {
  uint8_t reg = 0;
  uint8_t bytes[14] = {};
  size_t offset = 0;
  bool fail = false;
  void begin(int, int, int) {}
  void beginTransmission(uint8_t) { reg = 0; }
  void write(uint8_t value) { if (!reg) reg = value; }
  int endTransmission(bool = true) { return fail ? 1 : 0; }
  uint8_t requestFrom(uint8_t, uint8_t count) {
    if (fail) return 0;
    offset = 0;
    if (reg == 0x75) bytes[0] = 0x68;
    else {
      for (auto &byte : bytes) byte = 0;
      bytes[0] = 0x40; // +1 g X
    }
    reg = 0;
    return count;
  }
  int read() { return bytes[offset++]; }
};
extern TwoWire Wire;
