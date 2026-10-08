# AutoRoute.py - grid A* router for rev B (from studies/hatplus/AutoRoute.py), plus:
#   - LV signal and power nets may enter the pot only inside RevBLayout.LvPotBand (U1's LV pin row);
#     GND is exempt (it is the HV return and has pads inside the pot).
#   - GND pours on F.Cu and B.Cu after routing, filled under the project's DRC rules.
#
# Usage (KiCad 10 python, from the project directory, after tools/revb/BuildRevB.py):
#   "/c/Program Files/KiCad/10.0/bin/python.exe" tools/revb/AutoRoute.py "HV Pi Hat.kicad_pcb" [HvClearanceMm]
#
# Rules (ADR-0002, ADR-0003 interim):
#   - HV nets (netclass HV_*) only on F.Cu / B.Cu, centerline at least PotMargin + half width inside
#     the pot polygon drawn on User.1; clearance HvClearance to every other net.
#   - Other nets anywhere, inner layers only outside the In1/In2 rule areas.
#   - Clearance between two nets = max of their netclass clearances (HV = HvClearance).
#   - Multi-pin nets are grown as a tree; own-net PTH pads are free layer changes, vias cost extra.
# Writes routed tracks and vias back into the board, then fills zones and saves.
import heapq
import math
import os
import sys
import numpy as np
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import RevBLayout

BoardPath = sys.argv[1]
HvClr = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
Res = 0.1
Guard = 0.06          # grid quantization guard added to every clearance
ViaD, ViaDrill = 0.6, 0.3
ViaCost = 50.0      # high: vias block every layer of the narrow header-to-pot strip
InnerCost = 1.15      # mild preference for outer layers
LvPotCost = 4.0       # LV nets pay this per step inside the pot, so they leave it unless they must enter
PotMargin = 3.0
EdgeClr = 0.5
ClassClr = {"Default": 0.2, "5V_Power_2A": 0.5, "5V_Power_Light": 0.3, "Sensitive": 0.3, "Signal": 0.25,
            "Switching_Noise": 0.5, "HV_5kV": HvClr, "HV_Return": HvClr, "GND_Stitch": 0.2, "GPIO_01": 0.25, "GPIO_12": 0.25}
PowerNets = {"+5V": 0.4, "Net-(U1-VIN)": 0.4, "GND": 0.4}
HvWidth = 0.25
SignalWidth = 0.254

Board = pcbnew.LoadBoard(BoardPath)
Mm = pcbnew.ToMM
Layers = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
LayerIds = [Board.GetLayerID(N) for N in Layers]


def FromMm(V):
    return pcbnew.FromMM(float(V))


def ClassNames(Item):
    return [N.strip() for N in Item.GetNetClassName().split(",")] if Item.GetNetname() else ["Default"]


def ClrOf(Item):
    return max(ClassClr.get(N, 0.2) for N in ClassNames(Item))


def IsHvName(Names):
    return any(N.startswith("HV_") for N in Names)


Bb = Board.GetBoardEdgesBoundingBox()
X0, X1, Y0, Y1 = Mm(Bb.GetLeft()), Mm(Bb.GetRight()), Mm(Bb.GetTop()), Mm(Bb.GetBottom())
Nx, Ny = int(round((X1 - X0) / Res)) + 1, int(round((Y1 - Y0) / Res)) + 1
Xs, Ys = X0 + np.arange(Nx) * Res, Y0 + np.arange(Ny) * Res
Gx, Gy = np.meshgrid(Xs, Ys)


def Cell(X, Y):
    return int(round((Y - Y0) / Res)), int(round((X - X0) / Res))


def Win(Xa, Xb, Ya, Yb):
    return (max(0, int(math.floor((Xa - X0) / Res))), min(Nx, int(math.ceil((Xb - X0) / Res)) + 1),
            max(0, int(math.floor((Ya - Y0) / Res))), min(Ny, int(math.ceil((Yb - Y0) / Res)) + 1))


def PolyInside(Poly, Px, Py):
    # even-odd point-in-polygon on grids
    Inside = np.zeros(Px.shape, dtype=bool)
    N = len(Poly)
    for K in range(N):
        (Ax, Ay), (Bx, By) = Poly[K], Poly[(K + 1) % N]
        Cond = ((Ay > Py) != (By > Py))
        with np.errstate(divide="ignore", invalid="ignore"):
            Xc = Ax + (Py - Ay) * (Bx - Ax) / (By - Ay)
        Inside ^= Cond & (Px < Xc)
    return Inside


