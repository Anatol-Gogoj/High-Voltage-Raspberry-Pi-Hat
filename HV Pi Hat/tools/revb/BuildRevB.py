# BuildRevB.py - turn the rev A board into the rev B placement (HAT+ outline, potted HV zone).
#
# Usage (KiCad 10 python, from the project directory "HV Pi Hat/"):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" tools/revb/BuildRevB.py
#
# Rewrites "HV Pi Hat.kicad_pcb" in place (rev A stays in git history):
#   1. Drops tracks, vias, zones, the Edge.Cuts outline, rev A's User.Drawings notes and J3/J4.
#   2. Draws the 65 x 56.5 mm HAT+ outline with 3 mm corners.
#   3. Adds J3/J4 as HV_Footprints:HV_LeadPair_P6.00mm with their nets (ADR-0003 soldered leads).
#   4. Places every footprint from RevBLayout.py.
#   5. Draws the pot on User.1 (HV pads + 3 mm, keyhole notch around H4) and voids In1/In2 under it.
import importlib
import math
import os
import re
import sys
import pcbnew

Here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, Here)
import RevBLayout as Layout
importlib.reload(Layout)

BoardPath = os.path.abspath("HV Pi Hat.kicad_pcb")
LibPath = os.path.abspath("HV_Pi_Hat.pretty")
Mm = pcbnew.ToMM


def FromMm(V):
    return pcbnew.FromMM(float(V))


def Pt(X, Y):
    return pcbnew.VECTOR2I(FromMm(X), FromMm(Y))


# 1. Text-level strip (KiCad 10 SWIG removal is unreliable, see docs/TOOLING.md)
Text = open(BoardPath, encoding="utf-8", newline="").read()
Nl = "\r\n" if "\r\n" in Text else "\n"
Lines = Text.split(Nl)
Out, Index, Kept = [], 0, {}
while Index < len(Lines):
    Line = Lines[Index]
    M = re.match(r"^\t\((\w+)", Line)
    if not M:
        Out.append(Line)
        Index += 1
        continue
    End = Index
    if not Line.rstrip().endswith(")") or Line.count("(") != Line.count(")"):
        while Lines[End] != "\t)":
            End += 1
    Block = Lines[Index:End + 1]
    Joined = Nl.join(Block)
    Kind = M.group(1)
    Drop = Kind in ("segment", "via", "arc", "zone")
    if Kind.startswith("gr_") and ('(layer "Edge.Cuts")' in Joined or '(layer "User.Drawings")' in Joined or '(layer "User.1")' in Joined):
        Drop = True
    Ref = re.search(r'\(property "Reference" "([^"]+)"', Joined) if Kind == "footprint" else None
    if Ref and Ref.group(1) in ("J3", "J4"):
        Kept[Ref.group(1)] = {
            "value": re.search(r'\(property "Value" "([^"]*)"', Joined).group(1),
            "nets": dict(re.findall(r'\(pad "([^"]+)".*?\(net "([^"]*)"\)', Joined, re.S)),
        }
        Drop = True
    if not Drop:
        Out.extend(Block)
    Index = End + 1
open(BoardPath, "w", encoding="utf-8", newline="").write(Nl.join(Out))
if set(Kept) != {"J3", "J4"}:
    sys.exit("J3/J4 not found in the board")

# Footprint fields that schematic parity compares, read from the schematic so they stay in sync
Sch = open("HV Pi Hat.kicad_sch", encoding="utf-8").read()
SchDesc = {}
for Ref in ("J3", "J4"):
    I = Sch.index('(property "Reference" "%s"' % Ref)
    Block = Sch[Sch.rfind("(symbol", 0, I):Sch.index("(instances", I)]
    SchDesc[Ref] = re.search(r'\(property "Description" "([^"]*)"', Block).group(1)

Board = pcbnew.LoadBoard(BoardPath)

# 2. Outline
X0, Y0, X1, Y1, Rc = Layout.Outline
Edge = Board.GetLayerID("Edge.Cuts")


def AddEdge(Shape):
    Shape.SetLayer(Edge)
    Shape.SetWidth(FromMm(0.05))
    Board.Add(Shape)


for (Ax, Ay, Bx, By) in [(X0 + Rc, Y0, X1 - Rc, Y0), (X1, Y0 + Rc, X1, Y1 - Rc), (X1 - Rc, Y1, X0 + Rc, Y1), (X0, Y1 - Rc, X0, Y0 + Rc)]:
    S = pcbnew.PCB_SHAPE(Board, pcbnew.SHAPE_T_SEGMENT)
    S.SetStart(Pt(Ax, Ay))
    S.SetEnd(Pt(Bx, By))
    AddEdge(S)
