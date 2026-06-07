# Status — HV Pi Hat  (updated 2026-06-05)

**Current focus:** control-circuit rework in eeschema (Task #4), then PCB layout.

## Done
- ✅ **HV clearance strategy** locked + enforced — `HV Pi Hat.kicad_dru` (4 mm clearance, creepage, edge on `HV_5kV`/`HV_Return`); conformal-coat baseline, pot in reserve.
- ✅ **Libraries self-contained**: `HV_Pi_Hat.pretty` (8 footprints) + `HV_Electronics.kicad_sym` + `MHR0317SA107F70.kicad_sym`; `fp-lib-table`/`sym-lib-table` relinked via `${KIPRJMOD}`. 0 library errors.
- ✅ **R1/R2 → 100 MΩ** (label fix; the `…107…` part is 100 MΩ).
- ✅ **Datasheets** in `datasheets/` + index.
- ✅ **Design review** (`REVIEW_FINDINGS.md`) → corrected design (`CONTROL_DESIGN.md`), now with **active charge + discharge** (2 optos/channel).

## In progress — user, in eeschema (see `EESCHEMA_TODO.md`)
- Phase 0 checkpoint ✅ · Phase 1 (U1: ILIMIT→5 V, PGM op-amp ×1.55, input caps/ferrite) ✅ · Phase 2 (Ch1 charge→parallel) ⏳ partial.
- Confirmed present in the saved `.sch`: `MCP6001-OT` op-amp, decoupling caps, ferrite bead.

## Next
1. **(user)** Finish `EESCHEMA_TODO.md` Phases 2–8 → run **ERC** → ping.
2. **(Claude)** Re-verify the `.sch` loads via CLI; then **Update PCB from Schematic** (GUI/guided forward-annotation).
3. **(Claude)** **PCB layout**: place per zoning (LV under header, HV at output edge), add milled slots (moat + inter-channel + between terminal pads), In1/In2 HV keepouts, route, drive DRC → 0.
4. **(deferred)** Spec the 2-pos HV terminal block for J3/J4.

## Watch-outs / open
- kicad-cli couldn't load the `.sch` at last check (open in eeschema / OneDrive sync). Re-verify when closed.
- Confirm the ferrite symbol is `Device:Ferrite_Bead` (a `Device:FerriteBead` id appears in the cache).
- HV-zone part count ~doubles (2→4 optos + more HV resistors) → layout will be tighter (right third is empty, so OK).

## Task IDs (this session)
1 ✅ libraries · 2 ⬜ reconcile sch↔pcb (blocked by #4) · 3 ✅ datasheets · 4 ⏳ control rework
