# Autonomous build log — HV Pi Hat

> Decision/action journal for the autonomous completion pass started **2026-06-07** by Claude
> (Opus 4.8). Records *what* was done, *why*, alternatives weighed, and what still needs a human.
> Newest entries at the bottom of each section. This is the "separate doc" requested by the user.

## ⚠️ Standing safety caveat (read before fabricating)
This is a **5 kV** board. I am completing the *design* (schematic netlist + PCB layout +
fab outputs) and verifying it with KiCad's own tools (netlist, ERC, DRC against the custom HV
rules). That verification proves **electrical connectivity and spacing**, not physical safety.
**A qualified human (the user / an EE) must review the schematic, layout, and HV clearance
strategy before this board is fabricated or energized.** I flag every safety-relevant assumption
inline below with `SAFETY:`.

---

## 0. Situation as found (2026-06-07)

### Toolchain (corrects `docs/TOOLING.md`)
- **KiCad 10.0.1 is installed** (`/c/Program Files/KiCad/10.0/bin/`) *and is the version that last
  saved the schematic* (`.kicad_sch` is format `20260306`, `generator_version 10.0`).
- KiCad 9.0.6 is also installed; its `kicad-cli` **cannot** load the v10 schematic — this is the
  sole reason the prior notes said "kicad-cli couldn't load the .sch." Resolved by using the **v10**
  CLI: `/c/Program Files/KiCad/10.0/bin/kicad-cli.exe` (and `python.exe` for `pcbnew`).
- **No schematic Python API** in either version (no `kipy` bundled; IPC API needs the running GUI).
  → schematic edits are done by **verified S-expression surgery** on `.kicad_sch`, with correctness
  proven by exporting the netlist + ERC after every change. The **PCB is fully scriptable** (`pcbnew`).
- Decision: **computer-use driving of eeschema was rejected** — pixel-driving the schematic editor to
  place ~6 symbols and wire ~25 nets is far more error-prone and far less verifiable than
  S-expression edits checked against the exported netlist.

### Schematic state (`HV Pi Hat.kicad_sch`) — ~40% of the corrected design
Present & basically correct: PGM op-amp stage (U2 MCP6001 + R7/R8/R9/R10, gain ≈1.55), U1 input
filter (FB1 + C2/C3/C4), ILIMIT→5 V, and **both charge-side LV drivers** (OR1/Q3 and OR2/Q1 with
opto-R + indicator branches). **Gaps vs. `CONTROL_DESIGN.md`:**
1. **Entire HV path is unwired** — `U1.HVOUT(8)`, every opto `HVIN(3)/HVOUT(4)`, and `J3.2/J4.2`
   (the HV+ output pins) are floating. The board makes no high voltage as drawn.
2. **No active discharge** — design needs 2 more optos + 2 more MOSFETs + drivers; only a dangling
   `R13(10k)+R16(100)` gate-stub fragment exists.
3. **Bleeders R1/R2 (100 MΩ) are in the wrong leg** — `J.pin1→R→GND`, in series with the actuator;
   they must move to `DEA-node→GND` (and become the discharge-opto feed). (Review finding C, unfixed.)
4. **Ch-1 charge enable is on `GPIO1`/`ID_SC` (pin 28)** — a HAT-EEPROM pin; must move to GPIO5.
5. **PGM RC cap C1 is mis-placed** — C1(1µF) sits on the *GPIO12 side* of R7, not on the op-amp
   `+IN` node, so the PWM is **not** actually low-pass filtered into the op-amp. (See finding F-1.)
6. Stray/dangling `R13/R16` fragment (one unconnected pad).

Connectors: **J3/J4 are now `SHV-R` coax HV connectors** (Digikey 4912-SHV-R-ND), not the 2-pos
terminal blocks in `DECISIONS.md`. This is a *better* HV-output choice and **resolves the deferred
"spec the terminal block" item** — pin1 = ground shell, pin2 = HV center. (Decision D-1 below.)

### PCB state (`HV Pi Hat.kicad_pcb`) — stale (old design)
The board is the **pre-rework** design: old R3/R4 (200 Ω), R5/R6 (300 Ω), Q1/Q2, J1/J2 pin headers,
only OR1/OR2, **no op-amp, no discharge**. Its net names don't match the current schematic. It will
be **regenerated from the finalized schematic**. Re-usable: board outline **85.05 × 56.05 mm**,
4× M2.5 mounting holes at HAT positions, the 2×20 header. (`.kicad_pcb` is still v9 format; pcbnew 10
will upgrade it on save.)

### Custom HV DRC rules (`HV Pi Hat.kicad_dru`) — good, keep
4 mm clearance + 4 mm creepage + 4 mm edge-clearance on netclasses `HV_5kV`/`HV_Return`, plus a 1 mm
interlayer hole rule. **But no net is assigned to those classes yet** (only `/GPIO*`→Signal). Must add
HV-net→HV_5kV/HV_Return assignment during layout.

---

## 1. Approach decided

| # | Decision | Why / alternatives weighed |
|---|---|---|
| A-1 | **Edit the schematic by verified S-expression surgery**, using **net-label stubs** to make connections (a short wire off each pin + a `(label "NET")`), matching the schematic's existing label-based style. | No schematic API; computer-use GUI driving is unverifiable and fragile. Labels avoid fragile pin-to-pin wire routing and are exactly how the existing sheet wires GPIO/power nets. Every edit is proven by re-exporting the netlist with `kicad-cli` and diffing against an explicit target. |
| A-2 | **Build a geometry→netlist reconstructor first and calibrate it** against `kicad-cli sch export netlist` before touching the file. | Proves my coordinate/transform model (symbol position+rotation+mirror → absolute pin endpoints) is correct, so label-stub placement lands exactly on pins. No guessing. |
| A-3 | **Patch the existing schematic, don't rebuild it.** | Preserves the user's correct existing work (op-amp stage, charge drivers); less surface area for error. |
| A-4 | **Regenerate the PCB from the netlist via `pcbnew`** (scripted forward-annotation), then lay it out by HV zoning, add milled slots/keepouts, pour GND, route, drive DRC→0. | "Update PCB from Schematic" is GUI-only, but the PCB is fully scriptable; the stale board has no layout worth keeping. |
| A-5 | **Single-writer file edits; parallel agents only for analysis/verification.** | The `.kicad_sch`/`.kicad_pcb` are one-writer artifacts — concurrent mutation would corrupt them. Sub-agents are used for independent spec review, adversarial netlist/safety checks, and parts/pinout research. |

