ZOOP mechanical concept — not a finished or validated wearable
=============================================================

A shorter second-iteration unpowered fit study is in v2/README.txt. It is a
separate concept, not a validated replacement for the assembly below.

The latest model is v3/README.txt: it includes every planned internal part,
wire route, retention feature and port opening, and supersedes the power and
retention gaps described below. It is still unverified against real parts.

ZOOP_assembly.FCStd is a FreeCAD 1.1.4 document with separate solids for
the case, lid, carrier, optical retainer, module and rechargeable power
reference envelopes, straps and screws. assembly.step and the individual STEP files use assembled
coordinates. build_concept.py and regenerate.FCMacro regenerate the document,
STEP files and a FreeCAD view screenshot; run the macro from this directory.
The exported parts represent the model as it was generated, not measured
supplier part models. Open and inspect the document before modifying it.

The FreeCAD kernel checked each part as a valid single solid, reimported each
STEP and the assembly, and checked positive-volume overlap between modeled
parts; see validation_report.txt. This does not prove a functional assembly,
fit, wiring clearance, tolerances, material strength or safe skin contact.

Dimensions and assembly
-----------------------
The case is approximately 58 x 44 x 34 mm, excluding strap loops and screw
heads. The strap slots have about 19.6 mm clear width and are intended for
thin 3/4-inch (19.05 mm) webbing; test fabric thickness and strength. The
strap solids are short folded reference shapes, not a complete wrist strap.

Carrier is a 44 x 18 x 1.6 mm envelope. Either trim the owned 20 x 80 mm
perfboard to this envelope; verify
available holes and clearance before cutting. Case rails support the carrier;
the enlarged lid no longer has carrier keepers. The MAX30102 board slides between underside
guides facing the aperture. The separate optical retainer is a loose stop;
its retention in the guides and wire routing need physical verification.
There are no modeled fasteners for the ESP or GY-521 reference boards: design
and verify a secure attachment before wearing. Wiring, header pins, pull-ups,
plug shell and cable bend radius are not modeled.

The case has four 2 mm blind pilot holes and the lid four 2.3 mm clearance
holes, for four nominal M2 x 8 mm pan-head self-tapping screws. The screw
geometry is an envelope, not threads. Check the actual screw profile, pilot
diameter, print orientation and adequate wall strength; do not overtighten.
The printed retainer requires tolerance tests; adjust the CAD
to match your actual 3D-printing process.

The ESP32-S3-Zero and GY-521 PCB outlines are approximate; component heights
are placeholders. The GY-MAX30102 board is an assumed 13 x 16 mm envelope,
with an approximate 5.6 x 3.3 mm sensor; breakout versions differ. The
optical sensor surface is near the outer case face and needs a smooth safe
skin interface and light barrier, neither of which has been validated.
Verify all dimensions, retention and electrical clearances using your actual
modules before printing or ordering. The enclosure is not waterproof.

Power is a preliminary concept, not a finished or safe-to-wear design. The
model includes a 29 x 36 x 4.75 mm battery bounding box and a 30.2 x 19 x
10 mm charger/regulator bounding box above the existing electronics. These
are reference envelopes, not actual supplier models or mechanically retained
parts; battery leads, charger terminals, plugs, tolerances, separation,
insulation, protective padding and access for charging are not modeled.
There is no battery restraint or carrier retention, and no verified switch or
USB source isolation. Design and validate these before ordering a print or
wearing the prototype. The case is much thicker than a commercial band.

See the main README for the proposed battery and charger and the mandatory
charge-current and USB source-separation precautions. Do not connect a bare
battery directly to the ESP32.