K = Rc * (1 - 1 / math.sqrt(2))
for (Sx, Sy, Mx, My, Ex, Ey) in [(X0, Y0 + Rc, X0 + K, Y0 + K, X0 + Rc, Y0), (X1 - Rc, Y0, X1 - K, Y0 + K, X1, Y0 + Rc),
                                 (X1, Y1 - Rc, X1 - K, Y1 - K, X1 - Rc, Y1), (X0 + Rc, Y1, X0 + K, Y1 - K, X0, Y1 - Rc)]:
    S = pcbnew.PCB_SHAPE(Board, pcbnew.SHAPE_T_ARC)
    S.SetArcGeometry(Pt(Sx, Sy), Pt(Mx, My), Pt(Ex, Ey))
    AddEdge(S)

# 3. J3/J4 from the project library, same reference, value and pad nets as the schematic
for Ref in ("J3", "J4"):
    Fp = pcbnew.FootprintLoad(LibPath, "HV_LeadPair_P6.00mm")
    if Fp is None:
        sys.exit("HV_LeadPair_P6.00mm not found in " + LibPath)
    Fp.SetFPID(pcbnew.LIB_ID("HV_Footprints", "HV_LeadPair_P6.00mm"))
    Fp.SetField("Description", SchDesc[Ref])
    Fp.SetReference(Ref)
    Fp.SetValue("HV_LeadPair")
    for Pad in Fp.Pads():
        Pad.SetNet(Board.FindNet(Kept[Ref]["nets"][Pad.GetNumber()]))
    Board.Add(Fp)

# 4. Placement
Missing = []
for Fp in Board.GetFootprints():
    Ref = Fp.GetReference()
    if Ref not in Layout.Place:
        Missing.append(Ref)
        continue
    X, Y, Rot = Layout.Place[Ref]
    Fp.SetPosition(Pt(X, Y))
    Fp.SetOrientationDegrees(Rot)
if Missing:
    sys.exit("no placement for: " + ", ".join(sorted(Missing)))

# 5. Pot outline and inner-layer voids
HvPads = []
for Fp in Board.GetFootprints():
    for Pad in Fp.Pads():
        if Pad.GetNetname() and any(N.strip().startswith("HV_") for N in Pad.GetNetClassName().split(",")):
            P = Pad.GetPosition()
            R = Mm(max(Pad.GetSize(pcbnew.F_Cu).x, Pad.GetSize(pcbnew.F_Cu).y)) / 2
            HvPads.append((Mm(P.x), Mm(P.y), R))
PxMin = min(X - R for X, Y, R in HvPads) - Layout.PotMargin
PyMin = min(Y - R for X, Y, R in HvPads) - Layout.PotMargin
Hx, Hy, Hr = Layout.H4Notch
Arc = [(Hx + Hr * math.cos(math.radians(A)), Hy - Hr * math.sin(math.radians(A))) for A in range(90, 181, 15)]
Poly = [(PxMin, PyMin), (X1, PyMin), (X1, Hy - Hr), *Arc, (Hx - Hr, Y1), (PxMin, Y1)]
User1 = Board.GetLayerID("User.1")
for (Ax, Ay), (Bx, By) in zip(Poly, Poly[1:] + Poly[:1]):
    S = pcbnew.PCB_SHAPE(Board, pcbnew.SHAPE_T_SEGMENT)
    S.SetStart(Pt(Ax, Ay))
    S.SetEnd(Pt(Bx, By))
    S.SetLayer(User1)
    S.SetWidth(FromMm(0.2))
    Board.Add(S)
for LayerName in ("In1.Cu", "In2.Cu"):
    Z = pcbnew.ZONE(Board)
    Z.SetIsRuleArea(True)
    Z.SetDoNotAllowTracks(True)
    Z.SetDoNotAllowVias(True)
    Z.SetDoNotAllowZoneFills(True)
    Z.SetDoNotAllowPads(False)
    Z.SetDoNotAllowFootprints(False)
    Z.SetLayer(Board.GetLayerID(LayerName))
    Z.SetZoneName("PotVoid_" + LayerName)
    Ol = Z.Outline()
    Ol.NewOutline()
    for (Ax, Ay) in Poly:
        Ol.Append(FromMm(Ax), FromMm(Ay))
    Board.Add(Z)

Board.Save(BoardPath)
print("pot outline:", ", ".join("(%.1f, %.1f)" % P for P in Poly))
print("saved", BoardPath)
