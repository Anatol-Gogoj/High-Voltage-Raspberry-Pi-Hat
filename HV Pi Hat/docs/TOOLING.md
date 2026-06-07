# Tooling — HV Pi Hat

- **kicad-cli:** `/c/Program Files/KiCad/9.0/bin/kicad-cli.exe`
- **KiCad Python (has `pcbnew`):** `/c/Program Files/KiCad/9.0/bin/python.exe`
- Run commands from the project dir (parent of `docs/`); files: `HV Pi Hat.kicad_pcb` / `.kicad_sch`.

## DRC (honors the custom HV rules in `HV Pi Hat.kicad_dru`)
    kicad-cli pcb drc --format json --severity-all --schematic-parity \
      --output drc.json "HV Pi Hat.kicad_pcb"
Expect these violation types from our rules on HV nets: `clearance`, `creepage`, `copper_edge_clearance`.

## Render (top-view PNG)
    kicad-cli pcb render --side top --quality high -o render_top.png "HV Pi Hat.kicad_pcb"

## Netlist (read connectivity without the GUI)
    kicad-cli sch export netlist -o net.net "HV Pi Hat.kicad_sch"
Fails to load while the `.sch` is open in eeschema / mid-OneDrive-sync — close eeschema first.

## Footprint extraction to a project `.pretty` (KiCad 9 API)
Legacy `pcbnew.FootprintSave` is broken in v9. Use the IO manager:

    import pcbnew
    io = pcbnew.PCB_IO_MGR.PluginFind(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    io.FootprintSave(pretty_dir, footprint)   # footprint from board.GetFootprints()

## Custom DRC rules
`HV Pi Hat.kicad_dru` is auto-loaded. HV nets = netclasses `HV_5kV` (rail + outputs) and `HV_Return`.

## Limitations (drives who-does-what)
- **No schematic Python API** → schematic edits are eeschema **GUI** (or risky text surgery).
- **"Update PCB from Schematic"** (forward annotation) is GUI-only — not in kicad-cli.
- The **PCB is fully scriptable** via `pcbnew` (placement, tracks, zones, footprints) — see footprint extraction above.
