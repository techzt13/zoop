"""Generate the ZOOP v3 full-contents packaging model.

Coordinates are millimetres. X runs across the wrist (strap direction), Y runs
along the forearm, and Z rises from the skin. Every intended internal part is
represented; see README.txt for which dimensions are published and which are
assumptions that must be measured before printing.
"""
import itertools
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Mesh
from FreeCAD import Vector

HERE = os.getcwd()
doc = App.newDocument("ZOOP_v3_full_contents")

# Vertical stack.
FLOOR = 1.6        # case floor; MAX30102 board rests on it
GY_RIB = 0.6       # clearance for solder bumps under the GY-521
TRAY_B = 5.9       # underside of battery tray
TRAY_T = 6.7       # battery rests here
BAT_T = TRAY_T + 4.75
DECK_B = 12.05     # 0.6 mm swelling allowance above the battery
DECK_T = 12.85
BOARD_B = 14.35    # 1.5 mm for pin stubs and solder joints under boards
BOARD_T = BOARD_B + 1.6
LID_B = 24.85
LID_T = 26.45
WIRE_OD = 1.4      # assumed 26 AWG silicone wire outside diameter

PRINTED, COMPONENT, WIRING = "printed", "component", "wiring"
REGISTRY = []


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(x, y, z0, z1, r):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0))


