# TidyIdEeprom.py - redraw the ID EEPROM block that AddIdEeprom.py placed on the bottom frame line.
# Moves U3, R27-R29, TP1, C6, #FLG3 and their power symbols and labels into the empty area under the
# op-amp (x 20-80 mm, y 140-182 mm), ties A0-A2 to one GND with wires, gives the pull-up and test point
# labels a short wire stub, and moves PWR_FLAG off the +3V3 symbol it overlapped.
# Connectivity is unchanged: every label, power symbol and wire end still lands on the same pin.
# Symbol UUIDs are kept, so the PCB links are untouched. Check with a netlist diff and ERC afterwards.
# ONE-SHOT: already applied to the rev B schematic; running it again finds nothing at the old positions.
# Usage: python tools/revb/TidyIdEeprom.py "HV Pi Hat.kicad_sch"
import re
import sys
import uuid

Path = sys.argv[1]
Text = open(Path, encoding="utf-8", newline="").read()
Nl = "\r\n" if "\r\n" in Text else "\n"

# Old position -> new placement. Symbols: (lib_id, old x, old y) -> (new x, new y, rot, {prop: (x, y)}).
# Props not listed (hidden ones) move to the symbol origin.
Ux, Uy = 55.88, 152.4
Cx, Cy = 30.48, 152.4
Ry = 175.26
Moves = {
    ("Memory_EEPROM:24LC16", 100.33, 190.5): (Ux, Uy, 0, {"Reference": (Ux + 5.08, Uy + 8.89), "Value": (Ux + 5.08, Uy + 11.43)}),
    ("power:+3V3", 100.33, 182.88): (Ux, Uy - 7.62, 0, {"Value": (Ux, Uy - 7.62 - 3.556)}),
    ("power:GND", 100.33, 198.12): (Ux, Uy + 7.62, 0, {"Value": (Ux, Uy + 7.62 + 3.81)}),
    ("power:GND", 90.17, 193.04): (Ux - 10.16, Uy + 7.62, 0, {"Value": (Ux - 10.16, Uy + 7.62 + 3.81)}),
    ("power:GND", 90.17, 187.96): None,   # A0 and A1 now reach GND through the A-pin wire
    ("power:GND", 90.17, 190.5): None,
    ("Device:C", 80.01, 190.5): (Cx, Cy, 0, {"Reference": (Cx + 2.54, Cy - 1.27), "Value": (Cx + 2.54, Cy + 1.27)}),
    ("power:+3V3", 80.01, 186.69): (Cx, Cy - 3.81, 0, {"Value": (Cx, Cy - 3.81 - 3.556)}),
    ("power:GND", 80.01, 194.31): (Cx, Cy + 3.81, 0, {"Value": (Cx, Cy + 3.81 + 3.81)}),
    ("power:PWR_FLAG", 80.01, 186.69): (Cx - 10.16, Cy - 3.81, 0, {"Value": (Cx - 10.16, Cy - 3.81 - 3.81)}),
    ("Connector:TestPoint", 142.24, 193.04): (71.12, Ry + 2.54, 0, {"Reference": (73.66, Ry - 1.27), "Value": (73.66, Ry + 1.27)}),
}
Labels = {
    ("ID_SD", 110.49, 187.96): (Ux + 10.16, Uy - 2.54),
    ("ID_SC", 110.49, 190.5): (Ux + 10.16, Uy),
    ("ID_WP", 110.49, 193.04): (Ux + 10.16, Uy + 2.54),
    ("ID_WP", 142.24, 193.04): (71.12, Ry + 5.08),
}
Wires = [
    ((Ux - 10.16, Uy - 2.54), (Ux - 10.16, Uy)),          # A0 - A1
    ((Ux - 10.16, Uy), (Ux - 10.16, Uy + 2.54)),          # A1 - A2
    ((Ux - 10.16, Uy + 2.54), (Ux - 10.16, Uy + 7.62)),   # A2 - GND
    ((Cx - 10.16, Cy - 3.81), (Cx, Cy - 3.81)),           # PWR_FLAG - C6 pin 1
    ((71.12, Ry + 2.54), (71.12, Ry + 5.08)),             # TP1 - ID_WP label
]
Junctions = [(Ux - 10.16, Uy), (Ux - 10.16, Uy + 2.54)]
for OldX, NewX, Net in ((121.92, 40.64, "ID_SD"), (128.27, 50.8, "ID_SC"), (134.62, 60.96, "ID_WP")):
    Moves[("Device:R_Small_US", OldX, 190.5)] = (NewX, Ry, 0, {"Reference": (NewX + 2.54, Ry - 1.27), "Value": (NewX + 2.54, Ry + 1.27)})
    Moves[("power:+3V3", OldX, 187.96)] = (NewX, Ry - 2.54, 0, {"Value": (NewX, Ry - 2.54 - 3.556)})
    Labels[(Net, OldX, 193.04)] = (NewX, Ry + 5.08)
    Wires.append(((NewX, Ry + 2.54), (NewX, Ry + 5.08)))


