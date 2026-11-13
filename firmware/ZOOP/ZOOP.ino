// ZOOP experimental optical pulse and motion logger. Not a medical device.
// Beat detection: SparkFun MAX3010x Sensor Library, heartRate.h.
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>
#include <atomic>

constexpr int SDA_PIN = 5;
constexpr int SCL_PIN = 6;
constexpr uint8_t MPU_ADDR = 0x68;
constexpr uint32_t CONTACT_THRESHOLD = 50000; // Tune on the actual sensor.
constexpr uint32_t BEAT_TIMEOUT_MS = 3000;
constexpr uint32_t OUTPUT_PERIOD_MS = 250;
constexpr uint8_t RATE_COUNT = 4;

MAX30105 optical;
float rates[RATE_COUNT] = {};
uint8_t rateIndex = 0;
uint8_t rateSamples = 0;
uint32_t lastBeat = 0;
uint32_t lastOutput = 0;
uint32_t lastNotification = 0;
uint32_t latestIR = 0;
bool haveBeat = false;
bool contact = false;
std::atomic<bool> bleConnected{false};
bool wasConnected = false;
BLEServer *bleServer = nullptr;
BLECharacteristic *heartRateMeasurement = nullptr;

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *) override { bleConnected = true; }
  void onDisconnect(BLEServer *) override { bleConnected = false; }
};

bool writeMpu(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission() == 0;
}

bool readMpu(uint8_t reg, uint8_t *data, size_t count) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(MPU_ADDR, static_cast<uint8_t>(count)) != count) return false;
  for (size_t i = 0; i < count; ++i) data[i] = Wire.read();
  return true;
}

int16_t signed16(uint8_t high, uint8_t low) {
  return static_cast<int16_t>((static_cast<uint16_t>(high) << 8) | low);
}

void resetRates() {
  haveBeat = false;
  rateSamples = 0;
  rateIndex = 0;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin(SDA_PIN, SCL_PIN, 100000);
  if (!optical.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("# ERROR: MAX30102 not found; check wiring and power, then reset");
    while (true) delay(1000);
  }
  uint8_t id = 0;
  if (!readMpu(0x75, &id, 1) || id != 0x68 ||
      !writeMpu(0x6B, 0x00) || !writeMpu(0x1B, 0x00) ||
      !writeMpu(0x1C, 0x00)) {
    Serial.println("# ERROR: MPU6050 unavailable or configuration failed; check wiring and reset");
    while (true) delay(1000);
  }
  // 100 samples/s, no hardware averaging, red + IR, 18-bit ADC.
  optical.setup(0x1F, 1, 2, 100, 411, 4096);
  optical.setPulseAmplitudeRed(0x1F);
  optical.setPulseAmplitudeIR(0x1F);
  BLEDevice::init("ZOOP");
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new ServerCallbacks());
  BLEService *service = bleServer->createService(BLEUUID(static_cast<uint16_t>(0x180D)));
  heartRateMeasurement = service->createCharacteristic(
      BLEUUID(static_cast<uint16_t>(0x2A37)), BLECharacteristic::PROPERTY_NOTIFY);
  heartRateMeasurement->addDescriptor(new BLE2902());
  service->start();
  BLEAdvertising *advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(BLEUUID(static_cast<uint16_t>(0x180D)));
  advertising->start();
  Serial.println("# Experimental only; BPM is not medically validated");
  Serial.println("ms,ir,contact,bpm,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps");
}

void loop() {
  if (!bleConnected && wasConnected) bleServer->startAdvertising();
  wasConnected = bleConnected;
  optical.check();
  while (optical.available()) {
    uint32_t sampleTime = millis() - (optical.available() - 1) * 10U;
    latestIR = optical.getFIFOIR();
    contact = latestIR >= CONTACT_THRESHOLD;
    if (!contact) {
      resetRates();
    } else if (checkForBeat(latestIR)) {
      if (haveBeat) {
        uint32_t interval = sampleTime - lastBeat;
        if (interval > 0) {
          float bpm = 60000.0f / interval;
          if (bpm >= 40.0f && bpm <= 200.0f) {
            rates[rateIndex] = bpm;
            rateIndex = (rateIndex + 1) % RATE_COUNT;
            if (rateSamples < RATE_COUNT) ++rateSamples;
          } else {
            resetRates();
          }
        }
      }
      lastBeat = sampleTime;
      haveBeat = true;
    }
    optical.nextSample();
  }

  uint32_t now = millis();
  if (haveBeat && now - lastBeat > BEAT_TIMEOUT_MS) resetRates();
  if (now - lastOutput < OUTPUT_PERIOD_MS) return;
  lastOutput = now;

  uint8_t raw[14];
  if (!readMpu(0x3B, raw, sizeof(raw))) {
    Serial.println("# ERROR: MPU6050 read failed");
    return;
  }
  Serial.print(now);
  Serial.print(',');
  Serial.print(latestIR);
  Serial.print(',');
  Serial.print(contact ? 1 : 0);
  Serial.print(',');
  if (rateSamples) {
    float sum = 0;
    for (uint8_t i = 0; i < rateSamples; ++i) sum += rates[i];
    float average = sum / rateSamples;
    Serial.print(average, 1);
    if (bleConnected && now - lastNotification >= 1000) {
      uint8_t measurement[2] = {0, static_cast<uint8_t>(average + 0.5f)};
      heartRateMeasurement->setValue(measurement, sizeof(measurement));
      heartRateMeasurement->notify();
      lastNotification = now;
    }
  }
  for (uint8_t i = 0; i < 3; ++i) {
    Serial.print(',');
    Serial.print(signed16(raw[2 * i], raw[2 * i + 1]) / 16384.0f, 3);
  }
  for (uint8_t i = 0; i < 3; ++i) {
    Serial.print(',');
    Serial.print(signed16(raw[8 + 2 * i], raw[9 + 2 * i]) / 131.0f, 2);
  }
  Serial.println();
}
