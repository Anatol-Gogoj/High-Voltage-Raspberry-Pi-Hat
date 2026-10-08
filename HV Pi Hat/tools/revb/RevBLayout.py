# RevBLayout.py - rev B placement (board coordinates, mm). Started from studies/hatplus/Layout.py;
# J3/J4 are now the HV_LeadPair_P6.00mm footprint (pad 1 return, pad 2 HV).
# Footprint origin and rotation follow KiCad: rotation -90 maps local (x, y) to board (X - y, Y + x).

# HAT outline for a through-hole GPIO header: 65 x 56.0 mm, holes 3.5 mm from every edge, 3 mm corners.
# Legacy HAT drawing (github.com/raspberrypi/hats, hat-board-mechanical.pdf): "56.5mm FOR SMT STYLE
# GPIO HEADER OTHERWISE 56.0mm FOR THROUGH HOLE HEADER"; the bottom holes are 3.5 from the bottom edge.
Outline = (117.5, 86.0, 182.5, 142.0, 3.0)
# Mounting-hole land: "MIN. 6.2mm and EITHER ISOLATED COPPER OR BARE BOARD" (same drawing)
HoleLandDiameter = 6.2
# Keep the Pi 5 PCIe FFC edge free so a flex notch stays possible (M.2 HAT+ notch, HAT+ spec Fig. 3)
PcieNotch = (117.5, 103.0, 122.5, 121.0)

# Pot (ADR-0003 interim): 3 mm beyond HV copper; notch radius around the H4 screw
PotMargin = 3.0
H4Notch = (179.0, 138.5, 3.5)

# LV signals may enter the pot only in this band over U1's LV pin row (x0, x1, y0, y1)
LvPotBand = (159.5, 182.5, 86.0, 101.8)  # y0 above the pot top so no sliver of pot is left outside the band

Place = {
    # Mechanical: standard HAT+ hole pattern and header (unchanged from rev A)
    "H1": (179.0, 89.5, 0), "H2": (121.0, 89.5, 0), "H3": (121.0, 138.5, 0), "H4": (179.0, 138.5, 0),
    # GPIO socket on the underside (ADR-0005); flipped and at -90 its pads match the top-side header
    "GPIO1": (125.875, 90.775, -90, "B"),
    # HV module: courtyard x 160.0..182.2, y 96.5..118.7; LV pins on the top row, HV pin 8 bottom-left
    "U1": (160.3, 96.8, -90),
    # Opto column: LED pins face left (x 147.05), HV pins face right (x 154.0)
    "OR1": (144.0, 95.8, -90),   # CH1 charge: pin3 HV_RAIL, pin4 HV_CH1
    "OR2": (144.0, 107.3, -90),  # CH2 charge: pin3 HV_RAIL, pin4 HV_CH2
    "OR3": (144.0, 118.8, -90),  # CH1 discharge: pin3 HV_CH1_DIS, pin4 GND
    "OR4": (144.0, 130.3, -90),  # CH2 discharge: pin3 HV_CH2_DIS, pin4 GND
    # HV lead pairs: J3 vertical at the right edge (HV pad 2 at y 122.0 beside R1/R25, return below);
    # J4 along the bottom edge (return pad 1 at x 164.0, HV pad 2 at x 170.0 beside R2, 3 mm pot margin)
    "J3": (178.0, 128.0, 90),
    "J4": (164.0, 137.8, 0),
    # HV resistors under U1, rotated 180 so pad1 (HV_CHx) is on the right
    "R1": (165.5, 121.0, 180),   # R_dis CH1: HV_CH1 / HV_CH1_DIS
    "R25": (165.5, 125.3, 180),  # R_safety CH1: HV_CH1 / GND
    "R26": (165.5, 129.6, 180),  # R_safety CH2: HV_CH2 / GND
    "R2": (165.5, 133.9, 180),   # R_dis CH2: HV_CH2 / HV_CH2_DIS
    # Ferrite next to U1 pin 1 (VIN); the +5V bulk caps sit at the power entry by header pins 2/4
    # (ADR-0001: bulk stays on +5V, before the ferrite)
    "FB1": (177.0, 94.6, 0),
    "C2": (124.6, 106.0, 90), "C3": (124.6, 110.0, 90), "C4": (124.6, 113.2, 90),
    # PGM stage, top-left
    "U2": (125.0, 97.5, 0), "R9": (128.5, 97.5, 90), "R10": (128.5, 100.8, 90), "C5": (128.0, 94.4, 0),
    "R7": (120.5, 98.0, 90), "R8": (120.5, 101.6, 90), "C1": (123.8, 101.4, 0),
    # HAT+ ID EEPROM (HAT+ spec ch. 3): CAT24C32, ID_SD/ID_SC pull-ups, WP pull-up + test point
    "U3": (127.5, 124.0, 0), "R27": (124.6, 129.0, 0), "R28": (128.4, 129.0, 0),
    "R29": (124.6, 131.6, 0), "C6": (128.4, 131.6, 0), "TP1": (131.2, 134.2, 0),
}


