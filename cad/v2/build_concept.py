"""Generate the ZOOP v2 unpowered fit-study assembly and printable parts."""
import itertools
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Mesh
from FreeCAD import Vector

HERE = os.getcwd()
doc = App.newDocument("ZOOP_v2_fit_study")


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cylinder(x, y, z, radius, height):
    return Part.makeCylinder(radius, height, Vector(x, y, z))


def fuse(shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.removeSplitter()


def add(name, label, shape, color, transparency=0):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.LineColor = (0.12, 0.14, 0.18)
    obj.ViewObject.Transparency = transparency
    return obj


def export_step(objects, path):
    Part.export(objects, path)
    with open(path, encoding="utf-8") as stream:
        lines = stream.read().splitlines()
    with open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(line.rstrip() for line in lines) + "\n")


def main():
    case = box(-20, -22, 0, 20, 22, 32).cut(
        box(-18, -20, 2, 18, 20, 32.1)
    )
    ears = [box(-24, -12, 0, -20, 12, 4), box(20, -12, 0, 24, 12, 4)]
    guides = [
        box(x0, -10, 2, x1, 8, 5.8)
        for x0, x1 in [(-8.5, -7.1), (7.1, 8.5)]
    ]
    ledges = [
        box(x0, -8, z0, x1, 7.1, z1)
        for x0, x1 in [(-7.7, -6.5), (6.5, 7.7)]
        for z0, z1 in [(2, 3.3), (5.1, 5.8)]
    ]
    rear_stop = box(-7.1, 7.1, 2, 7.1, 8, 5.8)
    screw_positions = [(x, y) for x in (-17.5, 17.5) for y in (-19.5, 19.5)]
    pillars = [cylinder(x, y, 2, 2.4, 30) for x, y in screw_positions]
    case = fuse([case] + ears + guides + ledges + [rear_stop] + pillars)
    for slot in [
        box(-23, -9.8, -1, -21, 9.8, 4.2),
        box(21, -9.8, -1, 23, 9.8, 4.2),
        box(-4, -2.8, -1, 4, 2.8, 2.1),
    ]:
        case = case.cut(slot)
    # Open a guide channel with 0.1 mm clearance around the assumed sensor board.
    case = case.cut(box(-7.1, -8.1, 3.3, 7.1, 7.1, 5.1))
    case = case.cut(box(-7.7, -9.8, 3.3, 7.7, -8.1, 5.9))
    for x, y in screw_positions:
        case = case.cut(cylinder(x, y, 24, 0.85, 8.1))
    case = add("CaseBase", "01 v2 case - fit study only", case.removeSplitter(),
               (0.68, 0.74, 0.81))

    lid = box(-20, -22, 32, 20, 22, 34)
    for x, y in screw_positions:
        lid = lid.cut(cylinder(x, y, 31.9, 1.2, 2.2))
    lid = add("Lid", "02 v2 lid - M2 pilot test required", lid.removeSplitter(),
              (0.82, 0.87, 0.93), 55)

    retainer = add(
        "OpticalRetainer", "03 v2 loose optical slide stop",
        box(-7.6, -9.7, 3.4, 7.6, -8.2, 5.7), (0.90, 0.65, 0.15)
    )

    # Reference boxes are not component models or proof of wiring clearance.
    add("Carrier", "Reference: assumed 34 x 18 mm perfboard",
        box(-17, -9, 6, 17, 9, 7.6), (0.68, 0.41, 0.20))
    add("ESP", "Reference: ESP32-S3-Zero board outline only",
        box(-17.8, -11.75, 7.6, 0.2, 11.75, 9.2), (0.15, 0.32, 0.70))
    add("GY521", "Reference: GY-521 board outline only",
        box(1.1, -10, 7.6, 17.1, 10, 9.2), (0.16, 0.65, 0.67))
    sensor = fuse([
        box(-7, -7, 3.4, 7, 7, 5),
        box(-2.8, -1.65, 1.85, 2.8, 1.65, 3.4),
    ])
    add("MAX30102", "Reference: assumed 14 x 14 mm breakout",
        sensor, (0.60, 0.29, 0.64))
    add("Battery", "Reference: 500 mAh cell envelope; no leads or retention",
        box(-14.5, -18, 14, 14.5, 18, 18.75), (0.85, 0.85, 0.80))
    add("Charger", "Reference: bq25185 board envelope; no plugs or wires",
        box(-15.1, -9.5, 20, 15.1, 9.5, 30), (0.20, 0.50, 0.30))

    doc.recompute()
    objects = list(doc.Objects)
    report = [
        "ZOOP v2 fit-study: FreeCAD %s" % ".".join(App.Version()[:3]),
        "Units: mm and mm^3. Boxes are unverified component envelopes.",
    ]
    for obj in objects:
        shape = obj.Shape
        if not shape.isValid() or len(shape.Solids) != 1 or shape.Volume <= 0:
            raise RuntimeError("Invalid or non-single solid: " + obj.Name)
        report.append("%s: valid; one solid; volume %.4f" % (obj.Name, shape.Volume))

    for obj in (case, lid, retainer):
        basename = obj.Name.lower()
        step = os.path.join(HERE, basename + ".step")
        export_step([obj], step)
        imported = Part.read(step)
        if (not imported.isValid() or len(imported.Solids) != 1
                or abs(imported.Volume - obj.Shape.Volume) > max(1e-4, obj.Shape.Volume * 1e-6)):
            raise RuntimeError("STEP round-trip failed: " + obj.Name)
        stl = os.path.join(HERE, basename + ".stl")
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
    collisions = []
    for a, b in itertools.combinations(objects, 2):
        overlap = a.Shape.common(b.Shape).Volume
        if overlap > 1e-6:
            collisions.append((a.Name, b.Name, overlap))
    report.append("Positive-volume intersections: %d" % len(collisions))
    report.extend("%s / %s: %.6f" % collision for collision in collisions)
    if collisions:
        raise RuntimeError("\n".join(report))

    bounds = case.Shape.BoundBox
    if abs(bounds.XLength - 48) > 1e-6 or abs(bounds.YLength - 44) > 1e-6:
        raise RuntimeError("Case footprint is not 48 x 44 mm")
    if abs(lid.Shape.BoundBox.ZMax - 34) > 1e-6:
        raise RuntimeError("Assembly height is not 34 mm")
    for x in (-22, 22):
        slot = box(x - 1, -9.8, 0, x + 1, 9.8, 4)
        if case.Shape.common(slot).Volume > 1e-6:
            raise RuntimeError("Strap slot is not through the tab")
    aperture = box(-4, -2.8, 0, 4, 2.8, 2)
    if case.Shape.common(aperture).Volume > 1e-6:
        raise RuntimeError("Optical aperture is obstructed")
    report.append("Two 19.6 x 2 mm strap slots and optical aperture: open")
    report.append("Case outer footprint including strap slots: 48 x 44 mm")
    report.append("Case and lid height: 34 mm; excludes screws and webbing")
    report.append("These checks do not prove physical fit, retention, safety, or comfort.")

    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    doc.recompute()
    doc.saveAs(os.path.join(HERE, "ZOOP_v2_fit_study.FCStd"))
    lid.Placement.Base.z = 8
    doc.recompute()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    Gui.activeDocument().activeView().saveImage(
        os.path.join(HERE, "assembly-preview.png"), 1600, 1000, "White"
    )
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
