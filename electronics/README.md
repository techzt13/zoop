# ZOOP experimental wire-header carrier

This 44 × 18 mm custom PCB is an alternative to the hand-wired perfboard, not
an ESP32 or sensor module replacement. Each module is wired to its corresponding
header; header pin numbers are not the module pin order. No module footprints,
power switch, charger, protection circuit, battery, sensor pull-ups or mounting
holes are included. Modules and their wiring remain external to the PCB.

| Carrier header | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| J1: ESP32 | 3V3 | GND | GPIO5 / SDA | GPIO6 / SCL | — |
| J2: MAX30102 | 3V3-compatible input | GND | SDA | SCL | — |
| J3: GY-521 | 3V3-compatible input | GND | SDA | SCL | AD0 to GND |

Pin 1 is the square pad. Check actual breakout regulator and pull-up
configuration before connecting: inputs vary and SDA/SCL must not rise above
the ESP32's 3.3 V logic rail. Verify the combined pull-up resistance, the sensor
input supplies and ESP regulator current margin. USB powers the ESP32 only.
With power disconnected, use a multimeter to confirm all nets and no shorts.

`wristband.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_prl`, local symbol
and footprint libraries form the KiCad project. `generate.py` regenerates the
scripted schematic, board and libraries; plots must then be regenerated.
`gerbers.zip` contains KiCad 7.0.11 copper, mask, front silkscreen, edge and
metric Excellon drill exports. The README's PCB and schematic images are
actual KiCad SVG plots.

KiCad 7 loaded both sources, exported a netlist matching the intended pins and
reported zero unconnected PCB connections via its connectivity API. This is
not an ERC/DRC or a fabrication sign-off: run both checks in KiCad, compare
the netlist, inspect Gerbers in a viewer, confirm manufacturer rules and
validate actual connector fit before ordering. The modules, 3.3 V assumptions
and electrical/thermal safety are untested. The alternative perfboard requires
separate wiring and is not the PCB represented by the Gerbers.
