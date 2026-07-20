# Status — HV Pi Hat  (updated 2026-06-08)

**Toolchain note:** project is now **KiCad 10.0.1** (schematic is v10 format). Use the v10 CLI
`/c/Program Files/KiCad/10.0/bin/kicad-cli.exe` and v10 `python.exe` (pcbnew). The v9 CLI can't load
the v10 `.sch`. **DRC must be run via `kicad-cli pcb drc`** — `pcbnew.WriteDRCReport` asserts
("process failed") without the full app context.

**Current focus:** **Decision A1 - electrically complete & DRC-clean on all HV/GND.** HV is routed 100%
on the OUTER layers with the inner layers voided beneath it, LV re-routed around the voids, floating
mounting-hole pads removed, thick-stackup spec defined, and the bottom-right cluster refined (resistor
spread) so HV/GND clear at 2 mm. One **mechanical** review item remains (R26 body near H4 screw).
Full detail in `AUTONOMOUS_BUILD_LOG.md` (sections 'Decision A1 - execution' + 'placement refinement RESOLVED').
Renders: `docs/A1_final_top.png`, `docs/A1_final_bottom.png`.

## Decision A1 - status snapshot (2026-06-08, refined)
- DONE Inner-layer voids (In1/In2 keepouts) over the HV zone - **0 HV copper on inner layers** (audited F:15/B:19).
- DONE All 5 HV nets on **F/B outer only**, 0.25 mm, **0 HV creepage/clearance/short/crossing**, all connected.
- DONE LV nets displaced by the voids (+5V, VIN, GPIO_16, GPIO_26) re-routed through the empty B top channel.
- DONE **HV-zone placement refinement** (replace_A1.py): resistors spread into two channel-pairs with a 7 mm
  gap -> CH1 reaches J3.2 from the east (no J3.1 GND wall), GND gets a routable path.
- DONE GND connected (U1.9->OR3.4, bleeder R25.2->J4.1 stitched); only a floating corner pour sliver left (cosmetic).
- DONE H1-H4 floating 5.4 mm copper pads removed; custom JLCPCB thick stackup (2.0-2.4 mm, >=0.5 mm F/In1, In2/B) + conformal coat -> 2 mm creepage.
- TODO **For the mandatory 5 kV EE review:** (1) **mechanical** - R26's 18 mm body sits ~1 mm from H4's M2.5
  screw (copper clearances OK; verify standoff/flat-screw or shorter R26); (2) GPIO_12_Boost unrouted
  (*pre-existing*, saturated U2 cluster); (3) cosmetic silkscreen + corner sliver + Q1/Q3 thermal relief;
  (4) standard sign-off (stackup order, coating, as-built creepage, BOM HV ratings).

## Done
- ✅ **Schematic complete & verified** (autonomous pass, 2026-06-07). Netlist **exactly matches** the
  corrected `CONTROL_DESIGN.md` (30/30 nets, machine-checked); **ERC 0 errors**. Implements: PGM
  op-amp stage (gain ≈1.56, true ceiling ~4.68 kV from a 3.3 V PWM, C1 on the +IN node), ILIMIT→5 V,
  input ferrite+bulk, **2 channels × (charge opto + active-discharge opto)**, fixed indicator branch
  (→ MOSFET drain, 470 Ω), bleeders re-legged across the output, **1 GΩ safety bleeders POPULATED**
  (fail-safe, default-on per design intent — see F-9), GPIO map off ID_SC (PGM=12, Ch1 chg/dis = 5/6,
  Ch2 chg/dis = 26/16), corrected custom-symbol pin types, PWR_FLAGs.
- ✅ **HV clearance strategy** locked + enforced — `HV Pi Hat.kicad_dru` (4 mm). HV nets `/HV_*` →
  **HV_5kV** netclass via a `.kicad_pro` pattern.
- ✅ **Libraries self-contained** + **all footprints assigned & verified to load** (fixed a missing
  LED footprint; assigned 0603/1206 to previously-unfootprinted passives).
- ✅ **PCB regenerated from the netlist** (`pcbnew` forward-annotation) — **0 parity errors**
  (6 benign warnings: 4 mounting-holes-not-in-schematic + 2 op-amp SPICE-field — standard on any
  board); organized placement; F.Cu+B.Cu **GND guard pours** (4 mm HV moat).