def SegDistGrid(Ax, Ay, Bx, By, GX, GY):
    Dx, Dy = Bx - Ax, By - Ay
    L2 = Dx * Dx + Dy * Dy
    T = np.zeros_like(GX) if L2 == 0 else np.clip(((GX - Ax) * Dx + (GY - Ay) * Dy) / L2, 0, 1)
    return np.hypot(GX - (Ax + T * Dx), GY - (Ay + T * Dy))


# Pot polygon: the In1 rule area StudyBoard.py drew from the same points as the User.1 outline
PotPoly = None
for Z in Board.Zones():
    if Z.GetIsRuleArea() and Z.GetZoneName() == "PotVoid_In1.Cu":
        Ol = Z.Outline().Outline(0)
        PotPoly = [(Mm(Ol.CPoint(I).x), Mm(Ol.CPoint(I).y)) for I in range(Ol.PointCount())]
if PotPoly is None:
    sys.exit("pot rule area PotVoid_In1.Cu not found")
InPot = PolyInside(PotPoly, Gx, Gy)
# Distance-to-pot-boundary test: a cell is "deep" if a disc of radius R around it is inside the pot
def ErodedPot(R):
    Out = InPot.copy()
    K = int(math.ceil(R / Res))
    Pad = np.pad(InPot, K, constant_values=False)
    for Dj in range(-K, K + 1):
        for Di in range(-K, K + 1):
            if math.hypot(Dj, Di) * Res <= R:
                Out &= Pad[K + Dj:K + Dj + Ny, K + Di:K + Di + Nx]
    return Out


HvZoneOk = ErodedPot(PotMargin + HvWidth / 2)
Bx0, Bx1, By0, By1 = RevBLayout.LvPotBand
LvForbidden = InPot & ~((Gx >= Bx0) & (Gx <= Bx1) & (Gy >= By0) & (Gy <= By1))
HvViaOk = ErodedPot(PotMargin + ViaD / 2)

# Static geometry: pads, keepouts, edges
Pads = []
for Fp in Board.GetFootprints():
    for Pad in Fp.Pads():
        S = Pad.GetSize(pcbnew.F_Cu)
        Sx, Sy = Mm(S.x), Mm(S.y)
        Lids = [L for L, Lid in enumerate(LayerIds) if Pad.IsOnLayer(Lid)]
        Drill = Mm(max(Pad.GetDrillSize().x, Pad.GetDrillSize().y)) if Pad.HasHole() else 0.0
        Pads.append({"name": Fp.GetReference() + "." + Pad.GetNumber(), "net": Pad.GetNetname(), "x": Mm(Pad.GetPosition().x),
                     "y": Mm(Pad.GetPosition().y), "sx": Sx, "sy": Sy, "rot": Pad.GetOrientationDegrees(), "layers": Lids,
                     "pth": Pad.HasHole(), "drill": Drill, "clr": ClrOf(Pad), "hv": IsHvName(ClassNames(Pad))})
KeepoutPolys = []
for Z in Board.Zones():
    if Z.GetIsRuleArea():
        Ol = Z.Outline().Outline(0)
        Poly = [(Mm(Ol.CPoint(I).x), Mm(Ol.CPoint(I).y)) for I in range(Ol.PointCount())]
        for Lid in Z.GetLayerSet().Seq():
            if Board.GetLayerName(Lid) in Layers:
                KeepoutPolys.append((Layers.index(Board.GetLayerName(Lid)), Poly))
InnerBlocked = np.zeros((4, Ny, Nx), dtype=bool)
for L, Poly in KeepoutPolys:
    InnerBlocked[L] |= PolyInside(Poly, Gx, Gy)

Routed = []   # (net, layer, ax, ay, bx, by, width, clr)
RoutedVias = []  # (net, x, y, clr)


def PadDist(P, GX, GY):
    A = math.radians(P["rot"])
    Lx = (GX - P["x"]) * math.cos(A) - (GY - P["y"]) * math.sin(A)
    Ly = (GX - P["x"]) * math.sin(A) + (GY - P["y"]) * math.cos(A)
    Qx = np.maximum(np.abs(Lx) - P["sx"] / 2, 0)
    Qy = np.maximum(np.abs(Ly) - P["sy"] / 2, 0)
    return np.hypot(Qx, Qy)


