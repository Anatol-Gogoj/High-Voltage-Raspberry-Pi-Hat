# StudyBoard.py - build the HAT+ outline placement-study board from the rev A board.
#
# Usage (KiCad 10 python, from this directory):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" StudyBoard.py "../../HV Pi Hat.kicad_pcb"
#
# Steps:
#   1. Copy the rev A board text, dropping tracks, vias, zones, the Edge.Cuts outline and J3/J4.
#   2. Load it next to hatplus.kicad_pro / hatplus.kicad_dru (netclasses and rules resolve).
#   3. Draw the 65 x 56.5 mm HAT+ outline with 3 mm corners (HAT+ spec / legacy drawing).
#   4. Place every footprint from Layout.py; add J3/J4 as soldered-lead pads (ADR-0003).
#   5. Draw the pot outline on User.1 (HV copper + 3 mm, notched around H4) and void In1/In2 under it.
import importlib
import math
import os
import re
import sys
import pcbnew

Here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, Here)
import Layout
importlib.reload(Layout)

SourcePath = sys.argv[1]
OutPath = os.path.join(Here, "hatplus.kicad_pcb")
Mm = pcbnew.ToMM


def FromMm(V):
    return pcbnew.FromMM(float(V))


def Pt(X, Y):
    return pcbnew.VECTOR2I(FromMm(X), FromMm(Y))


# 1. Strip top-level blocks we rebuild
Text = open(SourcePath, encoding="utf-8", newline="").read()
Nl = "\r\n" if "\r\n" in Text else "\n"
Lines = Text.split(Nl)
Out, Index = [], 0
DropKinds = ("segment", "via", "arc", "zone")
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
    Drop = Kind in DropKinds
    if Kind.startswith("gr_") and '(layer "Edge.Cuts")' in Joined:
        Drop = True
    if Kind == "footprint" and re.search(r'\(property "Reference" "(J3|J4)"', Joined):
        Drop = True
    if not Drop:
        Out.extend(Block)
    Index = End + 1
open(OutPath, "w", encoding="utf-8", newline="").write(Nl.join(Out))

# 2. Load in the study project context
Board = pcbnew.LoadBoard(OutPath)

# 3. Outline: x 117.5..182.5, y 86.0..142.5, 3 mm corner radius
X0, Y0, X1, Y1, Rc = Layout.Outline
Edge = Board.GetLayerID("Edge.Cuts")


def AddShape(Shape):
    Shape.SetLayer(Edge)
    Shape.SetWidth(FromMm(0.05))
    Board.Add(Shape)


for (Ax, Ay, Bx, By) in [(X0 + Rc, Y0, X1 - Rc, Y0), (X1, Y0 + Rc, X1, Y1 - Rc), (X1 - Rc, Y1, X0 + Rc, Y1), (X0, Y1 - Rc, X0, Y0 + Rc)]:
    S = pcbnew.PCB_SHAPE(Board, pcbnew.SHAPE_T_SEGMENT)
    S.SetStart(Pt(Ax, Ay))
    S.SetEnd(Pt(Bx, By))
    AddShape(S)
K = Rc * (1 - 1 / math.sqrt(2))
for (Sx, Sy, Mx, My, Ex, Ey) in [(X0, Y0 + Rc, X0 + K, Y0 + K, X0 + Rc, Y0), (X1 - Rc, Y0, X1 - K, Y0 + K, X1, Y0 + Rc),
                                 (X1, Y1 - Rc, X1 - K, Y1 - K, X1 - Rc, Y1), (X0 + Rc, Y1, X0 + K, Y1 - K, X0, Y1 - Rc)]:
    S = pcbnew.PCB_SHAPE(Board, pcbnew.SHAPE_T_ARC)
    S.SetArcGeometry(Pt(Sx, Sy), Pt(Mx, My), Pt(Ex, Ey))
    AddShape(S)

