# ZOOP

ZOOP is Zack's experimental DIY fitness-band project, inspired by Whoop, using an ESP32-S3-Zero, an optical pulse sensor and a motion sensor. The intent is to explore how wearable sensing works with parts already on hand. ZOOP is independent of Whoop and does not use its software or branding.

**Status: Concept, not a finished or verified design.** The firmware and electrical and mechanical assumptions must be checked against the actual hardware; don't order a PCB or print a final enclosure yet. There are no finished-product photos or demo video because the device has not been built.

**Not a medical device.** Optical readings are experimental and may be absent or wrong, especially on the wrist or during movement. Do not use ZOOP for diagnosis, treatment, exercise safety decisions or emergencies.

## Design files

- [CAD concept and assumptions](cad/README.txt): a revised geometry generator, OpenSCAD, individual STEP solids, an exploded STEP assembly and a [browser preview](cad/cad_preview.html). **The OpenSCAD, STEP and preview are stale:** they show a 44 × 34 mm perfboard that cannot be cut from the owned 20 × 80 mm board. The generator was revised but regeneration was denied. The 48 × 18 mm revised perfboard and 44 × 18 mm PCB are alternative concepts, not a checked assembly. Source is not an `.FCStd`/`.f3d` file or an Onshape assembly; STEP import has not been verified.
- [Experimental electronics](electronics/README.md): scripted KiCad-format schematic, wire-header carrier, project files and provisional Gerbers. These have not been opened in KiCad or checked for manufacture.
- [Firmware](firmware/ZOOP/ZOOP.ino) and [linked BOM](BOM.csv).

![Illustrative carrier wiring](images/electronics-carrier.svg)

This is an illustrative diagram, **not** a screenshot of the PCB. Real assembly, PCB and schematic screenshots are still required.

## What it does

The draft firmware reads infrared light from the MAX30102 and acceleration and rotation from the MPU6050. It estimates pulse from the optical signal, emits motion and pulse data over USB serial, and advertises a standard Bluetooth Low Energy heart-rate service as **ZOOP**. It does not yet implement sleep staging, recovery or strain scores, SpO₂, a phone app, onboard logging, charging, or Whoop compatibility. BLE is unencrypted: anyone nearby may be able to connect and read the heart-rate estimate. Use only with consent and do not treat it as private.

## Wiring

![Conceptual wiring diagram](images/wiring.svg)

The diagram is conceptual, not a photo or a PCB layout. With power disconnected, connect the signals by the **labels on your exact boards**, not their assumed physical pin order:

| ESP32-S3-Zero | MAX30102 breakout | GY-521 |
|---|---|---|
| 3V3 | VIN/VCC, **only if your breakout accepts 3.3 V here** | VCC, **only if your breakout accepts 3.3 V here** |
| GND | GND | GND and AD0 |
| GPIO5 | SDA | SDA |
| GPIO6 | SCL | SCL |

Leave other pins unconnected. The switch is currently **not wired**; disconnect USB to turn off. Breakout versions differ: verify regulators, sensor supply, LED supply and I²C pull-ups against the specific boards. Both SDA and SCL must be pulled up to a safe 3.3 V logic rail, not 5 V; check existing pull-ups and their combined effective resistance before adding any. Some GY-521 regulators may not run reliably from a 3.3 V input. If either board requires a different supply or level shifting, revise the design before powering it. Never wire a bare LiPo to USB, 5V or 3V3.

For bench tests power the ESP32 via USB-C. For a body-worn prototype use an appropriately protected, isolated battery-powered USB source and disconnect it for charging/programming; do not wear the circuit while connected to a mains-powered computer or charger. Insulate exposed solder joints and avoid tight straps or prolonged skin contact with hot components.

## Firmware

1. Install Arduino IDE and Espressif's ESP32 board support, select **Waveshare ESP32-S3-Zero** where available (or the matching ESP32-S3 board for your actual module), and enable **USB CDC On Boot**. See [Waveshare's Arduino guide](https://docs.waveshare.com/ESP32-S3-Zero/Arduino).
2. Install **SparkFun MAX3010x Pulse and Proximity Sensor Library**, version 1.1.2, from Library Manager. The ESP32 board package supplies Wire and BLE.
3. Open `firmware/ZOOP/ZOOP.ino`, compile and upload. If upload fails, follow your board's BOOT/reset instructions.
4. Open Serial Monitor at 115200 baud. Errors beginning with `# ERROR` identify missing sensors or I²C failures. CSV output contains milliseconds, raw IR, contact flag, estimated BPM (empty until valid), accelerometer values in g and gyro values in degrees/second.
5. To try BLE, use a generic BLE client and subscribe to Heart Rate Measurement `0x2A37` under Heart Rate Service `0x180D`. Measurements are sent approximately once per second only when the firmware considers the pulse valid. Serial is needed for motion data.

The `CONTACT_THRESHOLD` is a starting guess, not a calibrated skin-contact detector. First test on a stationary finger, then characterize wrist placement, pressure, ambient-light sealing, motion artifacts and missed beats against a trustworthy reference. Recalibrate or replace the beat detection before relying on any output; the current algorithm has not been validated on skin.

For a limited host-side logic check, run `g++ -std=c++17 -Wall -Wextra -Werror -Itests/stubs tests/firmware_test.cpp -o /tmp/zoop-firmware-test && /tmp/zoop-firmware-test`. The stubs simulate APIs; this is **not** an ESP32 firmware build or hardware test.

## Bill of materials and funding

See [BOM.csv](BOM.csv). The six named items are marked owned and request $0. Some reference links are generic product or manufacturer links rather than a verified match for your particular breakout. The USB cable, wire, optional custom carrier, enclosure, strap, fasteners and isolated power source are **ownership and cost unknown**; choose actual items, update their links and quotes, and calculate the funding request before submission. A small USB power bank may shut off at low current. The included perfboard is a possible hand-wired alternative to the custom carrier.

## Before submitting

- Verify exact board pinouts, operating voltages, pull-ups, I²C addresses and dimensions. Decide whether perfboard or a custom PCB is the final electrical design.
- Complete and check the enclosure and assembly, including realistic sensor-to-skin position, component mounting, wiring clearances, strap attachment and USB access. Export source assembly and STEP for each modeled part, and include an assembly image.
- For a custom PCB, complete the source schematic, layout, project settings and fabrication exports; run electrical and design-rule checks and inspect footprints. Add real PCB and schematic screenshots.
- Build and test the firmware with the actual board and sensor modules. Measure the accuracy and document known limitations; the source is untested hardware-design firmware.
- Replace BOM placeholders with exact links, prices and a total; write your own motivation and document your work accurately. Check the current submission rules.
- For a **build** submission, add real photos of the finished device, a demo-video link, and update the source files to match the build.

## References

- [SparkFun MAX3010x Arduino library](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library), including its heart-rate beat detector and example.
- [MAX30102 product and datasheet](https://www.analog.com/en/products/max30102.html).
- [MPU-6050 product information](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/).
- [ESP32-S3-Zero documentation](https://www.waveshare.com/wiki/ESP32-S3-Zero).
