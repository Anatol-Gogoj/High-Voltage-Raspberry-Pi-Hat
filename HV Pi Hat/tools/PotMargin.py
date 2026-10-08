# PotMargin.py - smallest distance from HV copper (pads and tracks) to the edge of the pot.
# ADR-0003 interim rule: every piece of HV copper sits at least 3 mm inside the pot edge.
#
# Usage (KiCad 10 python, from the board's project directory):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" tools/PotMargin.py <board.kicad_pcb> [RuleAreaName] [rows]
# The pot outline is read from the In1 rule area that voids the inner layers under the pot
# (default name "PotVoid_In1.Cu", as drawn by studies/hatplus/StudyBoard.py).
import math
import sys
import pcbnew

BoardPath = sys.argv[1]
AreaName = sys.argv[2] if len(sys.argv) > 2 else "PotVoid_In1.Cu"
Rows = int(sys.argv[3]) if len(sys.argv) > 3 else 5
Board = pcbnew.LoadBoard(BoardPath)
Mm = pcbnew.ToMM

Poly = None
for Z in Board.Zones():
    if Z.GetIsRuleArea() and Z.GetZoneName() == AreaName:
        Ol = Z.Outline().Outline(0)
        Poly = [(Mm(Ol.CPoint(I).x), Mm(Ol.CPoint(I).y)) for I in range(Ol.PointCount())]
if Poly is None:
    sys.exit("rule area %s not found" % AreaName)


def SegmentDistance(Px, Py, Ax, Ay, Bx, By):
    Dx, Dy = Bx - Ax, By - Ay
    L2 = Dx * Dx + Dy * Dy
    T = 0.0 if L2 == 0 else max(0.0, min(1.0, ((Px - Ax) * Dx + (Py - Ay) * Dy) / L2))
    return math.hypot(Px - Ax - T * Dx, Py - Ay - T * Dy)


def ToBoundary(Px, Py):
    return min(SegmentDistance(Px, Py, *Poly[K], *Poly[(K + 1) % len(Poly)]) for K in range(len(Poly)))


def IsHv(Item):
    return bool(Item.GetNetname()) and any(N.strip().startswith("HV_") for N in Item.GetNetClassName().split(","))


Results = []
for Fp in Board.GetFootprints():
    for Pad in Fp.Pads():
        if not IsHv(Pad):
            continue
        S = Pad.GetSize(pcbnew.F_Cu)
        if Pad.GetShape(pcbnew.F_Cu) == pcbnew.PAD_SHAPE_CIRCLE:
            Radius = Mm(max(S.x, S.y)) / 2
        else:
            Radius = math.hypot(Mm(S.x), Mm(S.y)) / 2   # conservative for non-round pads
        P = Pad.GetPosition()
        Results.append((ToBoundary(Mm(P.x), Mm(P.y)) - Radius, "%s.%s %s" % (Fp.GetReference(), Pad.GetNumber(), Pad.GetNetname())))
for T in Board.GetTracks():
    if not IsHv(T):
        continue
    if T.GetClass() == "PCB_VIA":
        P = T.GetPosition()
        Results.append((ToBoundary(Mm(P.x), Mm(P.y)) - Mm(T.GetWidth(pcbnew.F_Cu)) / 2, "via " + T.GetNetname()))
        continue
    Ax, Ay, Bx, By = Mm(T.GetStart().x), Mm(T.GetStart().y), Mm(T.GetEnd().x), Mm(T.GetEnd().y)
    Steps = max(2, int(math.hypot(Bx - Ax, By - Ay) / 0.1))
    Nearest = min(ToBoundary(Ax + (Bx - Ax) * K / Steps, Ay + (By - Ay) * K / Steps) for K in range(Steps + 1))
    Results.append((Nearest - Mm(T.GetWidth()) / 2, "track %s %s" % (T.GetNetname(), T.GetLayerName())))
Results.sort()
for D, Name in Results[:Rows]:
    print("%.2f mm  %s" % (D, Name))