def Cluster(Oy, Q, Rled, Rgate, Rpd, Rind=None, Led=None):
    # One opto driver, aligned with the opto whose origin y is Oy (LED+ at Oy+0.635, LED- at Oy+9.525)
    Place[Q] = (139.0, Oy + 9.5, 0)          # drain (pin 3) at x 141.54 faces the opto LED- pin
    Place[Rled] = (141.0, Oy + 1.2, 0)       # +5V to LED+ (15 Ohm 1206, ADR-0006)
    Place[Rgate] = (134.5, Oy + 8.2, 0)      # GPIO to gate
    Place[Rpd] = (134.5, Oy + 10.5, 0)       # gate pulldown
    if Rind:
        Place[Led] = (136.0, Oy + 1.2, 0)    # indicator LED, anode on +5V
        Place[Rind] = (136.0, Oy + 4.0, 0)   # indicator resistor to the drain


Cluster(95.8, "Q3", "R6", "R17", "R19", "R11", "D1")    # OR1, GPIO_5
Cluster(107.3, "Q1", "R14", "R18", "R20", "R15", "D2")  # OR2, GPIO_26
Cluster(118.8, "Q2", "R21", "R16", "R13")               # OR3, GPIO_6
Cluster(130.3, "Q4", "R22", "R23", "R24")               # OR4, GPIO_16


# Vertical budget between the Pi 5 and the HAT underside (tools/revb/PiKeepouts.py)
Standoff = 20.0        # ADR-0005: 20 mm (HAT+ spec: 16 mm ideal, "even larger" with underside parts)
ThtProtrusion = 1.5    # assumed: THT leads trimmed to 1.5 mm below the HAT
BottomPot = 3.0        # assumed: bottom pot thickness over the HV zone (covers the trimmed leads)

# Pi 5 top-side parts, hole-referenced: Xh/Yh in mm from the centre of the hole nearest GPIO pin 1,
# +X toward USB/Ethernet, +Y away from the GPIO header (board x = 121.0 + Xh, board y = 89.5 + Yh).
# Heights above the Pi PCB. Sources: P5 = raspberry-pi-5-mechanical-drawing.pdf (RP-008347-DS-1),
# AC = Active Cooler drawing RP-008187-DS-1, DOC = raspberrypi.com documentation. Extents marked "meas"
# were measured from the official vector PDFs (the drawing says all dimensions are approximate).
Pi5Parts = [
    ("ActiveCooler", (-3.2, 2.8, 60.8, 46.0), 13.70, "AC 13.70 overall (pin tip to cap top); footprint meas"),
    ("CoolerFan", (24.0, 4.5, 54.0, 34.5), 13.70, "AC 30 x 30 fan; position meas"),
    ("PoE", (55.5, 40.5, 60.5, 45.5), 8.6, "P5 centre (58, 43); pins 8.6 meas"),
    ("FPC_A", (43.7, 36.3, 46.7, 51.8), 4.1, "P5 side view 4.1; extent meas"),
    ("FPC_B", (50.0, 36.3, 52.9, 51.8), 4.1, "P5 side view 4.1; extent meas"),
    ("UART", (26.2, 47.0, 31.5, 50.2), 4.4, "P5 4.4; location third-party"),
    ("RTC_J5", (13.5, 46.3, 17.5, 49.2), 4.5, "DOC location; meas"),
    ("PCIe_FFC", (-2.3, 17.3, 0.7, 27.8), 4.2, "DOC location; meas"),
    ("FanConn", (61.7, -2.5, 64.7, 3.5), 4.5, "DOC location; meas"),
    ("RJ45", (63.3, 34.3, 84.5, 50.3), 14.0, "P5; meas"),
    ("USB_A_1", (67.2, -1.8, 84.8, 12.8), 15.9, "P5; meas"),
    ("USB_A_2", (67.2, 16.2, 84.8, 30.8), 15.9, "P5; meas"),
]