def BuildMasks(Net, OwnClr, HalfW):
    Track = np.zeros((4, Ny, Nx), dtype=bool)
    Via = np.zeros((Ny, Nx), dtype=bool)
    for P in Pads:
        if P["net"] == Net and Net:
            continue
        Clr = max(OwnClr, P["clr"] if P["net"] else 0.25) + Guard
        Ext = math.hypot(P["sx"], P["sy"]) / 2 + Clr + ViaD
        I0, I1, J0, J1 = Win(P["x"] - Ext, P["x"] + Ext, P["y"] - Ext, P["y"] + Ext)
        D = PadDist(P, Gx[J0:J1, I0:I1], Gy[J0:J1, I0:I1])
        for L in P["layers"]:
            Track[L, J0:J1, I0:I1] |= D < Clr + HalfW
        Via[J0:J1, I0:I1] |= D < Clr + ViaD / 2
        if P["pth"]:
            Dh = np.hypot(Gx[J0:J1, I0:I1] - P["x"], Gy[J0:J1, I0:I1] - P["y"]) - P["drill"] / 2
            for L in range(4):
                Track[L, J0:J1, I0:I1] |= Dh < max(Clr, 0.25 + Guard) + HalfW
    for (N, L, Ax, Ay, Bx, By, W, C) in Routed:
        if N == Net:
            continue
        Clr = max(OwnClr, C) + Guard
        Ext = W / 2 + Clr + ViaD
        I0, I1, J0, J1 = Win(min(Ax, Bx) - Ext, max(Ax, Bx) + Ext, min(Ay, By) - Ext, max(Ay, By) + Ext)
        D = SegDistGrid(Ax, Ay, Bx, By, Gx[J0:J1, I0:I1], Gy[J0:J1, I0:I1]) - W / 2
        Track[L, J0:J1, I0:I1] |= D < Clr + HalfW
        Via[J0:J1, I0:I1] |= D < Clr + ViaD / 2
    for (N, X, Y, C) in RoutedVias:
        if N == Net:
            continue
        Clr = max(OwnClr, C) + Guard
        Ext = ViaD / 2 + Clr + ViaD
        I0, I1, J0, J1 = Win(X - Ext, X + Ext, Y - Ext, Y + Ext)
        D = np.hypot(Gx[J0:J1, I0:I1] - X, Gy[J0:J1, I0:I1] - Y) - ViaD / 2
        for L in range(4):
            Track[L, J0:J1, I0:I1] |= D < Clr + HalfW
        Via[J0:J1, I0:I1] |= D < max(Clr, 0.25 + Guard) + ViaD / 2
    # board edge
    for Mask, Own in ((Track, HalfW), (None, ViaD / 2)):
        M = int(math.ceil((EdgeClr + Own + Guard) / Res))
        Tgt = Mask if Mask is not None else Via
        if Tgt.ndim == 3:
            Tgt[:, :M, :] = Tgt[:, -M:, :] = True
            Tgt[:, :, :M] = Tgt[:, :, -M:] = True
        else:
            Tgt[:M, :] = Tgt[-M:, :] = True
            Tgt[:, :M] = Tgt[:, -M:] = True
    Track |= InnerBlocked
    Via |= InnerBlocked[1] | InnerBlocked[2]
    return Track, Via


Moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]


def AStar(Track, ViaOk, FreeSwitch, Sources, Goals, AllowedLayers, StepCost=None):
    GoalSet = set(Goals)
    Gj = np.mean([G[1] for G in Goals])
    Gi = np.mean([G[2] for G in Goals])
    Best, Parent, Open = {}, {}, []
    for S in Sources:
        Best[S] = 0.0
        heapq.heappush(Open, (math.hypot(S[1] - Gj, S[2] - Gi), 0.0, S))
    while Open:
        F, G, C = heapq.heappop(Open)
        if C in GoalSet:
            Path = [C]
            while Path[-1] in Parent:
                Path.append(Parent[Path[-1]])
            return Path[::-1]
        if G > Best.get(C, 1e18):
            continue
        L, J, I = C
        Step = InnerCost if L in (1, 2) else 1.0
        if StepCost is not None:
            Step *= StepCost[J, I]
        for Dj, Di, Cost in Moves:
            Nj, Ni = J + Dj, I + Di
            if 0 <= Nj < Ny and 0 <= Ni < Nx:
                N = (L, Nj, Ni)
                if not Track[L, Nj, Ni] or N in GoalSet:
                    Ng = G + Cost * Step
                    if Ng < Best.get(N, 1e18):
                        Best[N] = Ng
                        Parent[N] = C
                        heapq.heappush(Open, (Ng + math.hypot(Nj - Gj, Ni - Gi), Ng, N))
        Free = (J, I) in FreeSwitch
        if Free or ViaOk[J, I]:
            for L2 in AllowedLayers:
                if L2 == L or (Track[L2, J, I] and (L2, J, I) not in GoalSet):
                    continue
                N = (L2, J, I)
                Ng = G + (0.5 if Free else ViaCost)
                if Ng < Best.get(N, 1e18):
                    Best[N] = Ng
                    Parent[N] = C
                    heapq.heappush(Open, (Ng + math.hypot(J - Gj, I - Gi), Ng, N))
    return None


