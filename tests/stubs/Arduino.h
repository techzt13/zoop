#pragma once
#include <cstdint>
#include <cstddef>
#include <sstream>
#include <iomanip>
extern uint32_t testTime;
inline uint32_t millis() { return testTime; }
inline void delay(uint32_t ms) { testTime += ms; }
struct FakeSerial {
  std::ostringstream output;
  void begin(int) {}
  template <typename T> void print(T value) { output << value; }
  void print(float value, int digits) { output << std::fixed << std::setprecision(digits) << value; }
  template <typename T> void println(T value) { print(value); output << '\n'; }
  void println() { output << '\n'; }
};
extern FakeSerial Serial;