def F(V):
    return ("%.4f" % V).rstrip("0").rstrip(".")


def Key(X, Y):
    return (round(X, 3), round(Y, 3))


Moves = {(L, *Key(X, Y)): V for (L, X, Y), V in Moves.items()}
Labels = {(N, *Key(X, Y)): V for (N, X, Y), V in Labels.items()}
Used = set()


def EditSymbol(Item):
    Lib = re.search(r'\(lib_id "([^"]+)"\)', Item).group(1)
    At = re.search(r"\n\t\t\(at ([\d.-]+) ([\d.-]+) (\d+)\)", Item)
    K = (Lib, *Key(float(At.group(1)), float(At.group(2))))
    if K not in Moves:
        return Item
    Used.add(K)
    if Moves[K] is None:
        return ""
    X, Y, Rot, Props = Moves[K]
    Item = Item[:At.start()] + "\n\t\t(at %s %s %d)" % (F(X), F(Y), Rot) + Item[At.end():]

    def Prop(M):
        Px, Py = Props.get(M.group(2), (X, Y))
        return M.group(1) + "(at %s %s 0)" % (F(Px), F(Py))
    return re.sub(r'(\(property "([^"]+)" "[^"]*"\s*\n\t\t\t)\(at [\d.-]+ [\d.-]+ \d+\)', Prop, Item)


def EditLabel(Item):
    M = re.match(r'\t\(label "([^"]+)"\s*\n\t\t\(at ([\d.-]+) ([\d.-]+) 0\)', Item)
    if not M:
        return Item
    K = (M.group(1), *Key(float(M.group(2)), float(M.group(3))))
    if K not in Labels:
        return Item
    Used.add(K)
    X, Y = Labels[K]
    return Item[:M.start(2)] + "%s %s" % (F(X), F(Y)) + Item[M.end(3):]


# Top-level items are tab-indented once and close on the first line that is a single tab and ")".
Pattern = re.compile(r"(?m)^\t\((symbol|label)\b.*?^\t\)" + re.escape(Nl), re.S)
LibEnd = Text.index(Nl + "\t)", Text.index("\t(lib_symbols"))
Head, Body = Text[:LibEnd], Text[LibEnd:]
Body = Pattern.sub(lambda M: EditSymbol(M.group(0)) if M.group(1) == "symbol" else EditLabel(M.group(0)), Body)
Missing = (set(Moves) | set(Labels)) - Used
if Missing:
    sys.exit("not found at the old positions: %s" % sorted(Missing))

Add = []
for (X1, Y1), (X2, Y2) in Wires:
    Add += ["\t(wire", "\t\t(pts", "\t\t\t(xy %s %s) (xy %s %s)" % (F(X1), F(Y1), F(X2), F(Y2)), "\t\t)", "\t\t(stroke",
            "\t\t\t(width 0)", "\t\t\t(type default)", "\t\t)", '\t\t(uuid "%s")' % uuid.uuid4(), "\t)"]
for X, Y in Junctions:
    Add += ["\t(junction", "\t\t(at %s %s)" % (F(X), F(Y)), "\t\t(diameter 0)", "\t\t(color 0 0 0 0)",
            '\t\t(uuid "%s")' % uuid.uuid4(), "\t)"]
Anchor = Nl + "\t(sheet_instances"
I = Body.index(Anchor) + len(Nl) if Anchor in Body else Body.rstrip().rindex(")")
Body = Body[:I] + Nl.join(Add) + Nl + Body[I:]
open(Path, "w", encoding="utf-8", newline="").write(Head + Body)
print("moved %d items, added %d wires and %d junctions" % (len(Used), len(Wires), len(Junctions)))
