ZOOP v3 full-contents packaging model - unverified until real parts are measured
================================================================================

v3 is the first ZOOP model that contains every part planned to go inside the
band: both sensors, the ESP32-S3-Zero, the perfboard carrier, the battery, the
charger/3.3 V buck, the slide switch, solder-joint and pin-stub keepouts, and
envelopes for every wire bundle. It also models how each part is held and how
the USB ports, switch, optical window and strap slots are reached.

Files
-----
ZOOP_v3_full_contents.FCStd  FreeCAD 1.1.4 document, all 21 solids
assembly.step                every solid in assembled coordinates
casebase.step/.stl           printed case (print floor-down)
lid.step/.stl                printed lid (print top face down)
batterytray.step/.stl        printed battery tray (feet need supports)
electronicsdeck.step/.stl    printed deck (print plate-down)
build_v3.py                  parametric source; regenerate.FCMacro runs it
validation_report.txt        kernel checks from the last regeneration
assembly-preview.png         isometric view, lid raised 14 mm

Regenerate from this directory:
  FreeCAD regenerate.FCMacro   (or: xvfb-run -a FreeCAD "$PWD/regenerate.FCMacro")

Size
----
Body 38 x 48 mm; 44.8 mm across the wrist including strap bars; 26.45 mm tall
including the lid, excluding screw heads. That is taller than v2 because every
real part is now stacked inside. The biggest single height item is the
charger's 3-way screw-terminal block (about 8.4 mm above its board). If your
charger board has no terminal block fitted, or you desolder it and solder
wires to the pads instead, the lid can drop by roughly 3-4 mm.

Stack, skin side up (Z in mm)
-----------------------------
 0.0 - 1.6   case floor; 6.4 x 4.1 mm optical window under the MAX30102 IC
 1.6 - 3.2   GY-MAX30102 board on the floor, sensor IC facing the skin
 2.2 - 5.5   GY-521 on 0.6 mm ribs beside it, components facing up
 3.2 - 5.9   sensor wires run over the boards to a riser on the -X side
 5.9 - 6.7   battery tray; its feet press both sensor boards down
 6.7 - 11.45 Adafruit 1578 battery, inside 2.8 mm rims
11.45-12.05  0.6 mm swelling allowance
12.05-12.85  electronics deck, resting on case ledges and tray posts
12.85-14.35  pin-stub and solder-joint space under the boards
14.35-15.95  Adafruit 6092 charger (on standoffs/pins) and perfboard carrier
16.15-20.41  ESP32-S3-Zero on its headers; its USB-C at the +X wall
15.95-24.35  charger USB-C, battery JST and terminal block
24.85-26.45  lid (two M2 screws plus a tongue under the -Y wall)

Every part and where its size comes from
----------------------------------------
Adafruit 6092 bq25185 charger: 29.21 x 19.05 mm board, hole positions, USB-C,
  JST PH and terminal block positions read from Adafruit's published Eagle
  board file (github.com/adafruit/Adafruit-bq25185-with-3.3V-Buck-PCB).
Adafruit 1578 500 mAh LiPo: 36 x 29 x 4.75 mm from the product page; lead
  exit position and lead length are assumed.
GY-521: 21.2 x 16.4 x 3.3 mm (common published listing). Clones vary.
MSK-12C02 switch: 8 x 2.8 x 1.4 mm body, 1.6 mm actuator, 50 mA rating.
JST PH: 2.0 mm pitch, mated plug envelope modeled 8 x 11.1 x 4.8 mm.
ESP32-S3-Zero: 23.5 x 18 mm outline and 2.54 mm header rows 15.24 mm apart
  (Waveshare). PCB thickness 1.0 mm, component height and USB-C height
  (3.26 mm) are ASSUMED.
GY-MAX30102: ASSUMED 14 x 14 x 1.6 mm board with a 5.6 x 3.3 mm IC centred.
  Listings disagree; measure yours.
Perfboard: your owned 20 x 80 mm board cut to 33.25 x 18.95 mm, with a
  2.65 x 8.8 mm corner notch for the sensor-wire riser.
Wire: ASSUMED 1.4 mm outside diameter (26 AWG silicone). Each bundle envelope
  is checked for at least OD^2 of cross-section per wire.

Power wiring this model is laid out for
---------------------------------------
Battery JST -> charger. Charger 3.3V pad -> ESP32 3V3 and both sensor VCCs.
Charger GND pad -> common ground. Charger EN pad -> switch common; one switch
throw -> GND. Grounding EN shuts down the charger's 3.3 V buck, so the switch
only carries about 45 uA and never carries the load current. Test which
slider position is OFF with the multimeter before closing the case.
Unused pins on the charger's bottom header are not connected.

Charging: through the charger's USB-C in the -X wall, off the wrist.
Programming: remove the lid, slide the switch OFF, unplug the battery JST, then
  plug USB into the ESP32 through the +X wall notch. Never connect both USB
  ports at once. This procedure is not yet tested; what the buck does when its
  output is held up by the ESP32 is not documented.

Assembly order
--------------
1. Solder sensor wires; place the MAX30102 (IC down over the window) and the
   GY-521 on its ribs; route wires to the -X riser.
2. Drop in the battery tray, then the battery, leads toward +Y.
3. Drop in the deck. Seat the charger on the four locating pins.
4. Fit the carrier with the ESP32 and switch; solder riser and power wires.
5. Plug in the battery JST. Hook the lid tongue under the -Y wall, lower it,
   and fit two M2 x 8 mm screws into the +Y pillars. Lid posts press the
   charger and the carrier down.

What the validation does and does not show
------------------------------------------
Checked by the FreeCAD kernel on every regeneration: each part is one valid
solid; no two parts overlap (wire envelopes may merge with each other); the
charger USB plug, ESP32 USB plug (lid removed), switch actuator, optical
window and both strap slots have clear access paths; every loose part can be
lowered into the case from above; each wire bundle has room for its wires;
every STEP reimports and every STL is a closed mesh with matching bounds.

Not shown: real fit (assumed dimensions above), print tolerances, wall and
screw-boss strength, heat, sweat or water resistance, comfort, light leakage
around the optical window, pulse accuracy, or electrical safety. Measure every
module with a caliper, update build_v3.py, regenerate, and test-print before
trusting this design. Do not wear it until the power circuit is tested.
