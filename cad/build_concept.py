"""FreeCAD GUI macro implementation; see README.txt before using outputs."""
import os
import itertools
import traceback
import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector

HERE = os.getcwd()
IMG = os.path.abspath(os.path.join(HERE, '..', 'images'))
doc = App.newDocument('ZOOP_Prototype')

def box(x0,y0,z0,x1,y1,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,Vector(x0,y0,z0))

def cylinder(x,y,z,r,h):
    return Part.makeCylinder(r,h,Vector(x,y,z))

def fused(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()

def add(name, label, shape, color, transparency=0):
    obj = doc.addObject('PartDesign::Feature', name)
    obj.Label = label
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.LineColor = (0.12,0.14,0.18)
    obj.ViewObject.Transparency = transparency
    return obj

def main():
    # The enclosure is one connected print.  The four pillars blend into the wall.
    base = box(-29,-18,0,29,18,15).cut(box(-27,-16,2,27,16,15.1))
    ears = [box(-39,-12,0,-29,12,4), box(29,-12,0,39,12,4)]
    rails = [box(-23,-10,2,23,-8.15,6), box(-23,8.15,2,23,10,6)]
    guides = [box(4,y0,z0,17,y1,z1)
              for y0,y1 in [(-8.15,-7.5),(7.5,8.15)]
              for z0,z1 in [(2,3.35),(5.05,5.5)]]
    stops = [box(17,y0,2,17.8,y1,5.5) for y0,y1 in
             [(-8.15,-7.5),(7.5,8.15)]]
    stops.append(box(3,-7,2,3.9,7,3.4))
    pillars = [cylinder(x,y,2,3.2,13) for x in (-25,25) for y in (-13,13)]
    base = fused([base] + ears + rails + guides + stops + pillars)
    for cut in [box(-35.5,-9.8,-1,-32,9.8,5),box(32,-9.8,-1,35.5,9.8,5),
                box(7,-2.8,-1,15,2.8,2.1),box(-30,-6,8.5,-26,6,13)]:
        base = base.cut(cut)
    positions = [(x,y) for x in (-25,25) for y in (-13,13)]
    for x,y in positions:
        base = base.cut(cylinder(x,y,7,1,8.1))
    base = base.removeSplitter()
    shell = add('CaseBase','01 Case base, rails and optical guides',base,(0.68,0.74,0.81))
    lidshape = fused([box(-29,-18,15,29,18,17)] +
                    [box(x0,y0,7.6,x1,y1,15) for x0,x1 in [(-20,-14),(14,20)]
                     for y0,y1 in [(-10.2,-8.4),(8.4,10.2)]])
    for x,y in positions:
        lidshape = lidshape.cut(cylinder(x,y,14.9,1.15,2.2))
    lid = add('Lid','02 Lid with carrier edge keepers',lidshape.removeSplitter(),(0.82,0.87,0.93),65)
    carrier = add('Carrier','03 Carrier 44 x 18 x 1.6 placeholder',box(-22,-9,6,22,9,7.6),(0.68,0.41,0.20))
    add('OpticalRetainer','03b Optical slide stop (print separately)',box(3,-8.1,3.4,3.9,8.1,6),(0.90,0.65,0.15))
    esp = fused([box(-22,-8.4,7.6,1.5,8.4,9.2),box(-14,-4,9.2,-7,4,11.0),
                 box(-25.3,-4.5,9.2,-21.5,4.5,12.2)])
    add('ESP','04 ESP32-S3-Zero and USB placeholder',esp,(0.15,0.32,0.70))
    gyro = fused([box(2,-8,7.6,22,8,9.2),box(9,-3,9.2,15,3,10.5)])
    add('GY521','05 GY-521 placeholder',gyro,(0.16,0.65,0.67))
    optical = fused([box(4,-8,3.4,17,8,5),box(8,-1.65,1.85,13.6,1.65,3.4)])
    add('MAX30102','06 MAX30102 breakout and sensor placeholder',optical,(0.60,0.29,0.64))
    for sign, name in [(-1,'LeftStrap'),(1,'RightStrap')]:
        # Folded geometry is a short representational sample, not the full strap.
        def sb(x0,y0,z0,x1,y1,z1):
            if sign < 0: return box(-x1,y0,z0,-x0,y1,z1)
            return box(x0,y0,z0,x1,y1,z1)
        strip = fused([sb(33,-9,5,80,9,6), sb(33,-9,-1,34,9,5),
                       sb(33,-9,-2,40,9,-1), sb(39,-9,-2,40,9,6)])
        add(name,'07 '+name+' folded 18 mm fabric sample',strip,(0.19,0.25,0.32))
    screws=[]
    for i,(x,y) in enumerate(positions,1):
        screw = fused([cylinder(x,y,9,0.9,8),cylinder(x,y,17,1.9,1.2)])
        screws.append(add('Screw%d'%i,'08 M2 x 8 pan screw %d envelope'%i,screw,(0.55,0.57,0.61)))
    doc.recompute()
    objs = list(doc.Objects)
    report=['FreeCAD %s kernel solid and STEP checks'%'.'.join(App.Version()[:3]),
            'Units: mm, mm^3; assembled coordinates, including fastener and strap placeholders.']
    for obj in objs:
        s=obj.Shape
        if not s.isValid() or len(s.Solids)!=1 or s.Volume <= 0:
            raise RuntimeError('Invalid or non-single solid: '+obj.Name)
        file=os.path.join(HERE,obj.Name.lower()+'.step')
        Part.export([obj], file)
        imported=Part.read(file)
        if not imported.isValid() or len(imported.Solids)!=1 or abs(imported.Volume-s.Volume)>max(1e-4,s.Volume*1e-6):
            raise RuntimeError('STEP round-trip failed: '+obj.Name)
        report.append('%s: valid; 1 solid; volume %.4f; STEP reimport %.4f' % (obj.Name,s.Volume,imported.Volume))
    Part.export(objs, os.path.join(HERE,'assembly.step'))
    merged=Part.read(os.path.join(HERE,'assembly.step'))
    if not merged.isValid() or len(merged.Solids)!=len(objs):
        raise RuntimeError('Assembly STEP import invalid or unexpected solid count')
    report.append('Assembly STEP: valid; %d solids' % len(merged.Solids))
    bad=[]
    for a,b in itertools.combinations(objs,2):
        volume=a.Shape.common(b.Shape).Volume
        if volume>1e-6: bad.append((a.Name,b.Name,volume))
    report.append('Pairwise positive-volume intersections > 0.000001 mm^3: %d'%len(bad))
    report.extend('%s / %s: %.6f mm^3'%(a,b,v) for a,b,v in bad)
    if bad: raise RuntimeError('\n'.join(report))
    doc.recompute()
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.updateGui()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    doc.recompute()
    doc.saveAs(os.path.join(HERE,'ZOOP_assembly.FCStd'))
    # Explode only the lid and its screws for a readable screenshot; saved model stays assembled.
    lid.Placement.Base.z=14
    for screw in screws: screw.Placement.Base.z=14
    doc.recompute()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    Gui.activeDocument().activeView().saveImage(os.path.join(IMG,'cad-assembly.png'),1600,1000,'White')
    lid.Placement.Base.z=0
    for screw in screws: screw.Placement.Base.z=0
    doc.recompute()
    with open(os.path.join(HERE,'validation_report.txt'),'w') as f: f.write('\n'.join(report)+'\n')
    print('CAD SUCCESS\n'+'\n'.join(report), flush=True)

try:
    main()
except Exception:
    traceback.print_exc()
    with open(os.path.join(HERE,'build_error.txt'),'w') as f: f.write(traceback.format_exc())
finally:
    App.closeDocument(doc.Name)
    Gui.getMainWindow().close()
