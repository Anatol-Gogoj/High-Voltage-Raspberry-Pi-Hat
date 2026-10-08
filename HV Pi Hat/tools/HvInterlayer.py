# HvInterlayer.py - smallest 3-D distance between HV copper and non-HV copper on a different
# copper layer, with the average field at a given voltage. The 2-D DRC only checks same-layer
# spacing; this covers the through-board direction (see docs/adr/0002-hv-on-outer-layers.md).
#
# Usage (KiCad 10 python, run from the project directory so netclasses resolve):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" tools/HvInterlayer.py "HV Pi Hat.kicad_pcb" [kV] [rows]
#
# Shapes are conservative: pads are their circumscribed circle, tracks are capsules, vias are
# circles on every layer. Layer z positions come from the board file's (stackup ...) block.
import math
import re
import sys
import pcbnew

BoardPath = sys.argv[1]
Kv = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
Rows = int(sys.argv[3]) if len(sys.argv) > 3 else 10
CopperNames = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]


def ReadStackup(Path):
    # Returns [(name, type, thickness_mm), ...] in stackup order
    Text = open(Path, encoding="utf-8").read()
    Start = Text.index("(stackup")
    Block = Text[Start:Text.index("(copper_finish", Start)]
    Layers = []
    for M in re.finditer(r'\(layer "([^"]+)"\s*\(type "([^"]+)"\)(?:\s*\(thickness ([0-9.]+)\))?', Block):
        Layers.append((M.group(1), M.group(2), float(M.group(3) or 0.0)))
    return Layers


def LayerZ(Stackup):
    # z of the top surface and the thickness of each copper layer, F.Cu top at z = 0
    Z, Thick, Cursor, Started = {}, {}, 0.0, False
    for Name, Type, T in Stackup:
        if Name == "F.Cu":
            Started = True
        if not Started:
            continue
        if Type == "copper":
            Z[Name] = Cursor
            Thick[Name] = T
        Cursor += T
        if Name == "B.Cu":
            break
    return Z, Thick


Z, Thick = LayerZ(ReadStackup(BoardPath))
Board = pcbnew.LoadBoard(BoardPath)
Mm = pcbnew.ToMM


def Vertical(A, B):
    if A == B:
        return 0.0
    Top, Bot = (A, B) if Z[A] < Z[B] else (B, A)
    return Z[Bot] - (Z[Top] + Thick[Top])


def IsHv(Item):
    return any(N.strip().startswith("HV_") for N in Item.GetNetClassName().split(","))


Items = []  # (is_hv, layer, kind, geometry, label)
for Fp in Board.GetFootprints():
    for Pad in Fp.Pads():
        if not Pad.GetNetname():
            continue
        Size = Pad.GetSize(pcbnew.F_Cu)
        Radius = math.hypot(Mm(Size.x), Mm(Size.y)) / 2
        P = Pad.GetPosition()
        for L in CopperNames:
            if Pad.IsOnLayer(Board.GetLayerID(L)):
                Items.append((IsHv(Pad), L, "c", (Mm(P.x), Mm(P.y), Radius),
                              "%s.%s %s" % (Fp.GetReference(), Pad.GetNumber(), Pad.GetNetname())))
for T in Board.GetTracks():
    if T.GetClass() == "PCB_VIA":
        P = T.GetPosition()
        for L in CopperNames:
            Items.append((IsHv(T), L, "c", (Mm(P.x), Mm(P.y), Mm(T.GetWidth(pcbnew.F_Cu)) / 2), "via " + T.GetNetname()))
    else:
        Items.append((IsHv(T), T.GetLayerName(), "s",
                      (Mm(T.GetStart().x), Mm(T.GetStart().y), Mm(T.GetEnd().x), Mm(T.GetEnd().y), Mm(T.GetWidth()) / 2),
                      "track " + T.GetNetname()))


def PointSegment(Px, Py, Ax, Ay, Bx, By):
    Dx, Dy = Bx - Ax, By - Ay
    L2 = Dx * Dx + Dy * Dy
    T = 0.0 if L2 == 0 else max(0.0, min(1.0, ((Px - Ax) * Dx + (Py - Ay) * Dy) / L2))
    return math.hypot(Px - Ax - T * Dx, Py - Ay - T * Dy)


def Lateral(I, J):
    Gi, Gj = I[3], J[3]
    if I[2] == "c" and J[2] == "c":
        return math.hypot(Gi[0] - Gj[0], Gi[1] - Gj[1]) - Gi[2] - Gj[2]
    if I[2] == "c":
        return PointSegment(Gi[0], Gi[1], *Gj[:4]) - Gi[2] - Gj[4]
    if J[2] == "c":
        return PointSegment(Gj[0], Gj[1], *Gi[:4]) - Gj[2] - Gi[4]
    Core = min(PointSegment(Gi[0], Gi[1], *Gj[:4]), PointSegment(Gi[2], Gi[3], *Gj[:4]),
               PointSegment(Gj[0], Gj[1], *Gi[:4]), PointSegment(Gj[2], Gj[3], *Gi[:4]))
    return Core - Gi[4] - Gj[4]


Results = []
for H in (I for I in Items if I[0]):
    for L in (I for I in Items if not I[0]):
        if H[1] == L[1]:
            continue
        Lat = max(0.0, Lateral(H, L))
        Results.append((math.hypot(Lat, Vertical(H[1], L[1])), Lat, H[1], H[4], L[1], L[4]))
Results.sort()

print("stackup z (mm):", ", ".join("%s %.3f" % (N, Z[N]) for N in CopperNames))
Seen = set()
for D, Lat, Hl, Hn, Ll, Ln in Results:
    if (Hn, Ln) in Seen:
        continue
    Seen.add((Hn, Ln))
    print("%.3f mm (lateral %.3f)  %s %s  <->  %s %s  -> %.2f kV/mm at %.1f kV" % (D, Lat, Hl, Hn, Ll, Ln, Kv / D, Kv))
    if len(Seen) >= Rows:
        break
