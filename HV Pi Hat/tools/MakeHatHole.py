# MakeHatHole.py - generate HV_Pi_Hat.pretty/MountingHole_2.75mm_M2.5_NPTH_HAT.kicad_mod.
# Legacy HAT drawing (github.com/raspberrypi/hats, hat-board-mechanical.pdf): "MOUTING HOLES SHOULD IDEALLY
# BE NON-PLATED", "DRILLED TO 2.75mm +/- 0.05mm", land "MIN. 6.2mm and EITHER ISOLATED COPPER OR BARE BOARD".
# The 6.2 mm land is kept copper-free by rule areas in tools/revb/BuildRevB.py; the courtyard marks it.
# Usage: "/c/Program Files/KiCad/10.0/bin/python.exe" tools/MakeHatHole.py
import os
import pcbnew

Lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "HV_Pi_Hat.pretty")
Name = "MountingHole_2.75mm_M2.5_NPTH_HAT"
Drill, Land = 2.75, 6.2


def Mm(V):
    return pcbnew.FromMM(float(V))


def Pt(X, Y):
    return pcbnew.VECTOR2I(Mm(X), Mm(Y))


Board = pcbnew.BOARD()
Fp = pcbnew.FOOTPRINT(Board)
Fp.SetFPID(pcbnew.LIB_ID("HV_Footprints", Name))
Fp.SetLibDescription("Raspberry Pi HAT mounting hole: M2.5, NPTH 2.75 mm, 6.2 mm copper-free land (HAT drawing)")
Fp.SetKeywords("mounting hole M2.5 HAT NPTH")
Fp.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
Fp.SetReference("REF**")
Fp.SetValue(Name)
Fp.Reference().SetPosition(Pt(0, -4.0))
Fp.Reference().SetLayer(pcbnew.F_SilkS)
Fp.Value().SetPosition(Pt(0, 4.0))
Fp.Value().SetLayer(pcbnew.F_Fab)
Pad = pcbnew.PAD(Fp)
Pad.SetNumber("")
Pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
Pad.SetLayerSet(Pad.UnplatedHoleMask())
Pad.SetShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_CIRCLE)
Pad.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(Mm(Drill), Mm(Drill)))
Pad.SetDrillSize(pcbnew.VECTOR2I(Mm(Drill), Mm(Drill)))
Pad.SetPosition(Pt(0, 0))
Fp.Add(Pad)
for Layer, Radius, Width in ((pcbnew.F_CrtYd, Land / 2, 0.05), (pcbnew.B_CrtYd, Land / 2, 0.05), (pcbnew.F_Fab, Land / 2, 0.1)):
    C = pcbnew.PCB_SHAPE(Fp, pcbnew.SHAPE_T_CIRCLE)
    C.SetLayer(Layer)
    C.SetCenter(Pt(0, 0))
    C.SetEnd(Pt(Radius, 0))
    C.SetWidth(Mm(Width))
    Fp.Add(C)
Io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
Io.FootprintSave(os.path.abspath(Lib), Fp)
print("saved", os.path.join(os.path.abspath(Lib), Name + ".kicad_mod"))