def fuse(shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.removeSplitter()


def cut(shape, tools):
    for tool in tools:
        shape = shape.cut(tool)
    return shape.removeSplitter()


def add(name, label, shape, color, kind, transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.LineColor = (0.12, 0.14, 0.18)
    obj.ViewObject.Transparency = transparency
    REGISTRY.append((obj, kind))
    return obj


def settle():
    import time
    for _ in range(20):
        Gui.updateGui()
        time.sleep(0.05)


def export_step(objects, path):
    Part.export(objects, path)
    with open(path, encoding="utf-8") as stream:
        lines = stream.read().splitlines()
    with open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(line.rstrip() for line in lines) + "\n")


# Adafruit 6092 placement, from its published Eagle board file. Board-local
# coordinates (0..29.21, 0..19.05) map to global (CX + x, CY + y).
CX, CY = -14.61, -2.5
CHG_HOLES = [(CX + x, CY + y) for x, y in
             [(2.54, 2.54), (26.67, 2.54), (2.54, 16.51), (26.67, 16.51)]]
PILLARS = [(-12.0, 19.5), (12.0, 19.5)]


def build_case():
    shell = box(-19, -24, 0, 19, 24, LID_B).cut(box(-17, -22, FLOOR, 17, 22, LID_B + 1))
    parts = [shell]
    for s in (1, -1):
        tab = box(19, -12, 0, 22.4, 12, 5) if s > 0 else box(-22.4, -12, 0, -19, 12, 5)
        slot = box(19, -9.8, -1, 21, 9.8, 6) if s > 0 else box(-21, -9.8, -1, -19, 9.8, 6)
        parts.append(tab.cut(slot))
    # Deck ledges; gaps leave room for the riser, battery leads and pillars.
    parts += [
        box(16.4, -22, 11.25, 17, 22, DECK_B),
        box(-17, -22, 11.25, -16.4, -11.6, DECK_B),
        box(-17, 7.0, 11.25, -16.4, 22, DECK_B),
    ]
    for x0, x1 in [(-16.4, -14.6), (-9.4, -3.8), (3.8, 9.4), (14.6, 16.4)]:
        parts.append(box(x0, 21.4, 11.25, x1, 22, DECK_B))
    parts += [cyl(x, y, FLOOR, LID_B, 2.4) for x, y in PILLARS]
    # MAX30102 locating fences (0.8 mm tall, 0.1 mm clearance).
    parts += [
        box(7.1, 2, FLOOR, 7.7, 14, FLOOR + 0.8),
        box(-7.7, 8, FLOOR, -7.1, 14, FLOOR + 0.8),
        box(-4, 0.3, FLOOR, 6, 0.9, FLOOR + 0.8),
        box(-6, 15.1, FLOOR, 6, 15.7, FLOOR + 0.8),
    ]
    # GY-521 support ribs and side fence.
    parts += [
        box(-10.5, -21.5, FLOOR, 2.7, -20.9, FLOOR + GY_RIB),
        box(-10.5, -0.9, FLOOR, 2.7, -0.3, FLOOR + GY_RIB),
        box(3.0, -21, FLOOR, 3.6, -1, FLOOR + 1.4),
    ]
    parts += [box(11, -11, FLOOR, 13, -9, TRAY_B), box(11, 7, FLOOR, 13, 9, TRAY_B)]
    case = fuse(parts)
    tools = [
        box(-3.2, 5.95, -1, 3.2, 10.05, FLOOR + 0.1),            # optical window
        box(-19.1, 0.775, 14.08, -16.9, 13.275, 21.08),          # charger USB-C
        box(-19.1, -17.4, 15.85, -16.9, -14.6, LID_B + 0.1),     # switch notch
        box(-8, -22.9, 23.1, 8, -21.95, 24.1),                   # lid tongue slot
        box(-19.1, -19, 14.6, -18.0, -13, 18.7),                 # fingernail recess
        box(16.9, -18.8, 15.2, 19.1, -5.8, LID_B + 0.1),         # ESP USB notch
    ]
    tools += [cyl(x, y, LID_B - 8.1, LID_B + 0.1, 0.85) for x, y in PILLARS]
    return cut(case, tools)


def build_lid():
    lid = box(-19, -24, LID_B, 19, 24, LID_T)
    lid = fuse([
        lid,
        box(17.1, -18.6, 15.4, 19, -6.0, LID_B),                 # fills ESP notch
        box(-19, -17.3, 17.55, -17.1, -14.7, LID_B),             # fills switch notch
        box(-7.5, -21.9, 23.0, 7.5, -21.1, LID_B),               # tongue stem
        box(-7.5, -22.7, 23.2, 7.5, -21.9, 24.0),                # tongue into wall
        cyl(CHG_HOLES[2][0], CHG_HOLES[2][1], BOARD_T, LID_B, 1.5),
        cyl(CHG_HOLES[3][0], CHG_HOLES[3][1], BOARD_T, LID_B, 1.5),
        cyl(-10.5, -19.5, BOARD_T, LID_B, 1.5),                  # presses carrier
    ])
    return cut(lid, [cyl(x, y, LID_B - 0.1, LID_T + 0.1, 1.2) for x, y in PILLARS])


def build_tray():
    rim = 9.5
    parts = [
        box(-13.9, -21.75, TRAY_B, 16.35, 16.9, TRAY_T),
        box(-13.9, -21.75, TRAY_T, -13.1, 16.7, rim),
        box(-13.9, -21.75, TRAY_T, 15.6, -20.95, rim),
        box(-13.9, 15.9, TRAY_T, -3.8, 16.7, rim),
        box(3.8, 15.9, TRAY_T, 16.35, 16.7, rim),
        box(-13.9, -21.75, rim, -13.1, -20.95, DECK_B),
        box(-13.9, 15.9, rim, -13.1, 16.7, DECK_B),
        box(15.6, -21.75, TRAY_T, 16.35, -20.95, DECK_B),
        box(15.6, 15.9, TRAY_T, 16.35, 16.7, DECK_B),
        # Feet press the sensor boards onto the floor (corners assumed clear).
        box(5.7, 1.1, 3.2, 6.9, 2.3, TRAY_B),
        box(5.7, 13.7, 3.2, 6.9, 14.9, TRAY_B),
        box(-6.9, 13.7, 3.2, -5.7, 14.9, TRAY_B),
        box(1.5, -21.3, 3.8, 2.7, -20.1, TRAY_B),
        box(1.5, -1.5, 3.8, 2.7, -0.5, TRAY_B),
    ]
    return fuse(parts)


def build_deck():
    deck = box(-16.75, -21.75, DECK_B, 16.75, 21.75, DECK_T)
    parts = [deck]
    for x, y in CHG_HOLES:
        parts.append(cyl(x, y, DECK_T, BOARD_B, 2.0))
        parts.append(cyl(x, y, BOARD_B, BOARD_B + 1.2, 1.1))     # locating pin
    parts += [
        box(-13.6, -21.7, DECK_T, 16.3, -20.8, BOARD_B),
        box(-13.6, -3.7, DECK_T, 16.3, -2.9, BOARD_B),
    ]
    deck = fuse(parts)
    tools = [
        box(-17, -11.6, DECK_B - 1, -14.1, 7.0, DECK_T + 1),     # sensor riser
        box(-3.8, 19.4, DECK_B - 1, 2.8, 21.8, DECK_T + 1),      # battery leads
    ]
    tools += [cyl(x, y, DECK_B - 1, DECK_T + 1, 2.65) for x, y in PILLARS]
    return cut(deck, tools)


def main():
    case = add("CaseBase", "01 v3 case", build_case(), (0.68, 0.74, 0.81), PRINTED)
    lid = add("Lid", "02 v3 lid", build_lid(), (0.82, 0.87, 0.93), PRINTED, 60)
    tray = add("BatteryTray", "03 v3 battery tray", build_tray(), (0.95, 0.75, 0.30), PRINTED)
    deck = add("ElectronicsDeck", "04 v3 electronics deck", build_deck(),
               (0.40, 0.60, 0.90), PRINTED)
    printed = [case, lid, tray, deck]

    green = (0.15, 0.45, 0.25)
    add("MAX30102", "GY-MAX30102: assumed 14 x 14 mm, IC to skin", fuse([
        box(-7, 1, FLOOR, 7, 15, 3.2),
        box(-2.8, 6.35, 0.05, 2.8, 9.65, FLOOR),
        box(-5.4, 2.2, 3.2, 5.4, 13.8, 4.55),
    ]), (0.60, 0.29, 0.64), COMPONENT)
    add("GY521", "GY-521: 21.2 x 16.4 x 3.3 mm (Addicore)", fuse([
        box(-13.5, -21.5, FLOOR + GY_RIB, 2.9, -0.3, FLOOR + GY_RIB + 1.6),
        box(-10.5, -20.0, FLOOR + GY_RIB + 1.6, 1.3, -1.8, FLOOR + GY_RIB + 3.3),
    ]), (0.16, 0.65, 0.67), COMPONENT)
    add("Battery", "Adafruit 1578 500 mAh: 36 x 29 x 4.75 mm",
        box(-12.7, -20.5, TRAY_T, 16.3, 15.5, BAT_T), (0.85, 0.85, 0.80), COMPONENT)
    chg_pcb = cut(box(CX, CY, BOARD_B, CX + 29.21, CY + 19.05, BOARD_T),
                  [cyl(x, y, BOARD_B - 1, BOARD_T + 1, 1.25) for x, y in CHG_HOLES])
    add("Charger", "Adafruit 6092 bq25185: 29.21 x 19.05 mm (Eagle)", fuse([
        chg_pcb,
        box(-15.75, 2.555, BOARD_T, -8.4, 11.495, BOARD_T + 3.26),     # USB-C
        box(-4.64, 8.49, BOARD_T, 3.36, 19.6, BOARD_T + 4.8),         # JST PH mated
        box(7.06, 2.97, BOARD_T, 13.36, 11.09, LID_B - 0.5),          # terminal block
        box(-8.4, 1.9, BOARD_T, 7.06, 8.49, BOARD_T + 1.25),
        box(3.36, 8.49, BOARD_T, 7.06, 16.3, BOARD_T + 1.25),
        box(-8.4, 8.49, BOARD_T, -4.64, 16.3, BOARD_T + 1.25),
        box(7.06, 11.09, BOARD_T, 9.8, 16.3, BOARD_T + 1.25),
    ]), green, COMPONENT)
    add("ChargerJoints", "Charger EN 3V GND solder joints below pads",
        box(0.4, -0.8, 13.1, 9.8, 0.9, BOARD_B), (0.75, 0.75, 0.75), COMPONENT)
    carrier = cut(box(-16.75, -21.75, BOARD_B, 16.5, -2.8, BOARD_T),
                  [box(-17, -11.6, BOARD_B - 1, -14.1, -2.7, BOARD_T + 1)])
    add("Carrier", "Owned perfboard cut to 33.25 x 18.95 mm",
        carrier, (0.68, 0.41, 0.20), COMPONENT)
    add("ESP32S3Zero", "ESP32-S3-Zero 23.5 x 18 mm, USB-C to +X", fuse([
        box(-7.2, -21.3, BOARD_T + 0.2, 16.3, -3.3, BOARD_T + 1.2),
        box(-6.9, -20.8, BOARD_T + 1.2, 9.3, -3.8, BOARD_T + 2.4),
        box(9.3, -16.77, BOARD_T + 1.2, 16.6, -7.83, BOARD_T + 4.46),
    ]), (0.15, 0.32, 0.70), COMPONENT)
    add("ESPJoints", "ESP pin stubs below carrier", fuse([
        box(-6.0, -20.42, 13.1, 15.0, -19.42, BOARD_B),
    ]), (0.75, 0.75, 0.75), COMPONENT)
    add("ESPJoints2", "ESP pin stubs below carrier",
        box(-6.0, -5.18, 13.1, 15.0, -4.18, BOARD_B), (0.75, 0.75, 0.75), COMPONENT)
    add("BusJoints", "Perfboard bus solder joints",
        box(-13.4, -20.6, 13.1, -7.6, -4.0, BOARD_B), (0.75, 0.75, 0.75), COMPONENT)
    add("Switch", "MSK-12C02 switch on charger EN", fuse([
        box(-16.9, -20, BOARD_T, -14.1, -12, BOARD_T + 1.4),
        box(-18.5, -16.5, BOARD_T + 0.3, -16.9, -15.5, BOARD_T + 1.1),
    ]), (0.25, 0.25, 0.25), COMPONENT)

    wire = (0.95, 0.20, 0.20)
    wiring = [
        ("WireMAX", "4 wires MAX30102 to riser", [box(-14.1, 1.4, 3.2, -5.6, 7.0, 4.6)], 4),
        ("WireGY", "4 wires GY-521 plus AD0 link", [box(-14.1, -17.3, 3.8, -11.7, -0.7, 5.2)], 5),
        ("WireRiser", "8 sensor wires to carrier", [
            box(-17, -11.6, FLOOR, -14.1, 7.0, TRAY_B),
            box(-17, -11.6, TRAY_B, -14.1, -2.9, BOARD_T)], 8),
        ("WireBus", "Wire fan-out on carrier", [
            box(-14.1, -16.5, BOARD_T, -7.4, -2.9, BOARD_T + WIRE_OD),
            box(-17, -11.6, BOARD_T, -14.1, -2.9, BOARD_T + WIRE_OD)], 12),
        ("WirePower", "Charger 3V GND EN to carrier",
         [box(-14.1, -3.2, BOARD_T, 9.8, -0.4, BOARD_T + 2 * WIRE_OD)], 3),
        ("BatteryLeads", "Battery leads and slack to JST", [
            box(-3.6, 15.5, TRAY_T, 3.6, 21.5, DECK_B),
            box(-3.6, 19.6, DECK_B, 2.6, 21.5, BOARD_T + 4.8)], 2),
    ]
    for name, label, boxes, _count in wiring:
        add(name, "Wire envelope: " + label, fuse(boxes), wire, WIRING)
    # (envelope, wires crossing the narrowest section, section width x height)
    capacity = [
        ("WireMAX along X", 4, 5.6, 1.4),
        ("WireGY along X", 4, 16.6, 1.4),
        ("WireGY AD0 link along Y", 1, 2.4, 1.4),
        ("WireRiser floor run along Y", 4, 2.9, 4.3),
        ("WireRiser vertical", 8, 2.9, 8.7),
        ("WireBus fan-out along Y", 6, 9.6, 1.4),
        ("WirePower along X", 3, 2.8, 2 * WIRE_OD),
        ("BatteryLeads through deck", 2, 6.2, 1.9),
    ]

    doc.recompute()
    objects = [obj for obj, _ in REGISTRY]
    kinds = {obj.Name: kind for obj, kind in REGISTRY}
    report = [
        "ZOOP v3 full-contents model: FreeCAD %s" % ".".join(App.Version()[:3]),
        "Units: mm and mm^3. Assumed dimensions are listed in README.txt.",
    ]
    for obj in objects:
        shape = obj.Shape
        if not shape.isValid() or len(shape.Solids) != 1 or shape.Volume <= 0:
            raise RuntimeError("Invalid or non-single solid: " + obj.Name)
        report.append("%s: valid; one solid; volume %.3f" % (obj.Name, shape.Volume))

    collisions = []
    for a, b in itertools.combinations(objects, 2):
        if kinds[a.Name] == WIRING and kinds[b.Name] == WIRING:
            continue  # wire envelopes merge where bundles join
        overlap = a.Shape.common(b.Shape).Volume
        if overlap > 1e-6:
            collisions.append("%s / %s: %.6f" % (a.Name, b.Name, overlap))
    report.append("Positive-volume intersections between parts: %d" % len(collisions))
    report.extend(collisions)

    hardware = [o for o in objects if kinds[o.Name] != WIRING]
    access = [
        ("charger USB-C plug", box(-30, 1.025, 14.38, -16.0, 13.025, 20.78), hardware),
        ("ESP USB-C plug with lid removed", box(16.85, -18.3, 15.48, 30, -6.3, 22.08),
         [o for o in hardware if o is not lid]),
        ("switch actuator fingernail access", box(-22, -18, 15.6, -18.5, -14, 17.45), hardware),
        ("optical window below sensor", box(-2.8, 6.35, -3, 2.8, 9.65, 0.05), hardware),
        ("strap slot +X", box(19, -9.8, -3, 21, 9.8, 8), hardware),
        ("strap slot -X", box(-21, -9.8, -3, -19, 9.8, 8), hardware),
    ]
    for label, path, against in access:
        hits = [o.Name for o in against if o.Shape.common(path).Volume > 1e-6]
        if hits:
            collisions.append("%s blocked by %s" % (label, ", ".join(hits)))
        report.append("Access path clear: %s" % label if not hits
                      else "Access path BLOCKED: %s" % label)

    # Every loose part must be lowerable into the case from above.
    for obj in objects:
        if obj in (case, lid) or kinds[obj.Name] == WIRING:
            continue
        travel = LID_T + 1 - obj.Shape.BoundBox.ZMin
        dz, blocked = 0.25, False
        while dz <= travel:
            moved = obj.Shape.copy()
            moved.translate(Vector(0, 0, dz))
            if moved.common(case.Shape).Volume > 1e-6:
                blocked = True
                break
            dz += 0.5
        if blocked:
            collisions.append("%s cannot be lowered into the case (hit at +%.2f mm)"
                              % (obj.Name, dz))
    report.append("Top-down insertion of every printed part and module: %s"
                  % ("clear" if not any("lowered" in c for c in collisions) else "BLOCKED"))

    per_wire = WIRE_OD * WIRE_OD
    for name, count, width, height in capacity:
        section = width * height
        ok = section >= count * per_wire
        report.append("%s: %d wires need %.1f mm^2 at %.1f mm OD; smallest section %.1f mm^2 %s"
                      % (name, count, count * per_wire, WIRE_OD, section,
                         "OK" if ok else "TOO SMALL"))
        if not ok:
            collisions.append("Wire envelope too small: " + name)
    if collisions:
        raise RuntimeError("\n".join(report))

    bounds = case.Shape.BoundBox
    report.append("Case footprint including strap bars: %.1f x %.1f mm"
                  % (bounds.XLength, bounds.YLength))
    report.append("Case body without strap bars: 38.0 x 48.0 mm")
    report.append("Height with lid: %.2f mm (excluding screw heads and strap)" % LID_T)

    for obj in printed:
        base = obj.Name.lower()
        step = os.path.join(HERE, base + ".step")
        export_step([obj], step)
        imported = Part.read(step)
        if (not imported.isValid() or len(imported.Solids) != 1
                or abs(imported.Volume - obj.Shape.Volume) > max(1e-4, obj.Shape.Volume * 1e-6)):
            raise RuntimeError("STEP round-trip failed: " + obj.Name)
        stl = os.path.join(HERE, base + ".stl")
        Mesh.export([obj], stl)
        mesh = Mesh.Mesh(stl)
        if not mesh.isSolid() or mesh.CountFacets == 0:
            raise RuntimeError("STL is not a closed solid mesh: " + obj.Name)
        for axis in ("XLength", "YLength", "ZLength"):
            if abs(getattr(mesh.BoundBox, axis) - getattr(obj.Shape.BoundBox, axis)) > 0.05:
                raise RuntimeError("STL bounds differ from source: " + obj.Name)
        report.append("%s: STEP reimport valid; STL closed with matching bounds" % obj.Name)

    export_step(objects, os.path.join(HERE, "assembly.step"))
    merged = Part.read(os.path.join(HERE, "assembly.step"))
    if not merged.isValid() or len(merged.Solids) != len(objects):
        raise RuntimeError("Assembly STEP reimport failed")
    report.append("Assembly STEP reimport: %d valid solids" % len(merged.Solids))
    report.append("These checks do not prove physical fit, safety, comfort or pulse accuracy.")

    App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool(
        "UseNavigationAnimations", False)
    doc.recompute()
    doc.saveAs(os.path.join(HERE, "ZOOP_v3_full_contents.FCStd"))
    lid.Placement.Base.z = 14
    case.ViewObject.Transparency = 70
    doc.recompute()
    view = Gui.activeDocument().activeView()
    settle()
    view.viewAxonometric()
    settle()
    view.fitAll()
    settle()
    view.saveImage(os.path.join(HERE, "assembly-preview.png"), 1600, 1000, "White")
    with open(os.path.join(HERE, "validation_report.txt"), "w") as stream:
        stream.write("\n".join(report) + "\n")
    print("CAD SUCCESS\n" + "\n".join(report), flush=True)


try:
    main()
except Exception:
    traceback.print_exc()
    with open(os.path.join(HERE, "build_error.txt"), "w") as stream:
        stream.write(traceback.format_exc())
finally:
    App.closeDocument(doc.Name)
    Gui.getMainWindow().close()
