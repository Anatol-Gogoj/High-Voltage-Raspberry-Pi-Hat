# BuildRevB.py - build the rev B board (HAT outline, potted HV zone) and sync it with the schematic.
#
# Usage (KiCad 10 python, from the project directory "HV Pi Hat/"):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" tools/revb/BuildRevB.py
#
# Rewrites "HV Pi Hat.kicad_pcb" in place (it strips and rebuilds, so it runs on rev A or on rev B):
#   1. Exports the schematic netlist (kicad-cli) for components, footprints, fields and pad nets.
#   2. Drops tracks, vias, zones, the outline and user drawings, every footprint whose library ID no
#      longer matches the schematic, footprints no longer in the schematic, and H1..H4 if they are not
#      yet the HAT hole.
#   3. Draws the HAT outline (65 x 56.0 mm for a THT header, 3 mm corners).
#   4. Loads missing footprints from the libraries, sets reference/value/fields, and sets every pad's
#      net from the netlist. H1..H4 become HV_Footprints:MountingHole_2.75mm_M2.5_NPTH_HAT.
#   5. Places every footprint from RevBLayout.py (optional 4th field "B" = bottom side).
#   6. Pot outline on User.1 (HV pads + 3 mm, keyhole notch at H4), In1/In2 voids under it,
#      6.2 mm copper-free hole lands, and the PCIe notch strip.
import importlib
import math
import os
import re
import subprocess
import sys
import tempfile
import pcbnew

Here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, Here)
import RevBLayout as Layout
importlib.reload(Layout)

BoardPath = os.path.abspath("HV Pi Hat.kicad_pcb")
SchPath = os.path.abspath("HV Pi Hat.kicad_sch")
KiCadCli = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"
StdFootprints = "C:/Program Files/KiCad/10.0/share/kicad/footprints"
HoleFootprint = "HV_Footprints:MountingHole_2.75mm_M2.5_NPTH_HAT"
Holes = ("H1", "H2", "H3", "H4")
Mm = pcbnew.ToMM


def FromMm(V):
    return pcbnew.FromMM(float(V))


def Pt(X, Y):
    return pcbnew.VECTOR2I(FromMm(X), FromMm(Y))


# 1. Schematic netlist
NetFile = os.path.join(tempfile.gettempdir(), "revb_netlist.net")
subprocess.run([KiCadCli, "sch", "export", "netlist", "-o", NetFile, SchPath], check=True, capture_output=True)
Net = open(NetFile, encoding="utf-8").read()
Comps = {}
for Block in re.split(r"\n\t\t\(comp\n", Net[Net.index("(components"):Net.index("(libparts")])[1:]:
    def Field(Key):
        M = re.search(r'\(%s "((?:[^"\\]|\\.)*)"\)' % Key, Block)
        return M.group(1) if M else ""
    Comps[Field("ref")] = {"value": Field("value"), "footprint": Field("footprint"),
                           "datasheet": Field("datasheet"), "description": Field("description")}
PinNet = {}
for Block in re.split(r"\n\t\t\(net\n", Net[Net.index("(nets"):])[1:]:
    Name = re.search(r'\(name "([^"]*)"\)', Block).group(1)
    for Ref, Pin in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', Block):
        PinNet[(Ref, Pin)] = Name

# 2. Text-level strip (KiCad 10 SWIG removal is unreliable, see docs/TOOLING.md)
Text = open(BoardPath, encoding="utf-8", newline="").read()
Nl = "\r\n" if "\r\n" in Text else "\n"
Lines = Text.split(Nl)
Out, Index, OnBoard = [], 0, set()
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
    if Kind.startswith("gr_") and any('(layer "%s")' % L in Joined for L in ("Edge.Cuts", "User.Drawings", "User.1", "User.2")):
        Drop = True
    if Kind == "footprint":
        Ref = re.search(r'\(property "Reference" "([^"]+)"', Joined).group(1)
        FpId = re.match(r'^\t\(footprint "([^"]+)"', Line).group(1)
        if Ref in Holes:
            Drop = FpId != HoleFootprint
        elif Ref not in Comps or Comps[Ref]["footprint"] != FpId:
            Drop = True
        if not Drop:
            OnBoard.add(Ref)
    if not Drop:
        Out.extend(Block)
    Index = End + 1
open(BoardPath, "w", encoding="utf-8", newline="").write(Nl.join(Out))

