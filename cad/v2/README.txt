ZOOP v2 — unpowered fit-study, not a finished wearable
=====================================================

This is a separate second iteration, not a replacement for the earlier
assembly in cad/. It explores a shorter footprint for the user's wrist and
the proposed 500 mAh battery. It has not been printed or physically tested.
Do not install or charge a battery in this model or wear it with electronics.

Files for an unpowered test print:
  casebase.step / casebase.stl       case and strap slots
  lid.step / lid.stl                 lid
  opticalretainer.step / .stl        sensor slide stop

The STEP and STL parts use the same assembled millimetre coordinates. In the
slicer, put each part flat on the build plate and use 100% scale. STL has no
unit metadata: ensure the slicer treats it as millimetres. Print separately.
ZOOP_v2_fit_study.FCStd is the editable FreeCAD assembly; assembly.step
includes the printable parts and simplified component envelopes. The image is
a CAD preview, not a photo. Regenerate from this directory using FreeCAD
1.1.4 and regenerate.FCMacro; build_concept.py contains the source.

Dimensions and fit
------------------
The case is 40 x 44 mm without the strap tabs, 48 x 44 mm including them,
and 34 mm tall with the 2 mm lid, excluding screws and fabric. This is about
29 mm shorter between strap-tab tips than the 77 mm print Zack measured, but
is substantially thicker. It is not guaranteed to fit his wrist: if the
usable flat width were exactly 47 mm, the 48 mm span would still overhang
about 0.5 mm per side when centered. Measure his wrist before deciding.

Both slots are 19.6 x 2 mm in the model for approximately 19 mm webbing.
There is only about 1 mm of modeled material on either side of each slot.
Tab strength, print orientation, layer adhesion, fabric thickness, bending,
comfort and abrasion have not been tested; do not rely on them to hold a
wearable. The optical slide stop is retained only by its fit in the guide
notches; it can lift out and needs a positive retention method. The guides
assume a 14 x 14 x 1.6 mm board with 0.1 mm modeled clearance. Verify the
actual board, sensor position and printer tolerances before any modification
or force-fitting. The sensor is recessed relative to the outside of the case;
skin contact, light leakage and sensor pressure remain unresolved.

The lid has four nominal 2.4 mm clearance holes, and the case has 1.7 mm
pilot holes for the candidate M2 x 8 mm self-tapping screws. The pilot and
engagement are only starting points: the real screw, printed material and
hole size must be tested separately. The lid does not retain the carrier or
battery, and the case has no waterproofing.

Reference component envelopes
-----------------------------
These are only simple solids positioned as a packaging study. They do not
include connector housings, solder, pins, wires, solder joints, all component
heights, antenna clearances or tolerances:

  ESP32-S3-Zero: 23.5 x 18 mm board outline; actual variant unconfirmed.
  GY-521: assumed 20 x 16 mm board outline; actual variant unconfirmed.
  GY-MAX30102: assumed 14 x 14 mm board; actual variant unconfirmed.
  Perfboard: placeholder 34 x 18 x 1.6 mm; not a verified wiring layout.
  Adafruit 1578 battery: 36 x 29 x 4.75 mm, plus unmodeled leads and connector.
  Adafruit 6092 charger: 30.2 x 19 x 10 mm, plus unmodeled plugs and wiring.

The batteries and charger are in the shopping cart, not confirmed purchased.
The sensor boards and ESP are owned but were not available to measure.
Published breakout dimensions are examples, not proof of the user's units.
The modeled component envelopes have no positive-volume intersections;
that does not establish assembly feasibility. In particular, no wire routing,
USB port access, battery cushioning or retention, electrical insulation,
board fasteners, antenna keepout or power-source isolation is designed.
Do not cut or compress the battery pouch or install it against screw bosses.
The planned charger defaults to 1 A: set its jumper to 500 mA before
connecting the 500 mAh battery, and never connect ESP32 USB while the
external charger output is attached to its 3.3 V rail.

Research references, accessed 2026-11-25
---------------------------------------
Waveshare ESP32-S3-Zero dimensions (23.5 x 18 mm):
https://www.cnx-software.com/2024/08/07/waveshare-esp32-s3-zero-is-a-tiny-wifi-and-ble-iot-module-with-a-usb-c-port-up-to-32-gpios/
Waveshare antenna and variant information:
https://docs.waveshare.com/ESP32-S3-Zero
Representative GY-521 dimensions; variants may differ:
https://www.datasheethub.com/gy521-mpu6050-3-axis-digital-gyroscope-accelerometer-sensor-module
Example GY-MAX30102 dimensions; not a verified match:
https://www.hestore.eu/en/prod_10048077.html
MAX30102 IC dimensions, distinct from its breakout board:
https://www.analog.com/en/products/max30102.html
Adafruit 500 mAh battery and permitted charging current:
https://www.adafruit.com/product/1578
Adafruit bq25185 charger dimensions and current setting:
https://www.adafruit.com/product/6092
Measuring the flat wrist width and strap-tip span:
https://watch-standard.com/lug-to-lug-watch-sizing/
Screw pilot holes require material-specific testing:
https://www.kemi.team/en/docs/3d-print-fasteners-inserts/
Pouch-cell support, insulation and strain relief:
https://www.aovoltbattery.com/news/lithium-ion-pouch-cell-design/

Validation scope
----------------
validation_report.txt records FreeCAD solid and STEP reimport checks, closed
STL meshes with matching bounds, open strap slots and optical aperture, and
nonintersection of the simplified solids. These checks do not prove physical
fit, printability, battery protection, electrical safety, pulse accuracy or
wrist comfort. The next steps are wrist measurements, a harmless empty-case
fit test, actual component measurements and a complete power and retention
redesign before any powered assembly.