def PadCells(P, Allowed):
    # Cells inside the pad's inscribed circle (always inside the copper, whatever the pad shape)
    R = min(P["sx"], P["sy"]) / 2 - 0.05
    K = int(math.ceil(R / Res))
    J, I = Cell(P["x"], P["y"])
    Out = []
    for Dj in range(-K, K + 1):
        for Di in range(-K, K + 1):
            if math.hypot(Dj, Di) * Res <= R:
                for L in P["layers"]:
                    if L in Allowed:
                        Out.append((L, J + Dj, I + Di))
    return Out


def Rasterize(L, A, B):
    (Ja, Ia), (Jb, Ib) = A, B
    Steps = int(max(abs(Jb - Ja), abs(Ib - Ia)) * 2) + 1
    return [(L, int(round(Ja + (Jb - Ja) * T / Steps)), int(round(Ia + (Ib - Ia) * T / Steps))) for T in range(Steps + 1)]


def LineFree(Track, L, A, B):
    (Ja, Ia), (Jb, Ib) = A, B
    Steps = int(max(abs(Jb - Ja), abs(Ib - Ia)) * 2) + 1
    for S in range(Steps + 1):
        T = S / Steps
        if Track[L, int(round(Ja + (Jb - Ja) * T)), int(round(Ia + (Ib - Ia) * T))]:
            return False
    return True


def ToGeometry(Path, Track, FreeSwitch):
    Runs, Cur = [], [Path[0]]
    for C in Path[1:]:
        if C[0] != Cur[-1][0]:
            Runs.append(Cur)
            Cur = [C]
        else:
            Cur.append(C)
    Runs.append(Cur)
    Segs, Vias = [], []
    for K, Run in enumerate(Runs):
        L = Run[0][0]
        Pts = [(C[1], C[2]) for C in Run]
        Out, Idx = [Pts[0]], 0
        while Idx < len(Pts) - 1:
            Nxt = len(Pts) - 1
            while Nxt > Idx + 1 and not LineFree(Track, L, Pts[Idx], Pts[Nxt]):
                Nxt -= 1
            Out.append(Pts[Nxt])
            Idx = Nxt
        for A, B in zip(Out[:-1], Out[1:]):
            Segs.append((L, A, B))
        if K < len(Runs) - 1 and Run[-1][1:] not in FreeSwitch:
            Vias.append(Run[-1][1:])
    return Segs, Vias


def Xy(JI):
    return X0 + JI[1] * Res, Y0 + JI[0] * Res


NetPads = {}
for P in Pads:
    if P["net"] and not P["net"].startswith("unconnected"):
        NetPads.setdefault(P["net"], []).append(P)
