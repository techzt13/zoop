#!/usr/bin/env python3
"""Generate the experimental, hand-wired header carrier KiCad sources."""
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "wristband"
NS = uuid.UUID("61f5e443-c04f-4c44-82ce-8b07863790b9")
WIDTH, HEIGHT = 44, 18


def uid(key):
    return str(uuid.uuid5(NS, key))


def write(path, text):
    (ROOT / path).write_text(text, encoding="utf-8")


headers = [
    ("J1", "ESP32-S3-Zero wires", 7.0, ["3V3", "GND", "SDA", "SCL"]),
    ("J2", "GY-MAX30102 wires", 22.0, ["3V3", "GND", "SDA", "SCL"]),
    ("J3", "GY-521 wires", 37.0, ["3V3", "GND", "SDA", "SCL", "GND"]),
]
netids = {"3V3": 1, "GND": 2, "SDA": 3, "SCL": 4}
rows = [4.0 + 2.54 * i for i in range(5)]
tracks = [((7.0, rows[i]), (37.0, rows[i]), "B.Cu", net)
          for i, net in enumerate(["3V3", "GND", "SDA", "SCL"])]
tracks += [
    ((37.0, rows[1]), (39.54, rows[1]), "F.Cu", "GND"),
    ((39.54, rows[1]), (39.54, rows[4]), "F.Cu", "GND"),
    ((39.54, rows[4]), (37.0, rows[4]), "F.Cu", "GND"),
]


def fp_name(n):
    return f"WireHeader_1x{n:02d}_P2.54mm"


def footprint(n, ref=None, x=0, nets=None, value=None):
    name = fp_name(n)
    if ref is None:
        head = f'(footprint "{name}" (version 20221018) (generator wristband_script)\n  (layer "F.Cu")'
        pos = ""
        ref = "REF**"
    else:
        head = f'(footprint "Wristband:{name}" (layer "F.Cu")'
        pos = f'\n  (tstamp {uid(ref)}) (at {x} {rows[0]}) (path "/{uid(ref+"sch")}")'
    out = [head + pos,
           f'  (attr through_hole)',
           f'  (fp_text reference "{ref}" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
           f'  (fp_text value "{value or name}" (at 0 {2.54*(n-1)+2.5:.2f}) (layer "F.Fab") hide (effects (font (size 1 1) (thickness 0.15))))']
    for i in range(n):
        net = "" if nets is None else f' (net {netids[nets[i]]} "/{nets[i]}")'
        out.append(f'  (pad "{i+1}" thru_hole {"rect" if i == 0 else "circle"} '
                   f'(at 0 {2.54*i:.2f}) (size 1.7 1.7) (drill 1) '
                   f'(layers "*.Cu" "*.Mask"){net})')
    return "\n".join(out) + "\n)"


lib = ROOT / "Wristband.pretty"
lib.mkdir(exist_ok=True)
for n in (4, 5):
    write(f"Wristband.pretty/{fp_name(n)}.kicad_mod", footprint(n) + "\n")
write("fp-lib-table", '(fp_lib_table\n  (lib (name "Wristband")(type "KiCad")(uri "${KIPRJMOD}/Wristband.pretty")(options "")(descr "Unverified generic wire headers"))\n)\n')

board = ['(kicad_pcb (version 20221018) (generator wristband_script)',
         '  (general (thickness 1.6))',
         '  (paper "A4")',
         '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (49 "F.Fab" user))',
         '  (setup (pad_to_mask_clearance 0))',
         '  (net 0 "")']
board += [f'  (net {number} "/{name}")' for name, number in netids.items()]
board += [footprint(len(nets), ref, x, nets, value) for ref, value, x, nets in headers]
for i, (start, end, layer, net) in enumerate(tracks):
    board.append(f'  (segment (start {start[0]} {start[1]:.2f}) (end {end[0]} {end[1]:.2f}) (width 0.5) (layer "{layer}") (net {netids[net]}) (tstamp {uid("trace"+str(i))}))')
for i, (a, b) in enumerate([((0, 0), (WIDTH, 0)), ((WIDTH, 0), (WIDTH, HEIGHT)),
                              ((WIDTH, HEIGHT), (0, HEIGHT)), ((0, HEIGHT), (0, 0))]):
    board.append(f'  (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width 0.05) (type default)) (layer "Edge.Cuts") (tstamp {uid("edge"+str(i))}))')
