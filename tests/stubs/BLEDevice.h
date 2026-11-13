#pragma once
#include "Arduino.h"
#include <vector>
class BLEServer;
class BLEServerCallbacks {
 public:
  virtual ~BLEServerCallbacks() = default;
  virtual void onConnect(BLEServer *) {}
  virtual void onDisconnect(BLEServer *) {}
};
class BLEUUID { public: explicit BLEUUID(uint16_t) {} };
class BLE2902 {};
class BLECharacteristic {
 public:
  static constexpr int PROPERTY_NOTIFY = 1;
  std::vector<uint8_t> value;
  int notifications = 0;
  void addDescriptor(BLE2902 *) {}
  void setValue(uint8_t *p, size_t n) { value.assign(p, p + n); }
  void notify() { ++notifications; }
};
class BLEService {
 public:
  BLECharacteristic characteristic;
  BLECharacteristic *createCharacteristic(BLEUUID, int) { return &characteristic; }
  void start() {}
};
class BLEServer {
 public:
  BLEServerCallbacks *callbacks = nullptr;
  BLEService service;
  int advertisingStarts = 0;
  void setCallbacks(BLEServerCallbacks *cb) { callbacks = cb; }
  BLEService *createService(BLEUUID) { return &service; }
  void startAdvertising() { ++advertisingStarts; }
};
class BLEAdvertising {
 public:
  void addServiceUUID(BLEUUID) {}
  void start() {}
};
class BLEDevice {
 public:
  static void init(const char *) {}
  static BLEServer *createServer() { static BLEServer server; return &server; }
  static BLEAdvertising *getAdvertising() { static BLEAdvertising advertising; return &advertising; }
};
