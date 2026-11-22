# ZOOP

**Zack's DIY fitness band. Your sensors. Your data.**

ZOOP is an original, Whoop-inspired experiment built around an ESP32-S3-Zero, a GY-MAX30102 optical pulse sensor and a GY-521 motion sensor. It streams an experimental heart-rate estimate over Bluetooth and pulse/motion data over USB. The goal is to understand wearable sensing using parts already on hand, rather than paying for a closed subscription.

**Design submission, not a finished build.** The rechargeable on-band power system and enlarged case are concepts, not a tested or wearable-ready assembly. Dimensions for the actual modules still need measurement, and the device has not been assembled or tested on a wrist. ZOOP is independent of Whoop: it does not copy proprietary software, work with the Whoop app, or promise equivalent accuracy, battery life, sleep staging, recovery or strain scores.

## Full 3D assembly

![ZOOP assembly including electronics](images/cad-assembly.png)

Open the [FreeCAD assembly](cad/ZOOP_assembly.FCStd). [Assembly STEP](cad/assembly.step), individual part STEP files, modeling source, dimensions and mechanical validation details are in [cad/](cad/). Electronics are explicitly labeled reference-envelope models, not dimensionally certified supplier models.

## Electronics

The build uses the owned **perfboard**, not an ordered PCB. An earlier [custom carrier design](electronics/README.md) is retained for reference but is not part of the build or the purchase request.

### Wiring

![Prototype wiring](images/wiring.png)

This earlier image shows the USB-powered sensor prototype, **not the rechargeable power system**. With power disconnected, wire sensors by the **labels on your exact modules**:

| ESP32-S3-Zero | GY-MAX30102 | GY-521 |
|---|---|---|
| 3V3 | VIN/VCC, if verified 3.3 V compatible | VCC, if verified 3.3 V compatible |
| GND | GND | GND and AD0 |
| GPIO5 | SDA | SDA |
| GPIO6 | SCL | SCL |

The MAX30102 normally uses I²C address `0x57`; grounding MPU6050 AD0 selects `0x68`. Leave unused INT, XDA, XCL and other signals disconnected. The MSK-12C02 is listed as owned but **unused**: unplugging USB alone will not turn off a battery-powered circuit. Some versions are rated only 50 mA and must not switch ESP32 power directly.

**Breakout variants differ.** Inspect the actual regulators, LED supply and I²C pull-ups. SDA/SCL must not be pulled to 5 V, and the combined pull-up resistance must be suitable for the shared bus. Some GY-521 regulators will not operate reliably from a 3.3 V input. If either module cannot accept the assumed supply, revise the wiring and schematic before powering it; do not infer safety from its marketplace name.

### Rechargeable power concept

![Unverified rechargeable power concept](images/power-concept.svg)

