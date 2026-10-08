# MakeLeadPair.py - generate HV_Pi_Hat.pretty/HV_LeadPair_P6.00mm.kicad_mod (ADR-0003: HV leaves the
# potted zone only as soldered insulated leads).
# Pad 1 = return (GND), pad 2 = HV. 2.4 mm round pads, 1.2 mm drill (18 to 20 AWG HV silicone wire),
# 6.0 mm pitch: 3.6 mm between pad edges, which clears both the 2 mm interim and the 3 mm study case.
# Usage: "/c/Program Files/KiCad/10.0/bin/python.exe" tools/MakeLeadPair.py
import os
import pcbnew

Lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "HV_Pi_Hat.pretty")
Pitch, PadD, Drill = 6.0, 2.4, 1.2


def Mm(V):
    return pcbnew.FromMM(float(V))


def Pt(X, Y):
    return pcbnew.VECTOR2I(Mm(X), Mm(Y))


Board = pcbnew.BOARD()
Fp = pcbnew.FOOTPRINT(Board)
Fp.SetFPID(pcbnew.LIB_ID("HV_Footprints", "HV_LeadPair_P6.00mm"))
Fp.SetLibDescription("Soldered HV lead pair for a potted zone: pad 1 return, pad 2 HV, 6.0 mm pitch, 1.2 mm drill")
Fp.SetKeywords("HV lead wire solder pot")
Fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
Fp.SetReference("REF**")
Fp.SetValue("HV_LeadPair_P6.00mm")
Fp.Reference().SetPosition(Pt(Pitch / 2, -2.6))
Fp.Reference().SetLayer(pcbnew.F_SilkS)
Fp.Value().SetPosition(Pt(Pitch / 2, 2.6))
Fp.Value().SetLayer(pcbnew.F_Fab)
for Number, X in (("1", 0.0), ("2", Pitch)):
    Pad = pcbnew.PAD(Fp)
    Pad.SetNumber(Number)
    Pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    Pad.SetLayerSet(Pad.PTHMask())
    Pad.SetShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_CIRCLE)
    Pad.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(Mm(PadD), Mm(PadD)))
    Pad.SetDrillSize(pcbnew.VECTOR2I(Mm(Drill), Mm(Drill)))
    Pad.SetPosition(Pt(X, 0))
    Fp.Add(Pad)


def Rect(Layer, X0, Y0, X1, Y1, W):
    for (Ax, Ay, Bx, By) in ((X0, Y0, X1, Y0), (X1, Y0, X1, Y1), (X1, Y1, X0, Y1), (X0, Y1, X0, Y0)):
        S = pcbnew.PCB_SHAPE(Fp, pcbnew.SHAPE_T_SEGMENT)
        S.SetStart(Pt(Ax, Ay))
        S.SetEnd(Pt(Bx, By))
        S.SetLayer(Layer)
        S.SetWidth(Mm(W))
        Fp.Add(S)


Half = PadD / 2
Rect(pcbnew.F_CrtYd, -Half - 0.25, -Half - 0.25, Pitch + Half + 0.25, Half + 0.25, 0.05)
Rect(pcbnew.F_Fab, -Half, -Half, Pitch + Half, Half, 0.1)
for Text, X in (("RTN", 0.0), ("HV", Pitch)):
    T = pcbnew.PCB_TEXT(Fp)
    T.SetText(Text)
    T.SetPosition(Pt(X, 2.2))
    T.SetLayer(pcbnew.F_SilkS)
    T.SetTextSize(pcbnew.VECTOR2I(Mm(0.8), Mm(0.8)))
    T.SetTextThickness(Mm(0.12))
    Fp.Add(T)
Io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)  # KiCad 10 name (was PluginFind in 9)
Io.FootprintSave(os.path.abspath(Lib), Fp)
print("saved", os.path.join(os.path.abspath(Lib), "HV_LeadPair_P6.00mm.kicad_mod"))
