# ZOOP

**Zack's DIY fitness band. Your sensors. Your data.**

ZOOP is an original, Whoop-inspired experiment built around an ESP32-S3-Zero, a GY-MAX30102 optical pulse sensor and a GY-521 motion sensor. It streams an experimental heart-rate estimate over Bluetooth and pulse/motion data over USB. The goal is to understand wearable sensing using parts already on hand, rather than paying for a closed subscription.

**Design submission, not a finished build.** The rechargeable on-band power system and enlarged case are concepts, not a tested or wearable-ready assembly. Dimensions for the actual modules still need measurement, and the device has not been assembled or tested on a wrist. ZOOP is independent of Whoop: it does not copy proprietary software, work with the Whoop app, or promise equivalent accuracy, battery life, sleep staging, recovery or strain scores.

## Full 3D assembly

![ZOOP assembly including electronics](images/cad-assembly.png)

Open the [FreeCAD assembly](cad/ZOOP_assembly.FCStd). [Assembly STEP](cad/assembly.step), individual part STEP files, modeling source, dimensions and mechanical validation details are in [cad/](cad/). Electronics are explicitly labeled reference-envelope models, not dimensionally certified supplier models.

## Electronics

![ZOOP PCB layout](images/pcb.svg)

![ZOOP schematic](images/schematic.svg)

The compact carrier distributes four signals to wire headers: 3.3 V, GND, SDA and SCL. It is an **alternative** to cutting and hand-wiring the owned perfboard, not a custom replacement for the sensor modules. Header numbers are carrier positions, not the modules' physical pin order.

The [KiCad project](electronics/wristband.kicad_pro), [schematic](electronics/wristband.kicad_sch), [PCB](electronics/wristband.kicad_pcb), local settings, libraries and [Gerber ZIP](electronics/gerbers.zip) are in [electronics/](electronics/README.md). The images are generated from the actual design, not build photos. Read the electrical validation and manufacturing limitations before ordering.

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
2. Choose **one** carrier: cut the owned perfboard to the modeled envelope, or order the checked custom PCB. Use insulated wires, trim header pins for clearance and label both ends. Check continuity and shorts with power disconnected.
3. Before printing, finish the [CAD design](cad/README.txt): the larger case only includes battery and charger reference envelopes. It lacks secure retention, charger port access, wiring and adequate verified battery clearances. The carrier, ESP32 and GY-521 also need verified fasteners. The optical window must face the skin; validate retention and ambient-light shielding rather than covering the sensor lens with opaque material.
4. Compile and upload the firmware below. First test the electronics off-body on USB. Confirm both sensors initialize and that the optical stream changes when a stationary finger is placed over the lens.
5. Only after the power circuit, enclosure and retention have been checked, disconnect all external power for an experimental body-worn test. Adjust the strap loosely enough for circulation. Do not wear the current concept.
6. Subscribe to ZOOP's standard BLE heart-rate service with a generic BLE client, or read USB serial for the full pulse/motion stream.

The [BOM](BOM.csv) lists purchased soldering and measuring tools and remaining candidate assembly tools; borrow tools if available and request only what is needed. The existing Mac laptop is used for CAD and firmware. Printing service costs still need a quote.

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

[BOM.csv](BOM.csv) lists the owned supplies, cable and laptop, and purchased wire, soldering kit and multimeter at **$0 requested**. The remaining provisional subtotal is **$91.76**, including the proposed battery and charger, candidate tools not yet confirmed owned, a $20 print allowance, and $2 for the optional custom PCB. The PCB is an alternative to the owned perfboard; its advertised starting price is not a quote. Retail pack sizes and linked prices are shown.

This is **not a final funding request**: the $20 allowance for printing the case, lid and optical retainer is not a quote and could be too low; shipping, tax and any extra mounting materials are also unquoted. Prices are dated US retail listings, including older search-indexed listings, not live checkout quotes; confirm current prices, availability, local voltage and delivery before ordering. The caliper listing was in-store only. Confirm which tools can be borrowed and request only eligible essentials. Get a print quote after revising the design and obtain checkout totals for the destination.

The battery power concept and its enlarged enclosure have not been tested and are not Whoop-sized. Do not order a case print until the mechanical and electrical design is complete.

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
