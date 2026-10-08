# AddIdEeprom.py - add the HAT+ ID EEPROM circuit to "HV Pi Hat.kicad_sch" (HAT+ spec ch. 2-3):
#   U3 CAT24C32 (24LC16 symbol, same 24Cxx SOIC-8 pinout), A0..A2 = GND (address 0x50, Standard class),
#   R27/R28 3.9k pull-ups on ID_SD/ID_SC to 3.3V, R29 1k WP pull-up with TP1 on WP, C6 100n decoupling,
#   PWR_FLAG on +3V3. Header pins 1 (3.3V), 27 (ID_SD), 28 (ID_SC) lose their no-connect flags.
# Connections are made by labels and power symbols placed exactly on pin endpoints (no wires).
# ONE-SHOT: already applied to the rev B schematic; running it again would add a second copy.
# Usage: python tools/revb/AddIdEeprom.py "HV Pi Hat.kicad_sch"
import re
import sys
import uuid

Path = sys.argv[1]
KiSym = "C:/Program Files/KiCad/10.0/share/kicad/symbols"
Text = open(Path, encoding="utf-8", newline="").read()
Nl = "\r\n" if "\r\n" in Text else "\n"
T = "\t"


def U():
    return str(uuid.uuid4())


def LibBlock(File, Name, NewName):
    Lib = open("%s/%s" % (KiSym, File), encoding="utf-8").read()
    I = Lib.index('\n\t(symbol "%s"' % Name)
    J = Lib.index("\n\t)", I + 5)
    Block = Lib[I + 1:J + 3]
    Block = Block.replace('(symbol "%s"' % Name, '(symbol "%s"' % NewName, 1)
    return "\n".join("\t" + L for L in Block.split("\n"))


# 1. Embed library symbols
Lib0 = Text.index(Nl + "\t(lib_symbols")
LibEnd = Text.index(Nl + "\t)", Lib0 + 5)
Add = []
for File, Name, NewName in (("Memory_EEPROM.kicad_sym", "24LC16", "Memory_EEPROM:24LC16"),
                            ("power.kicad_sym", "+3V3", "power:+3V3"),
                            ("Connector.kicad_sym", "TestPoint", "Connector:TestPoint")):
    if '(symbol "%s"' % NewName not in Text:
        Add.append(LibBlock(File, Name, NewName).replace("\n", Nl))
Text = Text[:LibEnd] + "".join(Nl + B for B in Add) + Text[LibEnd:]

# 2. Remove the no-connects on header pins 1, 27, 28 (positions checked against the Raspberry_Pi_5 symbol)
for (X, Y) in (("29.21", "21.59"), ("29.21", "54.61"), ("44.45", "54.61")):
    Pattern = re.compile(r"\t\(no_connect" + re.escape(Nl) + r"\t\t\(at " + re.escape(X) + " " + re.escape(Y) + r"\)" +
                         re.escape(Nl) + r"\t\t\(uuid \"[0-9a-f-]+\"\)" + re.escape(Nl) + r"\t\)" + re.escape(Nl))
    Text, N = Pattern.subn("", Text)
    if N != 1:
        sys.exit("no_connect at %s %s: %d matches" % (X, Y, N))

Root = "/425f3247-1bd7-4183-a2c3-fb59f31c6b53"


def Prop(Name, Value, X, Y, Hide=False, Justify=None):
    L = ['\t\t(property "%s" "%s"' % (Name, Value), "\t\t\t(at %g %g 0)" % (X, Y)]
    if Hide:
        L.append("\t\t\t(hide yes)")
    L += ["\t\t\t(show_name no)", "\t\t\t(do_not_autoplace no)", "\t\t\t(effects", "\t\t\t\t(font", "\t\t\t\t\t(size 1.27 1.27)", "\t\t\t\t)"]
    if Justify:
        L.append("\t\t\t\t(justify %s)" % Justify)
    L += ["\t\t\t)", "\t\t)"]
    return L


def Symbol(LibId, Ref, Value, Footprint, Desc, X, Y, Rot, Pins, Datasheet="", PowerSym=False):
    L = ["\t(symbol", '\t\t(lib_id "%s")' % LibId, "\t\t(at %g %g %d)" % (X, Y, Rot), "\t\t(unit 1)", "\t\t(body_style 1)",
         "\t\t(exclude_from_sim no)", "\t\t(in_bom yes)", "\t\t(on_board yes)", "\t\t(in_pos_files yes)", "\t\t(dnp no)",
         '\t\t(uuid "%s")' % U()]
    L += Prop("Reference", Ref, X + 2.54, Y - 1.27, Hide=PowerSym, Justify=None if PowerSym else "left")
    L += Prop("Value", Value, X + 2.54, Y + 1.27, Justify=None if PowerSym else "left")
    L += Prop("Footprint", Footprint, X, Y, Hide=True)
    L += Prop("Datasheet", Datasheet, X, Y, Hide=True)
    L += Prop("Description", Desc, X, Y, Hide=True)
    for P in Pins:
        L += ['\t\t(pin "%s"' % P, '\t\t\t(uuid "%s")' % U(), "\t\t)"]
    L += ["\t\t(instances", '\t\t\t(project "HV Pi Hat"', '\t\t\t\t(path "%s"' % Root, '\t\t\t\t\t(reference "%s")' % Ref,
          "\t\t\t\t\t(unit 1)", "\t\t\t\t)", "\t\t\t)", "\t\t)", "\t)"]
    return L