# 4a. Soldered-lead pads replacing the J3/J4 screw terminals
def LeadPads(Ref, Value, Pads):
    Fp = pcbnew.FOOTPRINT(Board)
    Fp.SetReference(Ref)
    Fp.SetValue(Value)
    Fp.SetFPID(pcbnew.LIB_ID("HV_Pi_Hat", "HV_SolderedLeads_2"))
    Fp.SetPosition(Pt(*Pads[0][2]))
    for Number, NetName, (Px, Py) in Pads:
        Pad = pcbnew.PAD(Fp)
        Pad.SetNumber(Number)
        Pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        Pad.SetLayerSet(Pad.PTHMask())
        Pad.SetShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_CIRCLE)
        Pad.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(FromMm(Layout.LeadPad), FromMm(Layout.LeadPad)))
        Pad.SetDrillSize(pcbnew.VECTOR2I(FromMm(Layout.LeadDrill), FromMm(Layout.LeadDrill)))
        Pad.SetPosition(Pt(Px, Py))
        Pad.SetNet(Board.FindNet(NetName))
        Fp.Add(Pad)
        Cy = pcbnew.PCB_SHAPE(Fp, pcbnew.SHAPE_T_CIRCLE)
        Cy.SetLayer(pcbnew.F_CrtYd)
        Cy.SetCenter(Pt(Px, Py))
        Cy.SetEnd(Pt(Px + Layout.LeadPad / 2 + 0.25, Py))
        Cy.SetWidth(FromMm(0.05))
        Fp.Add(Cy)
    Board.Add(Fp)


for Ref, Value, Pads in Layout.Leads:
    LeadPads(Ref, Value, Pads)

# 4b. Place every other footprint
Missing = []
for Fp in Board.GetFootprints():
    Ref = Fp.GetReference()
    if Ref in Layout.LeadRefs:
        continue
    if Ref not in Layout.Place:
        Missing.append(Ref)
        continue
    X, Y, Rot = Layout.Place[Ref]
    Fp.SetPosition(Pt(X, Y))
    Fp.SetOrientationDegrees(Rot)
if Missing:
    sys.exit("no placement for: " + ", ".join(sorted(Missing)))

# 5. Pot outline from HV copper + margin, notched around H4; void In1/In2 under it
HvBoxes = []
for Fp in Board.GetFootprints():
    for Pad in Fp.Pads():
        if Pad.GetNetname() and any(N.strip().startswith("HV_") for N in Pad.GetNetClassName().split(",")):
            P = Pad.GetPosition()
            R = max(Mm(Pad.GetSize(pcbnew.F_Cu).x), Mm(Pad.GetSize(pcbnew.F_Cu).y)) / 2
            HvBoxes.append((Mm(P.x) - R, Mm(P.y) - R, Mm(P.x) + R, Mm(P.y) + R))
Margin = Layout.PotMargin
PxMin = min(B[0] for B in HvBoxes) - Margin
PyMin = min(B[1] for B in HvBoxes) - Margin
PxMax, PyMax = X1, Y1
Hx, Hy, Hr = Layout.H4Notch
# Keyhole notch: from the right edge, around the upper-left quarter of the H4 screw circle, down to the
# bottom edge. Only the screw and its dam are excluded, not the whole corner square.
Arc = [(Hx + Hr * math.cos(math.radians(A)), Hy - Hr * math.sin(math.radians(A))) for A in range(90, 181, 15)]
Poly = [(PxMin, PyMin), (PxMax, PyMin), (PxMax, Hy - Hr), *Arc, (Hx - Hr, PyMax), (PxMin, PyMax)]
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
    Outline = Z.Outline()
    Outline.NewOutline()
    for (Ax, Ay) in Poly:
        Outline.Append(FromMm(Ax), FromMm(Ay))
    Board.Add(Z)

Board.Save(OutPath)
print("pot outline:", ", ".join("(%.1f, %.1f)" % P for P in Poly))
print("saved", OutPath)