for ref, _, x, nets in headers:
    for i, net in enumerate(nets):
        label = "AD0=GND" if ref == "J3" and i == 4 else net
        board.append(f'  (gr_text "{label}" (at {x + 1.4} {rows[i]:.2f}) (layer "F.SilkS") (tstamp {uid(ref+"silk"+str(i))}) (effects (font (size 0.8 0.8) (thickness 0.12)) (justify left)))')
write(f"{NAME}.kicad_pcb", "\n".join(board) + "\n)\n")

sheet_id = uid("sheet")
sch = ['(kicad_sch (version 20211123) (generator wristband_script)',
       f'  (uuid {sheet_id})', '  (paper "A4")',
       '  (title_block (title "Experimental wristband wire carrier") (rev "UNVERIFIED"))',
       '  (lib_symbols']
for n in (4, 5):
    symbol = f"WireHeader_1x{n:02d}"
    half = (n-1)*1.27
    sch += [f'    (symbol "Wristband:{symbol}"',
            '      (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
            '      (property "Reference" "J" (id 0) (at 0 8.89 0) (effects (font (size 1.27 1.27))))',
            f'      (property "Value" "{symbol}" (id 1) (at 0 -8.89 0) (effects (font (size 1.27 1.27))))',
            f'      (property "Footprint" "Wristband:{fp_name(n)}" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
            '      (property "Datasheet" "" (id 3) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
            f'      (symbol "{symbol}_0_1" (rectangle (start -2.54 {half+1.27:.2f}) (end 2.54 {-half-1.27:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))',
            f'      (symbol "{symbol}_1_1"']
    for i in range(n):
        y = half - 2.54*i
        sch.append(f'        (pin passive line (at -5.08 {y:.2f} 0) (length 2.54) (name "Pin_{i+1}" (effects (font (size 1.27 1.27)))) (number "{i+1}" (effects (font (size 1.27 1.27)))))')
    sch += ['      )', '    )']
sch.append('  )')
for j, (ref, value, _, nets) in enumerate(headers):
    n = len(nets)
    x = 63.5 + j*60.96
    y = 80.01 if n == 4 else 81.28
    half = (n-1)*1.27
    for i, net in enumerate(nets):
        py = y - half + i*2.54
        sch += [f'  (wire (pts (xy {x-15.24} {py:.2f}) (xy {x-5.08} {py:.2f})) (stroke (width 0) (type default)) (uuid {uid(ref+"wire"+str(i))}))',
                f'  (label "{net}" (at {x-15.24} {py:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid(ref+"label"+str(i))}))']
    symbol = f"WireHeader_1x{n:02d}"
    sch += [f'  (symbol (lib_id "Wristband:{symbol}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {uid(ref+"sch")})',
            f'    (property "Reference" "{ref}" (id 0) (at {x} 68.58 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "{value}" (id 1) (at {x} 93.98 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Footprint" "Wristband:{fp_name(n)}" (id 2) (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (property "Datasheet" "" (id 3) (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))']
    for i in range(n):
        sch.append(f'    (pin "{i+1}" (uuid {uid(ref+"pin"+str(i+1))}))')
    sch += [f'    (instances (project "{NAME}" (path "/{sheet_id}" (reference "{ref}") (unit 1))))', '  )']
sch += ['  (sheet_instances (path "/" (page "1")))', ')']
write(f"{NAME}.kicad_sch", "\n".join(sch) + "\n")

# The schematic embeds the connector symbols; provide a matching editable library too.
first = sch.index('  (lib_symbols') + 1
last = sch.index('  )', first)
lib_symbols = '\n'.join(sch[first:last]).replace('(symbol "Wristband:', '(symbol "')
write("Wristband.kicad_sym", '(kicad_symbol_lib (version 20211014) (generator wristband_script)\n' + lib_symbols + '\n)\n')
write("sym-lib-table", '(sym_lib_table\n  (lib (name "Wristband")(type "KiCad")(uri "${KIPRJMOD}/Wristband.kicad_sym")(options "")(descr "Generic wire headers"))\n)\n')