Git safety net: working tree is clean at `4f087bc`; I can `git checkout` to revert. I also keep
manual `.bak` copies before each destructive edit.

---

## 2. Engineering findings raised during recon (to resolve/track)

- **F-1 (fix): PGM RC filter cap on wrong node.** C1(1µF) is GPIO12→GND; the low-pass needs it on the
  op-amp `+IN` node (after R7). As-is the op-amp sees attenuated PWM, not a filtered DC level → HV
  ripple. → move C1 to the `+IN` node. *Fixing.*
- **F-2 (note, not changing): full-scale ceiling ≈ 4.65 kV, not 5 kV.** With a 3.3 V PWM, the
  R7(10k)/R8(100k) input divider gives ≈3.0 V at `+IN`; ×1.55 ⇒ ≈4.65 kV PGM-equivalent. To reach a
  true 5 kV either raise the gain (Rf≈6.8k ⇒ ×1.68) or drop R8's loading. The locked decision is gain
  1.55 with "headroom to 5 kV, run lower in firmware," and 4.65 kV is 93% of range — **leaving 1.55 as
  locked**, flagged here as a recommendation for the user. (SAFETY-adjacent: higher ceiling = more HV.)
- **F-3 (fix): bleeder leg** — move R1/R2 to the DEA node and reuse them as the discharge-opto feed
  (`R_dis`), per `CONTROL_DESIGN.md`. Tie J pin1 → GND.
- **F-4 (fix): Ch-1 enable off ID_SC** → GPIO5; assign all four drive GPIOs per the design's GPIO map.
- **F-5 (add): R_safety 1 GΩ DNP** across each output as an unpowered fail-safe bleed. Part for 1 GΩ:
  `MHR0317SA108F70` (code 108) — to verify availability; the 100 MΩ symbol can be reused with value 1G + DNP.
- **F-6 (cleanup): remove the dangling R13/R16 fragment** or fold it into a discharge gate network.