Board = pcbnew.LoadBoard(BoardPath)

# 3. Outline
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

# 4. Footprints from the libraries, fields and nets from the netlist
ProjectNicks = set(re.findall(r'\(name "([^"]+)"\)', open("fp-lib-table", encoding="utf-8").read()))


def LoadFootprint(LibId):
    Nick, Name = LibId.split(":", 1)
    Path = os.path.abspath("HV_Pi_Hat.pretty") if Nick in ProjectNicks else "%s/%s.pretty" % (StdFootprints, Nick)
    Fp = pcbnew.FootprintLoad(Path, Name)
    if Fp is None:
        sys.exit("footprint %s not found in %s" % (LibId, Path))
    Fp.SetFPID(pcbnew.LIB_ID(Nick, Name))
    return Fp


for Ref in Holes:
    if Ref not in OnBoard:
        Fp = LoadFootprint(HoleFootprint)
        Fp.SetReference(Ref)
        Board.Add(Fp)
for Ref, C in sorted(Comps.items()):
    if Ref in OnBoard:
        continue
    Fp = LoadFootprint(C["footprint"])
    Fp.SetReference(Ref)
    Fp.SetValue(C["value"])
    Fp.SetField("Datasheet", C["datasheet"])
    Fp.SetField("Description", C["description"])
    Board.Add(Fp)
    print("added", Ref, C["footprint"])
Nets = {}
for Fp in Board.GetFootprints():
    Ref = Fp.GetReference()
    for Pad in Fp.Pads():
        Name = PinNet.get((Ref, Pad.GetNumber()))
        if Name is None:
            continue
        if Name not in Nets:
            Item = Board.FindNet(Name)
            if Item is None:
                Item = pcbnew.NETINFO_ITEM(Board, Name)
                Board.Add(Item)
            Nets[Name] = Item
        Pad.SetNet(Nets[Name])

# 5. Placement
Missing = []
for Fp in Board.GetFootprints():
    Ref = Fp.GetReference()
    if Ref not in Layout.Place:
        Missing.append(Ref)
        continue
    Spec = Layout.Place[Ref]
    X, Y, Rot = Spec[:3]
    Side = Spec[3] if len(Spec) > 3 else "F"
    Fp.SetPosition(Pt(X, Y))
    if (Side == "B") != Fp.IsFlipped():
        Fp.Flip(Fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    Fp.SetOrientationDegrees(Rot)
if Missing:
    sys.exit("no placement for: " + ", ".join(sorted(Missing)))

# 6. Pot outline, inner-layer voids, hole lands, PCIe notch strip
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


def RuleArea(Name, Points, Layers, Footprints=False):
    Z = pcbnew.ZONE(Board)
    Z.SetIsRuleArea(True)
    Z.SetDoNotAllowTracks(True)
    Z.SetDoNotAllowVias(True)
    Z.SetDoNotAllowZoneFills(True)
    Z.SetDoNotAllowPads(False)
    Z.SetDoNotAllowFootprints(Footprints)
    Ls = pcbnew.LSET()
    for L in Layers:
        Ls.AddLayer(Board.GetLayerID(L))
    Z.SetLayerSet(Ls)
    Z.SetZoneName(Name)
    Ol = Z.Outline()
    Ol.NewOutline()
    for (Ax, Ay) in Points:
        Ol.Append(FromMm(Ax), FromMm(Ay))
    Board.Add(Z)


for LayerName in ("In1.Cu", "In2.Cu"):
    RuleArea("PotVoid_" + LayerName, Poly, [LayerName])
AllCopper = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
for Ref in Holes:
    Hx, Hy = Layout.Place[Ref][:2]
    R = Layout.HoleLandDiameter / 2
    RuleArea("HoleLand_" + Ref, [(Hx + R * math.cos(math.radians(A)), Hy + R * math.sin(math.radians(A))) for A in range(0, 360, 15)], AllCopper)
Nx0, Ny0, Nx1, Ny1 = Layout.PcieNotch
RuleArea("PcieNotch", [(Nx0, Ny0), (Nx1, Ny0), (Nx1, Ny1), (Nx0, Ny1)], AllCopper, Footprints=True)

Board.Save(BoardPath)
print("pot outline:", ", ".join("(%.1f, %.1f)" % P for P in Poly))
print("saved", BoardPath)