def Label(Name, X, Y):
    return ['\t(label "%s"' % Name, "\t\t(at %g %g 0)" % (X, Y), "\t\t(effects", "\t\t\t(font", "\t\t\t\t(size 1.27 1.27)", "\t\t\t)",
            "\t\t\t(justify left bottom)", "\t\t)", '\t\t(uuid "%s")' % U(), "\t)"]


Pwr = [10]


def Power(Kind, X, Y, Rot=0):
    Ref = "#PWR%02d" % Pwr[0]
    Pwr[0] += 1
    Desc = 'Power symbol creates a global label with name \\"%s\\"' % Kind
    return Symbol("power:%s" % Kind, Ref, Kind, "", Desc, X, Y, Rot, ["1"], PowerSym=True)


Items = []
# Header: 3.3V (pin 1), ID_SD (pin 27), ID_SC (pin 28)
Items += Power("+3V3", 29.21, 21.59, 90)
Items += Label("ID_SD", 29.21, 54.61)
Items += Label("ID_SC", 44.45, 54.61)
# U3 at (100.33, 190.5): 24LC16 pins (lib) A0 (-10.16, 2.54) A1 (-10.16, 0) A2 (-10.16, -2.54) GND (0, -7.62)
# SDA (10.16, 2.54) SCL (10.16, 0) WP (10.16, -2.54) VCC (0, 7.62); schematic = (X + px, Y - py)
Ux, Uy = 100.33, 190.5   # on the 1.27 mm grid
Items += Symbol("Memory_EEPROM:24LC16", "U3", "CAT24C32", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                "HAT+ ID EEPROM, OnSemi CAT24C32 (HAT+ spec 3.3.1); 24LC16 symbol used for the 24Cxx SOIC-8 pinout",
                Ux, Uy, 0, [str(N) for N in range(1, 9)], Datasheet="https://www.onsemi.com/pdf/datasheet/cat24c32-d.pdf")
for Py in (2.54, 0.0, -2.54):
    Items += Power("GND", Ux - 10.16, Uy - Py, 270)
Items += Power("GND", Ux, Uy + 7.62)
Items += Power("+3V3", Ux, Uy - 7.62)
Items += Label("ID_SD", Ux + 10.16, Uy - 2.54)
Items += Label("ID_SC", Ux + 10.16, Uy)
Items += Label("ID_WP", Ux + 10.16, Uy + 2.54)
# Pull-ups (R_Small_US: pin 1 at (0, 2.54) top, pin 2 at (0, -2.54) bottom)
for Ref, Value, X, Net in (("R27", "3.9k", 121.92, "ID_SD"), ("R28", "3.9k", 128.27, "ID_SC"), ("R29", "1k", 134.62, "ID_WP")):
    Items += Symbol("Device:R_Small_US", Ref, Value, "Resistor_SMD:R_0603_1608Metric", "Resistor, small US symbol", X, Uy, 0, ["1", "2"])
    Items += Power("+3V3", X, Uy - 2.54)
    Items += Label(Net, X, Uy + 2.54)
# WP test point (pin at origin)
Items += Symbol("Connector:TestPoint", "TP1", "ID_WP", "TestPoint:TestPoint_Pad_D1.5mm",
                "Test point: drive low to write the ID EEPROM (HAT+ spec 3.3)", 142.24, Uy + 2.54, 0, ["1"])
Items += Label("ID_WP", 142.24, Uy + 2.54)
# Decoupling (Device:C: pin 1 at (0, 3.81) top, pin 2 at (0, -3.81) bottom) and PWR_FLAG on +3V3
Items += Symbol("Device:C", "C6", "0.1 uF", "Capacitor_SMD:C_0603_1608Metric", "Unpolarized capacitor", 80.01, Uy, 0, ["1", "2"])
Items += Power("+3V3", 80.01, Uy - 3.81)
Items += Power("GND", 80.01, Uy + 3.81)
Items += Symbol("power:PWR_FLAG", "#FLG3", "PWR_FLAG", "", 'Special symbol for telling ERC where power comes from', 80.01, Uy - 3.81, 0, ["1"], PowerSym=True)

Block = Nl.join(Items) + Nl
Anchor = Nl + "\t(sheet_instances"
if Anchor in Text:
    I = Text.index(Anchor) + len(Nl)
else:
    I = Text.rstrip().rindex(")")
Text = Text[:I] + Block + Text[I:]
open(Path, "w", encoding="utf-8", newline="").write(Text)
print("added: U3 R27 R28 R29 C6 TP1 #FLG3, power symbols #PWR10..#PWR%02d" % (Pwr[0] - 1))
