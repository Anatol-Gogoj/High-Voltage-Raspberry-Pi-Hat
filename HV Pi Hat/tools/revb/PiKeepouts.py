# PiKeepouts.py - Raspberry Pi 5 top-side parts under the HAT: draw them on User.2 and report the
# vertical room left between each part and the HAT's underside (THT leads, bottom pot).
#
# Usage (KiCad 10 python, from the project directory):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" tools/revb/PiKeepouts.py "HV Pi Hat.kicad_pcb" [--draw]
#
# Coordinates: Pi parts are hole-referenced (see RevBLayout.Pi5Parts): Xh/Yh from the centre of the
# hole nearest GPIO pin 1 (board H2 at 121.0, 89.5), +X toward USB/Ethernet, +Y away from the header.
import math
import os
import sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import RevBLayout as Layout

BoardPath = sys.argv[1]
Draw = "--draw" in sys.argv
Mm = pcbnew.ToMM


def FromMm(V):
    return pcbnew.FromMM(float(V))


def ToBoard(Xh, Yh):
    return 121.0 + Xh, 89.5 + Yh


Board = pcbnew.LoadBoard(BoardPath)
X0, Y0, X1, Y1, Rc = Layout.Outline

# Pot polygon (bottom pot covers the same area as the top one, ADR-0003)
Pot = None
for Z in Board.Zones():
    if Z.GetIsRuleArea() and Z.GetZoneName() == "PotVoid_In1.Cu":
        Ol = Z.Outline().Outline(0)
        Pot = [(Mm(Ol.CPoint(I).x), Mm(Ol.CPoint(I).y)) for I in range(Ol.PointCount())]


def RectInPoly(Poly, Xa, Ya, Xb, Yb):
    # True if any sample of the rectangle lies inside the polygon (even-odd)
    def Inside(Px, Py):
        In = False
        for K in range(len(Poly)):
            (Ax, Ay), (Bx, By) = Poly[K], Poly[(K + 1) % len(Poly)]
            if (Ay > Py) != (By > Py) and Px < Ax + (Py - Ay) * (Bx - Ax) / (By - Ay):
                In = not In
        return In
    Steps = 20
    return any(Inside(Xa + (Xb - Xa) * I / Steps, Ya + (Yb - Ya) * J / Steps) for I in range(Steps + 1) for J in range(Steps + 1))


Standoff = float(sys.argv[sys.argv.index("--standoff") + 1]) if "--standoff" in sys.argv else Layout.Standoff
Rows = []
for Name, (Px0, Py0, Px1, Py1), Height, Source in Layout.Pi5Parts:
    Bx0, By1 = ToBoard(Px0, Py0)
    Bx1, By0 = ToBoard(Px1, Py1)
    Xa, Xb = sorted((Bx0, Bx1))
    Ya, Yb = sorted((By0, By1))
    Under = Xa < X1 and Xb > X0 and Ya < Y1 and Yb > Y0
    InPot = Under and Pot is not None and RectInPoly(Pot, max(Xa, X0), max(Ya, Y0), min(Xb, X1), min(Yb, Y1))
    # The pot is measured from the board surface and covers the trimmed leads
    Below = max(Layout.ThtProtrusion, Layout.BottomPot) if InPot else Layout.ThtProtrusion
    Room = None if (Height is None or not Under) else Standoff - Height - Below
    Rows.append((Name, Xa, Ya, Xb, Yb, Under, InPot, Height, Room, Source))
    if Draw and Under:
        L = Board.GetLayerID("User.2")
        Pts = [(Xa, Ya), (Xb, Ya), (Xb, Yb), (Xa, Yb)]
        for (Ax, Ay), (Cx, Cy) in zip(Pts, Pts[1:] + Pts[:1]):
            S = pcbnew.PCB_SHAPE(Board, pcbnew.SHAPE_T_SEGMENT)
            S.SetStart(pcbnew.VECTOR2I(FromMm(Ax), FromMm(Ay)))
            S.SetEnd(pcbnew.VECTOR2I(FromMm(Cx), FromMm(Cy)))
            S.SetLayer(L)
            S.SetWidth(FromMm(0.1))
            Board.Add(S)
        T = pcbnew.PCB_TEXT(Board)
        T.SetText("Pi5 %s %s" % (Name, "h ?" if Height is None else "h %.1f" % Height))
        T.SetPosition(pcbnew.VECTOR2I(FromMm((Xa + Xb) / 2), FromMm((Ya + Yb) / 2)))
        T.SetLayer(L)
        T.SetTextSize(pcbnew.VECTOR2I(FromMm(0.8), FromMm(0.8)))
        Board.Add(T)

print("standoff %.1f mm, THT protrusion %.1f mm, bottom pot %.1f mm" % (Standoff, Layout.ThtProtrusion, Layout.BottomPot))
print("%-22s %-28s %-6s %-6s %-7s %s" % ("part", "board x / y (mm)", "under", "in pot", "height", "room left"))
for Name, Xa, Ya, Xb, Yb, Under, InPot, Height, Room, Source in Rows:
    print("%-22s x %6.1f..%6.1f y %6.1f..%6.1f  %-6s %-6s %-7s %s" % (
        Name, Xa, Xb, Ya, Yb, "yes" if Under else "no", "yes" if InPot else "no",
        "?" if Height is None else "%.1f" % Height,
        "outside outline" if not Under else ("?" if Room is None else "%.1f mm%s" % (Room, "  CONFLICT" if Room < 0.5 else ""))))
if Draw:
    Board.Save(BoardPath)
    print("drawn on User.2 and saved")