The proposed on-band supply is a protected [500 mAh LiPo](https://www.adafruit.com/product/1578) and [bq25185 charger/3.3 V buck board](https://www.adafruit.com/product/6092). Before connecting the battery, set the charger's current to **500 mA**, following the [manufacturer's guide](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-3-3v-buck-board/overview): its default 1 A exceeds this battery's specified maximum. Verify the battery connector polarity; JST connectors from other suppliers can be reversed.

The intended battery-powered configuration is the charger board's **3.3 V output** to the ESP32 3V3 and sensor 3.3 V rail, with grounds common. Never connect the battery to the ESP32 or 3.3 V rail directly. The charger output can fall to 3.0 V as the battery empties; operation, brownout behavior and runtime with the actual boards are untested. The existing carrier schematic is a signal distribution board only: it does **not** show or include the charger, battery, source selection or protection.

**Do not connect ESP32 USB while the charger 3.3 V output is connected to its 3V3 pin:** the two supplies may backfeed. For programming or USB serial, disconnect the charger output from the ESP32 rail first; for battery operation, unplug ESP32 USB before reconnecting it. Use a removable, insulated connection until a properly engineered power-path selector is designed. Charge off-body, with the ESP32 USB disconnected, and never wear it connected to a computer or mains charger. The existing 50 mA switch is not specified to switch the load safely.

## Build and use

1. Measure board outlines, thicknesses, header orientation, sensor position and USB plug clearance. Adjust the CAD parameters and regenerate exports before printing. Verify the actual electrical requirements above.
2. Use the owned perfboard as the carrier; do not cut it until the fit and hole positions are verified. Use insulated wires, trim header pins for clearance and label both ends. Check continuity and shorts with power disconnected.
3. Before printing, finish the [CAD design](cad/README.txt): the larger case only includes battery and charger reference envelopes. It lacks secure retention, charger port access, wiring and adequate verified battery clearances. The carrier, ESP32 and GY-521 also need verified fasteners. The optical window must face the skin; validate retention and ambient-light shielding rather than covering the sensor lens with opaque material.
4. Compile and upload the firmware below. First test the electronics off-body on USB. Confirm both sensors initialize and that the optical stream changes when a stationary finger is placed over the lens.
5. Only after the power circuit, enclosure and retention have been checked, disconnect all external power for an experimental body-worn test. Adjust the strap loosely enough for circulation. Do not wear the current concept.
6. Subscribe to ZOOP's standard BLE heart-rate service with a generic BLE client, or read USB serial for the full pulse/motion stream.

The [BOM](BOM.csv) lists purchased soldering and measuring tools and remaining candidate assembly tools; borrow tools if available and request only what is needed. The existing Mac laptop is used for CAD and firmware. Printing service costs still need a quote.

### Physical testing plan

These tests have not been performed on ZOOP hardware. Work off-body on a nonconductive surface; disconnect all power before changing wires.

1. Verify the actual sensor boards' supply and I²C levels. Solder headers or wires securely, then check each intended connection and check for shorts between power and ground or adjacent pins with the multimeter.
2. Leave the battery and charger disconnected. Connect both sensors according to the wiring table, then upload the firmware over ESP32 USB. Open the Serial Monitor at 115200 baud. Sensor errors require disconnecting power and fixing the wiring before retrying.
3. Check that the serial IR values change when the optical sensor is covered, that motion values change when the MPU6050 moves, and that a BLE client can discover ZOOP. These are basic communication checks, not evidence of heart-rate accuracy.
4. Once the power circuit has been reviewed and the charge-current jumper set to 500 mA, check the charger's regulated output with the multimeter before connecting it to the ESP32. Never connect ESP32 USB and the external 3.3 V output at the same time. Measure battery-powered runtime and compare a resting pulse with a manual count only after safe source isolation and retention have been designed; do not wear the current case.

## Firmware

Source: [firmware/ZOOP/ZOOP.ino](firmware/ZOOP/ZOOP.ino).

Install Arduino IDE or Arduino CLI, **Espressif ESP32 core 3.3.5**, and **SparkFun MAX3010x Pulse and Proximity Sensor Library 1.1.2**. Select the matching ESP32-S3 board and enable **USB CDC On Boot**. For a Waveshare board, follow its [Arduino instructions](https://docs.waveshare.com/ESP32-S3-Zero/Arduino). If flashing fails, use your board's BOOT/reset sequence.

The reproducible compile target used by [CI](.github/workflows/firmware.yml) is:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc firmware/ZOOP
```

The default generic ESP32-S3 target does not enable PSRAM; the firmware does not require it. Do not flash a different board's flash/PSRAM settings without checking your hardware.

Serial Monitor at **115200 baud** prints:

```text
ms,ir,contact,bpm,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps
```

BPM is empty until plausible beat intervals have been collected. The starting contact threshold is uncalibrated. An optical-sampling stall or implausible interval invalidates the estimate; sensor initialization/read errors are reported explicitly. The MPU6050 scales are ±2 g and ±250 degrees/second. There is no onboard recording; save serial data on your computer if needed.

Over BLE, the device name is **ZOOP**, Heart Rate Service is `0x180D`, and Heart Rate Measurement is `0x2A37`. Enable notifications. Approximate BPM is sent about once a second when valid; no pulse estimate is sent when invalid. Your client must handle stale/absent notifications. Motion data is currently USB-only.

**BLE is unencrypted and not authenticated.** Nearby people may connect and read estimates. Use only with consent; this is not private health-data storage.

## BOM and funding

[BOM.csv](BOM.csv) lists the owned supplies, jumper wires, cable and laptop, and purchased wire, soldering kit and multimeter at **$0 requested**. The remaining provisional subtotal is **$83.45**, including the proposed battery and charger, candidate tools not yet confirmed owned, an unconfirmed webbing starting price and a $20 print allowance. The hook-and-loop tape and screws are in the cart, not yet purchased; their Hong Kong dollar prices are converted at HK$7.83787 per US dollar, a reference rate reported on 2026-11-22, not a checkout exchange rate. No custom PCB is requested. Solder is listed as a conditional purchase, not included in the subtotal, until the purchased kit's contents are confirmed.

This is **not a final funding request**: the $20 allowance for printing the case, lid and optical retainer is not a quote and could be too low; shipping, tax and any extra mounting materials are also unquoted. Prices include dated retail listings and converted cart prices, not final checkout quotes; confirm current prices, availability, local voltage and Hong Kong delivery before ordering. The caliper listing was in-store only. Confirm which tools can be borrowed and request only eligible essentials. Get a print quote after revising the design and obtain checkout totals for the destination.

The battery power concept and its enlarged enclosure have not been tested and are not Whoop-sized. Power-source isolation and battery retention still need design, so the BOM cannot yet guarantee a complete final shopping list. Do not order a case print until the mechanical and electrical design is complete.

## Validation and honest limitations

Firmware has a real ESP32-S3 compile in GitHub Actions and focused host-side tests. Host tests can be reproduced with:

```sh
g++ -std=c++17 -Wall -Wextra -Werror -Itests/stubs tests/firmware_test.cpp -o /tmp/zoop-test
/tmp/zoop-test
```

The FreeCAD solids and STEP round trips passed geometric checks; KiCad 9 ERC and DRC with schematic parity passed. Details and assumptions are documented beside the sources. Passing these and the firmware compile does **not** establish physical fit, electrical compatibility, reliable wrist pulse detection, manufacturing acceptance or safe prolonged wear. Complete board retention, wire routing and exact module measurements before calling the design finished.

**Not a medical device.** Motion, light, pressure, skin contact and sensor quality can make readings wrong. Do not use ZOOP for diagnosis, treatment, exercise safety decisions or emergencies. Never wear it connected to a mains-powered charger/computer; never connect a LiPo directly to USB, 5V or 3V3. Protect the cell from puncture, crushing, heat and shorts; insulate joints, stop if anything warms or irritates skin, and keep this non-waterproof prototype away from sweat and water.

For a design review, verify your actual modules and update dimensions and prices. Program approval and funding are determined by Fallen organizers.

For a **build submission**, add genuine finished-product photos and a real demo-video link, document measured behavior, and update every source/export to match what was built. None are fabricated here.

## References and license

- [SparkFun MAX3010x library](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library): the included firmware calls its `heartRate.h` beat detector; library source and licensing remain upstream.
- [MAX30102 manufacturer information](https://www.analog.com/en/products/max30102.html).
- [MPU6050 manufacturer information](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/).
- [ESP32-S3-Zero documentation](https://www.waveshare.com/wiki/ESP32-S3-Zero).

Original ZOOP source and documentation are [MIT-licensed](LICENSE). Supplier/module references are credited; their trademarks and designs belong to their respective owners.