HvNets = sorted(N for N, Ps in NetPads.items() if Ps[0]["hv"])
# Nets that must reach U1's LV pins through the header-to-pot strip go first, GND (pours too) last
StripNets = ["Net-(U1-VIN)", "+5V", "/GPIO_12_Boost"]
Order = HvNets + StripNets + sorted(N for N in NetPads if N not in HvNets and N not in PowerNets and N not in StripNets) + ["GND"]
Failed = []
LvStep = np.where(InPot, LvPotCost, 1.0)
for Net in Order:
    Ps = NetPads.get(Net, [])
    if len(Ps) < 2:
        continue
    Hv = Ps[0]["hv"]
    Width = HvWidth if Hv else PowerNets.get(Net, SignalWidth)
    OwnClr = HvClr if Hv else max(P["clr"] for P in Ps)
    Track, ViaBlk = BuildMasks(Net, OwnClr, Width / 2)
    Allowed = [0, 3] if Hv else [0, 1, 2, 3]
    if Hv:
        for L in (1, 2):
            Track[L] = True
        Track[0] |= ~HvZoneOk
        Track[3] |= ~HvZoneOk
        ViaBlk |= ~HvViaOk
    if not Hv and Net != "GND":
        Track |= LvForbidden[np.newaxis, :, :]
        ViaBlk |= LvForbidden
    ViaOk = ~ViaBlk
    FreeSwitch = set()
    for P in Ps:
        if P["pth"]:
            for (L, J, I) in PadCells(P, [0]):
                FreeSwitch.add((J, I))
    # own pads are passable on their layers
    for P in Ps:
        for C in PadCells(P, Allowed):
            Track[C] = False
    PadCenter = {}
    for P in Ps:
        Cj, Ci = Cell(P["x"], P["y"])
        for (L, J, I) in PadCells(P, Allowed):
            PadCenter[(J, I)] = (Cj, Ci)
    Remaining = sorted(Ps, key=lambda P: (P["x"], P["y"]))
    First = Remaining.pop(0)
    Tree = PadCells(First, Allowed)
    NetSegs, NetVias = [], []
    while Remaining:
        Tj = np.mean([C[1] for C in Tree])
        Ti = np.mean([C[2] for C in Tree])
        Remaining.sort(key=lambda P: min(math.hypot(Cell(P["x"], P["y"])[0] - C[1], Cell(P["x"], P["y"])[1] - C[2]) for C in Tree[::max(1, len(Tree) // 200)]))
        Target = Remaining.pop(0)
        Goals = PadCells(Target, Allowed)
        Path = AStar(Track, ViaOk, FreeSwitch, Tree, Goals, Allowed, None if Hv else LvStep)
        if Path is None:
            Failed.append((Net, Target["name"]))
            print("FAIL", Net, "->", Target["name"])
            continue
        # Snap ends that land in an own pad to the pad center so the copper connects
        for End in (0, -1):
            C = Path[End]
            if (C[1], C[2]) in PadCenter:
                Cj, Ci = PadCenter[(C[1], C[2])]
                Snap = (C[0], Cj, Ci)
                if Snap != C:
                    if End == 0:
                        Path.insert(0, Snap)
                    else:
                        Path.append(Snap)
        Segs, Vias = ToGeometry(Path, Track, FreeSwitch)
        NetSegs += Segs
        NetVias += Vias
        for L, A, B in Segs:
            Tree += Rasterize(L, A, B)
        for V in Vias:
            Tree += [(L, V[0], V[1]) for L in Allowed]
        Tree += Goals
    for L, A, B in NetSegs:
        (Ax, Ay), (Bx, By) = Xy(A), Xy(B)
        if (Ax, Ay) != (Bx, By):
            Routed.append((Net, L, Ax, Ay, Bx, By, Width, OwnClr))
    for V in NetVias:
        X, Y = Xy(V)
        RoutedVias.append((Net, X, Y, OwnClr))
    print("routed %-22s segs %3d vias %2d" % (Net, len(NetSegs), len(NetVias)))

for (N, L, Ax, Ay, Bx, By, W, C) in Routed:
    T = pcbnew.PCB_TRACK(Board)
    T.SetStart(pcbnew.VECTOR2I(FromMm(Ax), FromMm(Ay)))
    T.SetEnd(pcbnew.VECTOR2I(FromMm(Bx), FromMm(By)))
    T.SetWidth(FromMm(W))
    T.SetLayer(LayerIds[L])
    T.SetNet(Board.FindNet(N))
    Board.Add(T)
for (N, X, Y, C) in RoutedVias:
    V = pcbnew.PCB_VIA(Board)
    V.SetPosition(pcbnew.VECTOR2I(FromMm(X), FromMm(Y)))
    V.SetWidth(FromMm(ViaD))
    V.SetDrill(FromMm(ViaDrill))
    V.SetViaType(pcbnew.VIATYPE_THROUGH)
    V.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    V.SetNet(Board.FindNet(N))
    Board.Add(V)
# GND THT pads inside the pot: solid zone connection (traces nearby starve thermal spokes there)
for Fp in Board.GetFootprints():
    for Pad in Fp.Pads():
        if Pad.GetNetname() == "GND" and Pad.HasHole():
            J, I = Cell(Mm(Pad.GetPosition().x), Mm(Pad.GetPosition().y))
            if 0 <= J < Ny and 0 <= I < Nx and InPot[J, I]:
                Pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
# GND pours on both outer faces (the .kicad_dru keeps them 4 mm from HV)
Edge = Board.GetBoardEdgesBoundingBox()
for LayerName in ("F.Cu", "B.Cu"):
    Z = pcbnew.ZONE(Board)
    Z.SetLayer(Board.GetLayerID(LayerName))
    Z.SetNet(Board.FindNet("GND"))
    Z.SetZoneName("GND_" + LayerName)
    Z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    Ol = Z.Outline()
    Ol.NewOutline()
    for (Px, Py) in ((X0 + 0.3, Y0 + 0.3), (X1 - 0.3, Y0 + 0.3), (X1 - 0.3, Y1 - 0.3), (X0 + 0.3, Y1 - 0.3)):
        Ol.Append(FromMm(Px), FromMm(Py))
    Board.Add(Z)
pcbnew.ZONE_FILLER(Board).Fill(Board.Zones())
Board.Save(BoardPath)
print("failed connections:", len(Failed), Failed)