- ✅ **Sourced BOM** — `docs/BOM_SOURCED.md` (DigiKey/Mouser, in-stock); `fab/BOM.csv`.
- ✅ Independent design review of the netlist (PASS 9/10 → indicator fix applied).

## PCB fit + clean placement — DONE 2026-06-07 (compact opto footprint)
The active-discharge design now **fits 85×56** after redesigning the opto footprint: the OPTO-100-05
HV pins are flexible **wire leads** (not rigid pins), so they were pulled in next to the ~10 mm body
(`HVM OR-100.kicad_mod`; courtyard 25→11 mm; original kept as `*_ORIGINAL_25mm.bak`).
**Placement is now 100 % DRC-clean at the full 4 mm HV spacing: 0 violations** — 0 courtyard
overlaps, 0 off-board parts, 0 shorts, 0 creepage — and **parity 0**. Layout: GPIO header top, LV
drivers + op-amp + filter left, 2×2 compact-opto grid center, SMHV module right, HV-output resistors
(R_dis + safety) and terminals split around the bottom-right mounting hole, F.Cu/B.Cu GND guard
pours, Pi-IO keep-out marked. (Cleanup pass also removed 32 stray leftover Edge.Cuts slot segments.)
**Only remaining step: routing** (56 unconnected nets). Freerouting struggles with the dense HV zone
(~4 min/pass single-thread); best finished in pcbnew now that the placement is clean, or with more
autorouter tuning. HV netclass at 4 mm (safety).
Standoffs: **≥20 mm** + tall GPIO header (clears the Pi 5 USB-A/RJ45/cooler under the right ~13 mm).

## Connector — RESOLVED (2026-06-07)
J3/J4 → generic **1×2 screw terminal, 10.16 mm pitch** (`TerminalBlock_RND_205-00241`; pad1=HV−/GND,
pad2=HV+). 10.16 mm gives real 5 kV creepage margin and is pitch-compatible with the recommended
**Phoenix MKDS 10 HV (1709681)**. Alternatives (incl. direct-soldered HV silicone lead — the
smallest/cheapest/most-reliable 5 kV termination) in `docs/HV_CONNECTOR_OPTIONS.md`.

## Open decision — HV density vs. the locked 4 mm rule (needs EE sign-off)
Even with small terminals, the HV section (**4× 25 mm optos + 4× 19 mm MHR resistors + module +
2 terminals**) is over-constrained at 4 mm on 85×56 mm with two corner mounting holes. ~33 residual
DRC violations, all HV-zone spacing. Also: the milled-slot creepage trick **conflicts with the
"HV-to-edge 4 mm" rule** (KiCad treats slot edges as board edges). Pick ONE: **(a)** relax the HV
*air*-clearance + slot-edge rules to ~2 mm, keep CREEPAGE 4 mm, add slots (consistent with the coated
5 kV reasoning — 4 mm is ~2.4× the real ~1.7 mm air breakdown; *EE approves*); **(b)** smaller HV
resistors (2512 5 kV chip instead of 19 mm MHR0317) to free the zone; or **(c)** enlarge the board.

## Next
1. **(user/EE)** Decide (a)/(b)/(c) above.
2. **(then)** Finalize HV placement → route (LV routable now; freerouting path set up) → DRC → 0 →
   gerbers/drill/pos.
3. ⚠️ **Human-EE review of the schematic + HV layout before fabricating/energizing** (5 kV board).

## ⚠️ Safety
This pass verified **connectivity + spacing rules** with KiCad's own tools — not physical safety.
A qualified human must review before this board is built or powered. See the standing caveat at the
top of `AUTONOMOUS_BUILD_LOG.md`.

## Task IDs (autonomous session 2026-06-07)
1 ✅ netlist tool · 2 ✅ target spec+review · 3 ✅ schematic edits (30/30, ERC 0) · 4 ✅ PCB forward-annot
· 5 ⏳ PCB layout (placed+poured; routing blocked by connector decision) · 6 ⏳ fab/docs · 7 ✅ sourced BOM
· 8 ✅ footprints