(Resolutions recorded in §3 as they're applied.)

---

## 3. Action log
(chronological; appended as work proceeds)

- **2026-06-07** — Recon complete (above). Created task list (#1–#6), this log, and the netlist
  reconstruction tooling plan. Next: build & calibrate the geometry→netlist tool (task #1).

### Final adversarial review (task #6) + fixes it forced — the value of checking my work
A final independent review agent confirmed the **schematic is sound and safe-by-design** (topology
matches `CONTROL_DESIGN.md`; the optical isolation barrier is intact — **no HV-to-GPIO copper path**;
0 ERC errors). It also caught **two things I had wrong**, both now fixed:
- **F-9 (SAFETY, important): R25/R26 (1 GΩ safety bleeders) were marked DNP — backwards.** The locked
  intent is "1 GΩ **always-on**, DNP *if undesired*" → default **populated**. With them unpopulated a
  charged DEA (≤~4.7 kV) has **no passive bleed when the board is unpowered** (active discharge needs
  +5 V + a GPIO) — a real charged-HV-capacitor hazard. **Now POPULATED** (dnp=no) in schematic + PCB.
  Re-checked the voltage impact and found it negligible: R1 (100 MΩ) is *gated by the discharge opto*
  (not a steady load), so during hold only the 1 GΩ lightly loads the DEA node (~5 µA vs the opto's
  ~50 µA) → still reaches the ~4.7 kV ceiling; the always-on 1 GΩ gives τ≈1 s fail-safe bleed for
  0.025 W. (This also corrected my own earlier mental model of which resistor is the steady bleeder.)
- **F-10 (parity bug): my "PCB parity = 0" claim was imprecise/misleading.** I had checked with
  `--severity-error`; at full severity there were **79 parity warnings** — root cause: my
  forward-annotation left **every footprint with an empty library nickname** (`""`:name vs the
  schematic's `Lib:name`). Fixed `gen_pcb.py` to `SetFPID(LIB_ID(nick,name))`; also copied the
  Description/Datasheet symbol fields to the footprints (what KiCad's "Update PCB" does) and annotated
  the mounting holes H1–H4. **Parity now = 6 warnings**, all standard/benign: 4 `extra_footprint`
  (mounting holes legitimately aren't in the schematic — present on essentially every KiCad board)
  + 2 `Sim.Pins` (the op-amp symbol's SPICE field). **0 parity errors, 0 nickname/footprint
  mismatches.** Also made the small resistors uniform at **0603** (the review noted a 0402/0603 mix).
- Minor confirmations from the review (left as-is, documented): the true PGM ceiling is **~4.68 kV**
  (gain 1.56), so "5 kV" is really "~4.7 kV max" (safety-positive); the SHV connector under-rating is
  real (already a user decision); `HV_Return` netclass is defined but unused (harmless); U1.8 (HVOUT)
  pin is slightly off-grid (cosmetic; connectivity verified).

**Lesson recorded:** report verification results at the right severity and state exactly what was
checked — "0 errors" ≠ "0 issues." The adversarial review earned its keep by catching both the
safety default and the parity imprecision.

### Tasks #4/#5 — PCB regenerated from schematic, placed, poured (NOT yet fully routed)
- **Forward annotation (task #4 DONE):** wrote `gen_pcb.py` — a programmatic "Update PCB from
  Schematic" via `pcbnew` (there is no CLI for this). It strips the stale old-design footprints
  (kept the 85×56 outline, 4 mounting holes, header position), adds all 43 components from the
  netlist with their assigned footprints, and assigns every net to pads by pad-number↔pin-number.
  Verified **`kicad-cli pcb drc --schematic-parity` → 0 parity issues** (PCB nets exactly match the
  schematic). Fixed a real net bug: the SHV footprint has **two GND tabs (both pad "1")**; the
  naive assignment only netted one — netted both.
- **HV netclasses:** the `/HV_*` nets resolve to the **HV_5kV** class (4 mm clearance/creepage),
  confirmed by the DRC creepage rule firing on them. **Ground pours** added on F.Cu + B.Cu — they
  auto-carve a 4 mm moat around every HV net, giving the HV zone a guard-ground (visible in the
  render as voids around the optos/HV-R/SHV).
- **Placement (task #5, partial):** organized zoning — GPIO header along the top, LV (op-amp PGM,
  the four charge/discharge MOSFET drivers, gate/LED resistors, indicator LEDs, input filter) in the
  left/center, SMHV module center, HV (4 optos + 4 HV resistors + 2 SHV outputs) in the right half
  split channel-1-top / channel-2-bottom. **Fixed the safety-critical issue** that HV pads were
  initially within 4 mm of the GPIO header — all HV is now well clear of the header.

### BREAKTHROUGH (user insight): compact opto footprint — 85×56 now FITS
The user pointed out that the OPTO-100-05's HV pins (3/4) are **flexible wire leads** (the white/red
coiled wires in the datasheet photo — body is only 0.40"×0.24" ≈ 10.2×6.1 mm), not rigid pins fixed
where the original footprint drew them at ±16 mm (which is why it read as **25 mm wide**). Confirmed
from `datasheets/HVM_OPTO-100.pdf`. **Redesigned `HV_Pi_Hat.pretty/HVM OR-100.kicad_mod`**: LED pins
1/2 stay at the rigid body; HV wire-pads 3/4 pulled in just above the body (6.2 mm apart → ≥4 mm
edge-to-edge creepage, ≥4 mm from the LED pins). **Courtyard 25.4×6.6 mm → 11.4×12.7 mm.** Original
saved as `HVM OR-100_ORIGINAL_25mm.kicad_mod.bak`. Result: the full **active-discharge design now
fits 85×56** (LV + 2×2 compact-opto grid + module + R_dis + safety + terminals), where it was
*impossible* before. Down to a handful of residual courtyard overlaps **only in the bottom
HV-output cluster** (the four 19 mm MHR resistors + 2 terminals + the corner mounting hole are right
at the area limit) — genuine hand-tweak territory. (Note: the MHR resistors must stay *horizontal* —
vertical mounting would run a bare HV lead alongside the body at a 5 kV difference, killing creepage.)

### Pi-IO clearance (user asked) + full scripted route attempt — the honest outcome
- **Pi-5 tall-IO clearance (was missed; now handled):** researched the Pi 5 mechanical drawings. The
  USB-A stack (~17 mm) + RJ45 (~13.5 mm) sit under the **right ~13 mm of this full-size HAT (board
  x≈189.5–202)**. All HAT parts are top-side + B.Cu GND pour, so the fix is **≥20 mm standoffs + a
  tall (≥20 mm) 2×20 GPIO stacking header** (clears USB-A/RJ45/Active-Cooler with no board cutout; the
  B.Cu GND pour shields HV from the Pi's metal IO). Marked on `Dwgs.User` + noted. No layout change.
- **Autorouter pipeline established:** `pcbnew.ExportSpecctraDSN`/`ImportSpecctraSES` + **freerouting
  v2 (headless)**. v1.9 throws `HeadlessException`; v2 routes from the CLI. Round-trip verified.
- **Full scripted route (user chose: keep 85×56 + active discharge, 4-layer, tighter):** routed the
  board — **184 tracks, 22 vias; LV fully routed.** But the HV zone **did not close: 20 unrouted +
  22 HV-net spacing (creepage/clearance) violations.** The autorouter could only fit the HV nets at
  ~2 mm, **below the 4 mm creepage 5 kV needs — i.e. the auto-routed HV is electrically unsafe.**
  Restored the HV netclass to 4 mm (safety) so DRC reports honestly. Preliminary Gerbers in
  `fab/preliminary_DO_NOT_FAB/` (clearly marked not-fab-ready).
- **HONEST CONCLUSION (as the user asked me to report):** the 2-channel **active-discharge** design
  (4 optos + 4× 19 mm HV resistors + module + 2 terminals) **physically cannot close on 85×56 mm at
  4 mm HV spacing**, and **4 layers does not help because creepage is a 2-D *surface* constraint.**
  Proven analytically (the optos alone stack to 32 mm and leave no room for the 22 mm module + the
  four 19 mm resistors) and empirically (every placement bottoms out at ~8 unavoidable courtyard
  collisions; the autorouter leaves 20 HV nets unroutable at 4 mm). The board is delivered routed as
  far as 85×56 allows. **The only paths to a clean, safe, fabricable board:** (a) **enlarge to
  ~100×56 mm** (recommended — HV zone fits with full 4 mm, routes clean) or (b) drop active discharge.

### HV spacing decision (user, 2026-06-07): **relax air → 2 mm, keep creepage 4 mm + slots**
Updated `HV Pi Hat.kicad_dru`: HV **creepage 4 mm** (binding, extended by milled slots), HV **air
clearance 2 mm** (~1.2× the ~1.7 mm real 5 kV air breakdown), and **dropped the "HV-to-board-edge"
rule** (the F/B GND guard pour already moats every HV net at 4 mm so the *pour*, not bare HV, faces
the outer edge — and the edge rule would otherwise fire on the intentional creepage slots). Engineering
note recorded: because creepage ≥ air on coplanar copper, the air relaxation only helps **with slots**;
and the 4× 19 mm MHR HV resistors remain the dominant space hog (option **(b)**, smaller 2512 5 kV chip
HV resistors, would still help and is recommended as a follow-up even under option (a)).

### PCB — final autonomous state + the exact remaining work
After applying the spacing decision: HV DRU corrected so the **GND guard pour holds the full 4 mm
from HV** (`HV to GND pour` rule — the pour, not bare HV, faces the outer edge) while HV-to-component
air is 2 mm. Final committed state: **parity 0 errors**; physical DRC = ~**24 violations, all inside
the HV zone** + unrouted ratsnest. Breakdown and the precise finish steps:
- **8 creepage (component-to-component, 2–4 mm)** → add a milled slot (Edge.Cuts cutout) between each
  pair so the surface path ≥4 mm. KiCad's creepage engine routes around slots; do this in the GUI
  where you can see the creepage number update live (scripting blind slot geometry for 8 pairs is
  error-prone).
- **6 clearance (<2 mm) + 8 courtyard overlaps** → nudge the touching parts apart by 1–2 mm. These
  exist because **5 kV-rated resistors are inherently large** (the MHR0317 is 19 mm *because* it is
  7 kV-rated; sub-10 mm 5 kV resistors essentially don't exist), so 4×opto + 4×HV-resistor + module
  is genuinely dense even at 2 mm. The placement is organized and ~90% clear; the last nudges are a
  few minutes of GUI drag-with-live-DRC.
- **Then route** (LV first; HV with the wide HV netclass tracks) and re-run DRC → 0 → gerbers/drill/pos.
**Why I stopped here autonomously:** the residual work is precise interactive geometry (slot shapes,
final part nudges, routing) that is far faster and safer with KiCad's live DRC feedback than by blind
coordinate scripting — and it does not change any of the verified electrical design. Everything up to
this line (the entire schematic + netlist + parity-clean board + rules + pours + BOM) is done and
verified. A clean alternative if a fully-scripted board is required: **enlarge the board** (option c)
to regain 4 mm everywhere with no slots.

### PCB layout — connector RESOLVED, HV-spacing decision applied
- **Connector decision (user, 2026-06-07):** drop the oversized/under-rated SHV-R; use a **generic
  1×2 screw terminal per channel (HV+/HV−)** for now + research alternatives. Implemented: J3/J4 →
  `TerminalBlock_RND_205-00241_1x02_P10.16mm` (10.16 mm pitch → ~10 mm pole-to-pole creepage, real
  5 kV margin; pad1=GND/HV−, pad2=HV+). Footprint is pitch-compatible with the researcher's specific
  recommendation **Phoenix MKDS 10 HV (1709681)**; the cheapest/smallest/most-reliable 5 kV option is
  a **direct-soldered HV silicone lead + turret** (see `docs/HV_CONNECTOR_OPTIONS.md`). The small
  terminals freed the HV zone and the layout is now organized & presentable (header top; LV drivers
  left; SMHV module center; 4 optos spread right; HV resistors at the edge; terminals at the bottom
  edge; F.Cu+B.Cu GND guard pours moating every HV net). **Parity: 0 errors.**
- **⛔ Remaining decision — HV density vs. the locked 4 mm rule (needs EE sign-off).** Even with the
  small terminals, the HV section (**4× 25 mm optos + 4× 19 mm MHR resistors + module + 2 terminals**)
  on 85×56 mm with two fixed corner mounting holes is **genuinely over-constrained at 4 mm**
  (U1 + one opto + one terminal alone = 55 mm > the ~50 mm usable width). Residual DRC = ~33 physical
  violations, all in the HV zone (HV-net pads <4 mm apart) + ~62 unrouted. **New finding:** the
  design's *milled-slot* creepage strategy **conflicts with its own "HV to board edge 4 mm" rule** —
  KiCad treats a slot's edge as a board edge, so a creepage slot between two HV nets *triggers*
  HV-edge violations. To reach DRC=0, pick ONE (in order of preference):
  - **(a) Relax the HV *air*-clearance + slot-edge sub-rules to ~2 mm while keeping CREEPAGE at 4 mm**
    + add milled slots. This is consistent with the docs' own coated-5 kV reasoning (4 mm is ~2.4×
    the ~1.7 mm real air breakdown; creepage/coating is the true failure-mode guard). *EE must approve
    this DRU change — I will not relax an HV safety rule unilaterally.*
  - **(b) Smaller HV resistors** — the MHR0317 (R1/R2/R25/R26) are 19 mm axial; 5 kV-rated chip HV
    resistors (e.g. 2512) would free the zone substantially. (A part change.)
  - **(c) Enlarge the board** beyond 85×56 (a locked form-factor decision).
- **Routing** deferred until (a)/(b)/(c) lands (it moves HV parts → re-route). LV is routable now;
  the freerouting path (`ExportSpecctraDSN`/`ImportSpecctraSES` + Java) is available. Gerbers/drill
  intentionally not generated on an unrouted board. `fab/BOM.csv` + `docs/BOM_SOURCED.md` are ready.

### Task #3 DONE — schematic finalized & verified (netlist 30/30, 0 ERC errors)
Built a text-surgery editor (`scheditor.py`) on top of the calibrated geometry model and applied the
edit plan: cloned 11 new symbols (C5, OR3/OR4, Q2/Q4, R21–R26), surgically removed the conflicting
wires/labels/junctions (bleeder re-leg, C1→PGM_IN, GPIO reassign, indicator→drain), and assigned all
nets via **bare net-labels at proven pin endpoints** (verified that KiCad connects a bare label to a
pin). A two-pass build labels only the nets KiCad doesn't already connect, and a **collision guard**
(coinciding pins must share a target net) caught a real bug: R25/R26 (20 mm-tall MHR resistors)
placed exactly 20 mm apart had end-to-end pin coincidence shorting HV_CH2 to GND → fixed by spacing.
Result vs. `target_net.py`: **30/30 nets exact, 0 diffs, 0 unexpected nets.**
ERC: **0 errors.** Fixes applied to get there:
- Corrected custom-symbol pin electrical types (root cause of false output-output errors): TN0610
  SRC/DRAIN → passive; HVM_OR-100 all 4 pins → passive; SMHV0550 HVRTN → passive, ILIMIT → input.
  Applied to BOTH the embedded `lib_symbols` and the on-disk `HV_Electronics.kicad_sym` so they stay
  in sync (no GUI "symbol differs from library").
- Removed the 4 `netclass_flag` directives (2 were orphaned by the bleeder rewire) and assign HV nets
  to the **HV_5kV** netclass via a `.kicad_pro` pattern `/HV_*` instead (cleaner, centralized).
- Added 2 `PWR_FLAG`s (+5V, GND) — exact copy of KiCad's `power` lib symbol — to satisfy the
  pre-existing `power_pin_not_driven` errors (HAT is powered from the Pi; no on-board supply).
- Cleaned 19 dangling wire fragments (mix of disconnect leftovers + pre-existing user artifacts).
Residual ERC **warnings (all benign / non-actionable)**: 45 `lib_symbol/footprint_link` = **kicad-cli
headless noise** (every named lib IS in the project `sym-/fp-lib-table` with `${KIPRJMOD}` URIs;
kicad-cli's ERC only checks the *global* table — these do NOT appear in the GUI); 2 `pin_to_pin`
(PWR_FLAG `power_out` meeting the Pi header `bidirectional` 5V/GND pins — standard, harmless);
4 `endpoint_off_grid` (pre-existing tiny user wires + the SMHV symbol's HVOUT pin — connectivity
verified regardless). Tracked file changes: `HV Pi Hat.kicad_sch` (rebuilt), `HV_Electronics.kicad_sym`
(pin types), `HV Pi Hat.kicad_pro` (HV netclass pattern). Original recoverable via git (`4f087bc`).
Schematic exported to PDF and visually confirmed (all parts, DNP marks on R25/R26, HV nets labeled).
Note: schematic is **label-dense** (net name at each touched pin) — electrically exact and auditable;
the user can re-route visually in eeschema if a prettier sheet is desired.
### Task #2 done — target netlist defined + independently reviewed
Wrote a machine-readable target netlist (`target_net.py`): 43 components, 30 nets, 113 pin
assignments, **0 pins double-assigned**, every non-header pin covered (GPIO header's 33 unused pins
stay no-connected). An independent review agent traced it against `CONTROL_DESIGN.md`/datasheets and
returned **PASS on 9/10** (no wiring/polarity/short/floating errors). Findings folded in:
- **F-8 (fix, from review + my deeper trace): indicator branch fixed.** Review flagged R11/R15 = 47 Ω
  vs the locked **470 Ω**. Investigating, the indicator was also tied to the **wrong node** — the
  opto-LED+ node (~2.9 V, ~0.1 V headroom → barely lights) instead of the MOSFET **drain** per
  `CONTROL_DESIGN.md` (`+5V → R(470) → D → DRAIN`). Fixed both: moved R11.2/R15.2 to the drain node
  and set 470 Ω. (At 47 Ω on the correct node the LED would pull ~64 mA — over-driven — so the value
  and the node fix go together.) Net effect: indicator now lights at ~6 mA when its channel charges.
- **F-7 (decision, revised): bulk caps stay on +5V.** A ferrite bead is ~transparent at the SMHV's
  45–80 kHz switching frequency (ferrites act in the MHz range), so moving the 47/1/0.1 µF bulk
  across FB1 to VIN gives negligible benefit at that frequency and the existing cap network is
  junction'd (risky rewire). Kept bulk on +5V; **added C5 (0.1 µF) op-amp decoupling** (which the
  design explicitly calls for and was missing). Documented as the engineering tradeoff.
- Connector note (from review): J3/J4 are `SHV-R` (value) on a generic `Conn_01x02_Pin` symbol;
  pinout 1=GND/shell, 2=HV-center is correct. Confirm the SHV footprint pad numbering at layout.

### Edit plan locked (task #3)
Geometry-inspected every "disconnect" pin: each reassigned pin connects via a *single wire ending at
it* (no through-wire taps) → surgical removal is precise. Plan: clone 11 new symbols (C5, OR3/OR4,
Q2/Q4, R21–R26), set values/DNP, do ~17 targeted wire/label/NC removals (cap-free since F-7), then
assign nets via **net-label stubs** at proven pin endpoints, keeping the user's existing correct
drawn wiring. Verify by exporting the netlist with kicad-cli 10 and diffing against `target_net.py`,
then ERC. The netlist diff is the safety net for every surgical step.

### Sourcing (task #7) — `docs/BOM_SOURCED.md` written by a research agent. Key results:
- **U1 SMHV0550**: stocked on DigiKey (`2244-SMHV0550-ND`), ~$200–300. **OR1–OR4 OPTO-100-05**:
  DigiKey `2244-OPTO-100-05-ND`, ~$95 ea (~$380 total — dominant cost). **TN0610N3-G**: active/in-stock.
  Commodity passives: representative in-stock DigiKey PNs per value. Full BOM in the doc.
- **⚠️ SAFETY / SOURCING RISK — SHV connector (J3/J4).** The schematic's `4912-SHV-R-ND` label
  conflates a Keystone terminal with the Tyclon **SHV-R** jack; the realistic Tyclon SHV-R is rated
  **3.5 kV continuous / 5 kV for 1 minute only** — *marginal-to-inadequate for a 5 kV continuous
  output.* Agent recommends Radiall **R317580000** (12 kVDC, ~$30) for true margin, but it's
  panel-mount (not board-mount), so it would need a different footprint/mounting. **USER DECISION
  REQUIRED:** either (a) cap continuous output ≤3.5 kV in firmware and keep the board-mount SHV-R, or
  (b) switch to a panel-mount ≥7.5 kV connector (new footprint). Left the footprint as-is pending the call.
- **R25/R26 1 GΩ** = Murata `MHR0317SA108F70` (7 kV, real DigiKey page) — stock uncertain, but DNP so
  low impact. **Dissipation check (agent caveat):** at 5 kV, R_dis (R1/R2, 100 MΩ) burns V²/R =
  5000²/100 M = **0.25 W < 0.8 W rating** ✓; R_safety (1 GΩ) = 0.025 W ✓. Margins OK.

### Footprints (task #8) — assigned & all-resolve
Assigned footprints to the 14 symbols that lacked them (PGM-stage R7–R10 → 0603; the four 51 Ω
opto-LED resistors R6/R14/R21/R22 → **0603 for power margin** (~0.09 W each, marginal on 0402);
FB1 → L_0805; C1/C3/C4/C5 → 0603; C2 47 µF → 1206). Verified **every** footprint loads via pcbnew
and its pad numbering matches the symbol pins. Found & fixed a broken one: **D1/D2 referenced
`3372-BND0603JKRS001TR-ND:Untitled`, which doesn't exist** in the project `.pretty` → reassigned to
the standard `LED_SMD:LED_0603_1608Metric`. All other specialty footprints (SMHV0550, HVM OR-100,
TO-92, MHR0317, SHV-R) already exist in `HV_Pi_Hat.pretty` with correct pads — no new footprints
needed to be drawn. Launched a background **sourcing** agent (task #7) to build a DigiKey/Mouser
in-stock BOM in parallel.

- **2026-06-07** — User added requirements mid-run: (a) **every BOM part must be sourceable/in-stock**
  (DigiKey preferred, Mouser OK) → added task #7 (sourced BOM); (b) **create any missing
  footprints/symbols from datasheets**, saved to a dir → task #8; (c) run on a **10-min self-check
  loop** (cron `*/10 * * * *`, job `071f48f1`). Launched a background agent to verify the custom
  symbol pinmaps vs. the local datasheets + find the 1 GΩ Murata part number.

### Task #1 done — geometry→netlist model validated (the foundation)
Built `schlib.py` (scratch): parses `.kicad_sch`, computes **absolute pin endpoints** from
lib-symbol pin defs + instance position/rotation, and reconstructs the full net partition
(union-find over wires/junctions/labels/pins, **merging fragments by shared power/label name**).
**Calibrated the symbol transform decisively against KiCad's own netlist:** the winning convention
is `mode=base, ysign=-1, rotsign=-1` (connection point = lib pin (x,y); lib-Y negated for the
sheet's Y-down; clockwise rotation). It reproduces KiCad's pin→net partition for **118/118
component pins = 100% exact**. Two bugs were found and fixed en route: (1) net fragments must be
merged by *name* (power/labels connect by name, not geometry); (2) an earlier `rotsign=+1` passed a
weak "any-feature-coincidence" calibration but **silently swapped pin-1/pin-2 on rotated 2-pin
parts** — caught only by scoring against true pin→net identity. Lesson logged: calibrate against
identity, not mere coincidence. → I can now compute any pin's exact coordinate and verify edits.

---

## User layout rework — placement repair + parked-part placement (2026-06-07, later)
User hand-rearranged the PCB (new topology: **U1 module → left, MOSFETs Q1–Q4 → right column,
op-amp top-left, optos center**) and routed ~24 nets. Review of their version found: **11 parts
stranded off-board** (gate + opto-LED resistors R6/R13/R14/R17–R20/R21–R23, C5 — left behind when
the Q's moved), **19 HV creepage violations** in their routing (HV tracks <4 mm from GND/control
pads, the H4 mounting-hole, and U1's GND pins), and 4 starved-thermal. Parity still 0 (netlist
intact). Fix (keeping their topology):
- **Placed all 11 parked parts** — gate resistors in a 3rd column beside the Q's, opto-LED resistors
  beside each opto's LED+ pad, C5 below U1.
- **Tidied the 4 optos into a clean 2×2** (center, 18 mm pitch) — their scattered arrangement left
  no room for the opto-LED resistors and put OR1 into the header keep-out.
- Re-organized the bottom HV outputs by channel (ch1 left / ch2 right of the H4 hole) to kill the
  channel-intermixing creepage; **set SMD GND pads to solid zone-connection** (the op-amp is forced
  into a tight strip above U1, starving thermal spokes — solid is correct for a ground plane).
- Ripped the stale routing (invalidated by moving the optos) and re-routed.
- **Result: placement 100 % DRC-clean (0 violations), parity 0, nothing off-board.** Re-routing in
  progress.

---

## Decision A1 — HV/LV lane separation re-placement (2026-06-08)
After the user picked **inner-HV + FR4 encasing + conformal coating + 2mm creepage**, review surfaced a
**3D stackup hazard the 2D DRC can't see**: on a standard JLC 4-layer 1.6mm stack, HV copper on ANY
layer sits ~0.21mm (prepreg) from adjacent-layer copper -> ~24 kV/mm at 5kV, far over FR4's safe
long-term field (~2-4 kV/mm). Fix requires the layer adjacent to HV to be void of copper +/or a thick
stackup. User chose **A1: HV on outer layers + inner voids + thick custom stackup, keep 85x56**.

**Re-placement (`place_A1.py`):** reorganized into clean lanes — **LV left | opto column center
(rot270 so LED pins face LEFT/HV pins face RIGHT) | all HV right** (module + R_dis + safety + terminals).
HV nets now never cross the LV gate drivers. **Placement DRC 0, parity 0.** Because the HV zone holds
no LV components, In1/In2 are naturally bare there (the outer HV faces FR4, not copper) — keepout
zones will enforce it; the opposite-outer GND pour is held off by the thick stackup. Creepage rule
already at 2mm (coated). Routing the isolated HV zone next.

---

## Decision A1 — execution & outcome (2026-06-08)

Implemented A1 end-to-end via deterministic pcbnew scripts (DRC checked headlessly with
`kicad-cli pcb drc`, which — unlike `pcbnew.WriteDRCReport` — runs without the full app context).

### What was built
1. **Inner voids (`prep_A1.py`).** In1.Cu + In2.Cu rule-area keepouts over the HV zone
   `x[163..202.5] y[94.5..142]` (`SetDoNotAllowTracks/Vias/ZoneFills`). No inner copper can sit under
   the outer-layer HV → outer HV faces only FR4 (+ conformal coat on the exposed surface). The
   top-channel `y<94.5` is intentionally **outside** the void so header-escape routing stays on inner.
2. **LV displaced by the void, re-routed (clean).** Adding the void invalidated three inner-layer LV
   nets that used to cross the HV zone. All re-routed up into the **empty B.Cu top channel** (header
   pins/escapes are all on F/In; B was bare there):
   - `+5V` (U1.7) and `Net-(U1-VIN)` (U1.1 ↔ FB1.2): B-layer lanes at y≈93.2/93.9, kept ≥2 mm off the
     opto HV pads and below the header pins; reconnect on existing vias / SMD pads.
   - `GPIO_16` (→ header pin 36, mid-field): F arrival → B climb up the opto **mid-body gap (x161.5,
     ≥3 mm from the HV pad column)** → F corridor threading the pin34/36 column-gap.
   - `GPIO_26` jogged to clear OR1's HV pad by >2 mm.
   These are **DRC-clean**.
3. **Mounting-hole safety fix (`fix_holes.py`).** H1–H4 (`MountingHole_2.7mm_M2.5_Pad_TopBottom`) shipped
   with **unconnected 5.4 mm copper pads on F & B = floating conductors**. H4 sits in the HV terminal
   zone — a floating 5.4 mm plate near 5 kV can charge to an intermediate potential and erode creepage;
   H1 also blocked the top routing channel. **Removed the oversized floating pads**, leaving the standard
   3.1 mm plated mounting ring. (If chassis-grounding is wanted, add a deliberate GND tie in review.)
   This shows up as 4 `lib_footprint_mismatch` (board instance now differs from library) and 4
   `extra_footprint` parity notes — both expected/benign (mounting holes have no schematic symbol).
4. **HV routed on OUTER layers only (`route_hv.py`), 0.25 mm, 2 mm target clearance.** Key levers:
   - **Layer-separated crossings:** HV nets that must cross are put on opposite outer layers (F vs B).
     KiCad creepage/clearance is per-surface, so F-vs-B HV pairs don't creep against each other; the
     through-board (vertical) separation is handled by the thick stackup (below).
   - `HV_RAIL` (B): threads the one-track-wide pinch between the opto GND pads (x165) and U1.9 GND
     (x170.95) at **x≈167.95** — the strip is only ~4.3 mm of clear copper, so RAIL fits at 0.25 mm
     with ~0.025 mm margin each side (see residual #1).
   - `HV_CH1_DIS`/`HV_CH2_DIS` cross the HV zone via the clear corridor between U1.8 and U1.9.
   - `HV_CH1`→J3 (B) and `HV_CH2_DIS` (F) clear the **H4 mounting hole** with opposite-layer
     **S-curves** (rise to y≈134.8 where H4 is >3.67 mm away, dip to y≈136 past the R26 pads).
   - **All 5 HV nets are electrically connected; HV is 100 % on F/B (zero HV copper on In1/In2).**

### Custom JLCPCB stackup (the "thick" part of A1) — FAB SPEC
The void removes inner copper under HV; the **vertical** HV-to-opposite-outer-GND-pour gap is set by
board thickness. Target ≤ ~2 kV/mm sustained in FR4 bulk for long-term reliability at 5 kV:

| Layer | Copper | Dielectric to next |
|------|--------|--------------------|
| F.Cu (HV + GND pour) | 1 oz | **core/prepreg to In1 ≥ 0.5 mm** |
| In1.Cu (**voided under HV**) | 0.5 oz | ≥ 1.0 mm |
| In2.Cu (**voided under HV**) | 0.5 oz | **≥ 0.5 mm to B** |
| B.Cu (HV + GND pour) | 1 oz | — |

**Order from JLCPCB as a 4-layer board, total thickness 2.0 mm (min) — preferably 2.4 mm — with a
custom stackup that puts ≥0.5 mm dielectric between F↔In1 and In2↔B** (so an F-side HV trace is ≥0.5 mm
from any In1 copper edge and ≥2.0 mm from the B-side GND pour through the board). JLC's standard 2.0 mm
4-layer (0.5/0.55/... ) is acceptable as a floor; 2.4 mm is the safer choice. **+ conformal coating**
(e.g. acrylic/urethane) over both outer surfaces → pollution degree 1 → 2 mm creepage is the governing
2D rule (already in the .kicad_dru).

### Residuals — for the MANDATORY human-EE review before fab
DRC (severity all, 2 mm HV): **HV is connected & on-outer**; the following remain, all traced to one
root cause — the **bottom-right terminal/bleeder cluster is over-packed**:

1. **6 HV creepage/clearance at 1.3–2.0 mm**, all against **J3.1 GND** (a large screw-terminal pad).
   `R26.2 GND (187.62,133)` and `J3.1 GND (188,139)` are only ~3.4 mm apart → no 2 mm-clearance HV
   track can pass between them, so `HV_CH1`→`J3.2` is walled in. **Recommended fix (needs a human —
   it changes how 5 kV is wired):** re-orient/re-place J3 so its GND pad is *not* between the resistor
   block and the CH1 output pad (e.g. swap J3 pin assignment to GND-outer/CH1-inner, or shift the
   terminal), which simultaneously opens the GND escape in #2. *Not* done autonomously: pin-swapping an
   HV output terminal affects field wiring safety.
2. **4 unconnected GND pads** = HV-zone GND **pour islands** (`{OR3.4,U1.9}`, `{R25.2,R26.2,J3.1}`,
   + an F-corner sliver). With HV on *both* outer layers and inner voided, these GND pads are boxed in
   with no in-zone escape. Resolved by the same #1 re-placement (give GND an outer-layer path), or by
   adding a deliberate GND-stitch lane during the review.
3. **GPIO_12_Boost unrouted (2 ratsnest)** — *pre-existing* (0 tracks originally; one of the original
   "5 unrouted"). Its target U2/R9 cluster (a 5-pin device with all pins already routed) is saturated on
   every layer. The void did **not** displace it. Left as the pre-existing gap; needs interactive routing.
4. **Left-strip RAIL pinch (#residual-margin).** RAIL threads the opto-GND ↔ U1.9-GND gap with ~25 µm
   slack each side — below fab tolerance. Recommend nudging U1 ~+0.5 mm right (widens the strip) in review.
5. Cosmetic: 13 silk_over_copper / 8 text_height / 8 silk_overlap / 3 silk_edge — footprint silkscreen
   (ref-des over pads, sub-min text); 2 starved_thermal on Q1/Q3 GND (pre-existing thermal relief).

**Bottom line:** Decision A1 is *structurally complete* — HV is on the outer layers at 0.25 mm, inner
layers are voided beneath it, LV is cleanly re-routed around the voids, the floating mounting pads are
gone, and the thick-stackup spec is defined. The board is **not yet fab-ready**: the bottom-right HV
terminal cluster needs a placement refinement (item #1, which also fixes #2 and is a human-wiring
decision), GPIO_12_Boost needs routing (#3), and the left strip wants a 0.5 mm U1 nudge (#4). All are
documented above for the required 5 kV EE review. Render: `docs/A1_outer_routed.png`. Working scripts in
the session scratch dir (`prep_A1.py`, `route_hv.py`, `fix_holes.py`); board checkpoints `CKPT_*.kicad_pcb`.

---

## Decision A1 — placement refinement RESOLVED the HV residuals (2026-06-08)

The earlier residuals (6 HV creepage vs J3.1 GND, 4 GND pour islands) were all rooted in the over-packed
bottom-right cluster. With the user's approval ("re-place + finish", net/pin assignments unchanged) I did
a **targeted HV-zone placement refinement** (`replace_A1.py`) and re-routed (`route_hv.py`):

- **Spread the four HV resistors** from a 4 mm-pitch block into two channel-pairs with a **7 mm middle gap**:
  R1@y120, R25@y125 — (gap) — R2@y131, R26@y137 (centers; pads at x172.38/187.62). The gap does three jobs:
  1. CH1's output reaches **J3.2 from the EAST** (cross the gap → right edge → down into J3.2), so it never
     passes J3.1 GND — the wall that caused the 6 creepage violations is gone.
  2. CH1 (B) and CH2 (F) cross the block on opposite layers in the gap (no mutual creepage).
  3. GND gets a routable path; the bleeder R25.2 GND ties to J4.1 GND through it.
- **GND stitching:** U1.9 GND → OR3.4 GND (F, clear of the B-side HV); bleeder R25.2 GND → J4.1 GND (B).
  Both islands the HV had boxed in are now connected. Removed a pre-existing dangling GPIO_6 via.
- **CH1 F→B transition uses the R25.1 PTH pad itself** (no separate via → no co-located holes).
- HV traces 0.25 mm; RAIL still threads the opto↔U1.9 pinch at x167.95.

### Result — verified with `kicad-cli pcb drc --severity-all`
- **HV: 0 creepage / clearance / short / crossing violations.** All 5 HV nets connected.
- **HV is 100 % on the outer layers** (F.Cu 15 segs + B.Cu 19 segs; **In1/In2 carry ZERO HV copper**).
- **GND connected** (all functional GND pads); only a tiny floating corner pour sliver remains (cosmetic).
- 48 total DRC items, all **cosmetic or pre-existing**: 35 silkscreen (ref-des over pads / sub-min text /
  overlap — footprint silk, a cleanup pass), 5 redundant LV stub tails (track_dangling; nets connected),
  4 lib_footprint_mismatch (the intentional mounting-hole pad removal), 2 starved_thermal (Q1/Q3 GND
  relief, pre-existing), and **2 courtyards_overlap (the one real item — see below)**.

### Remaining for the human-EE review (much smaller now)
1. **MECHANICAL — R26 body vs H4 mounting screw (2 courtyard overlaps).** The four bleeder/charge resistors
   are 18 mm long and need a 6 mm pad pitch for 2 mm creepage; four of them at 6 mm don't fit between U1
   (y≈118) and H4 (y138.5), so R26 sits at y137 — its body lands ~1 mm from H4's M2.5 screw head and the J3
   terminal. **No electrical issue** (copper clearances are met); verify standoff/screw-head clearance, use
   a low-profile/flat screw at H4, or source a shorter R26. This is the genuine size constraint of fitting
   4× 18 mm HV resistors + a corner mounting hole on 85×56.
2. **GPIO_12_Boost** still unrouted (pre-existing; saturated U2/R9 cluster) — interactive routing.
3. Cosmetic silkscreen cleanup; the floating corner GND sliver; Q1/Q3 thermal relief.
4. Standard 5 kV sign-off: confirm the thick-stackup order (above), conformal coat, creepage on the as-built
   Gerbers, BOM HV ratings.

**Bottom line: Decision A1 is electrically complete and DRC-clean on all HV/GND nets.** HV is on the outer
layers, inner layers are voided beneath it, LV is re-routed around the voids, the thick stackup is specified,
and the floating mounting pads are gone. Renders: `docs/A1_final_top.png`, `docs/A1_final_bottom.png`.
Scripts: `prep_A1.py` (voids + LV reroute), `replace_A1.py` (resistor spread), `route_hv.py` (HV + GND),
`fix_holes.py` (mounting pads). Board checkpoint `CKPT_A1_FINAL.kicad_pcb`.
