# Tooling: HV Pi Hat

- **kicad-cli:** `/c/Program Files/KiCad/10.0/bin/kicad-cli.exe` (10.0.1 verified 2026-10-08)
- **KiCad Python (has `pcbnew`):** `/c/Program Files/KiCad/10.0/bin/python.exe`
- The project is KiCad 10 format. The 9.0 CLI cannot load the schematic.
- Run commands from the project dir (parent of `docs/`); files: `HV Pi Hat.kicad_pcb` / `.kicad_sch`.

## DRC (honors the custom HV rules in `HV Pi Hat.kicad_dru`)
    kicad-cli pcb drc --format json --severity-all --schematic-parity \
      --output drc.json "HV Pi Hat.kicad_pcb"
Use kicad-cli, not `pcbnew.WriteDRCReport`, which asserts ("process failed") outside the GUI.
HV rule violations show up as `clearance`, `creepage`, `copper_edge_clearance`, `hole_clearance`.

## ERC
    kicad-cli sch erc --format json --severity-all --output erc.json "HV Pi Hat.kicad_sch"

## BOM
    kicad-cli sch export bom --fields "Reference,Value,Footprint,QUANTITY,DNP" \
      --labels "Reference,Value,Footprint,QUANTITY,DNP" --group-by "Value,Footprint" \
      --ref-range-delimiter "" -o fab/BOM.csv "HV Pi Hat.kicad_sch"

## Render (PNG)
    kicad-cli pcb render --side top --quality basic --width 1600 --height 1100 -o render_top.png "HV Pi Hat.kicad_pcb"

## Netlist (read connectivity without the GUI)
    kicad-cli sch export netlist -o net.net "HV Pi Hat.kicad_sch"
Fails to load while the `.sch` is open in eeschema; close eeschema first.

## HV interlayer check (what the 2-D DRC cannot see)
    "/c/Program Files/KiCad/10.0/bin/python.exe" tools/HvInterlayer.py "HV Pi Hat.kicad_pcb"
Prints the smallest 3-D distances between HV copper and non-HV copper on other layers, using the
ADR-0002 stackup, and the average field at 5 kV. Re-run after any HV re-route or stackup change.
Round pads use their true radius; other pads their circumscribed circle (conservative).

## pcbnew scripting gotchas (KiCad 10.0.1)
- **Load boards from inside the project directory.** Zone fill and netclass lookup need the
  `.kicad_pro` and `.kicad_dru` next to the board. A board loaded from elsewhere fills GND right up
  to the HV copper with default clearances and reports every net as `Default`.
- `GetEffectiveNetClass()` returns an unwrapped SWIG object. Use `GetNetClassName()`, which can be
  a composite such as `"HV_5kV,Default"`; take the strictest member.
- `Board.Remove(item)` can break SWIG typing for later `GetTracks()` / `GetFootprints()` calls
  (symptom: "memory leak of type 'PCB_TRACK *'", then `SwigPyObject` has no attribute ...). Collect
  UUIDs read-only and delete the `(segment ...)` blocks from the file text instead.
- `pcbnew.FromMM()` rejects numpy floats; cast with `float()`.
- The board file is CRLF on Windows. Text edits must preserve the newline style.
- After any change that touches GND copper, check that GND is one connected network
  (`kicad-cli pcb drc` reports 0 unconnected items). Pour islands are kept when they hold a pad,
  so a cut-off island shows up only as an unconnected zone-to-zone item.

## Footprint save to a project `.pretty`
Use the IO manager. KiCad 10 renamed `PluginFind` (9.0) to `FindPlugin`:

    import pcbnew
    io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    io.FootprintSave(pretty_dir, footprint)

`tools/MakeLeadPair.py` is a working example. Library nickname for the project footprints is
`HV_Footprints` (it points at `HV_Pi_Hat.pretty`); there is no `HV_Pi_Hat` nickname.

## Rev B build (HAT+ outline)
    "/c/Program Files/KiCad/10.0/bin/python.exe" tools/revb/BuildRevB.py
    "/c/Program Files/KiCad/10.0/bin/python.exe" tools/revb/AutoRoute.py "HV Pi Hat.kicad_pcb" 2.0
BuildRevB rewrites the board in place with the placement in `tools/revb/RevBLayout.py` (it strips and
rebuilds, so it runs on rev A or on an existing rev B);
AutoRoute routes it (HV first, LV kept out of the pot) and pours GND. Then run DRC with
`--schematic-parity`, `tools/HvInterlayer.py` and `tools/PotMargin.py`.

## Pot margin
    "/c/Program Files/KiCad/10.0/bin/python.exe" tools/PotMargin.py "HV Pi Hat.kicad_pcb"
Smallest distance from HV copper to the pot edge (the `PotVoid_In1.Cu` rule area); ADR-0003 wants 3 mm.

## Limitations (drives who-does-what)
- **No schematic Python API**, so schematic edits are eeschema **GUI** (or risky text surgery).
- **"Update PCB from Schematic"** (forward annotation) is GUI-only, not in kicad-cli.
- The **PCB is fully scriptable** via `pcbnew` (placement, tracks, zones, footprints).
- Freerouting does not handle the HV zone (about 4 minutes per pass, no clean result). HV was
  routed by script.
