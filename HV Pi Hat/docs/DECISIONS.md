# Locked design decisions — HV Pi Hat

Choices made with the user. Change only with a new explicit decision (and note it here).

| Area | Decision | Why |
|---|---|---|
| Form factor | **85 × 56 mm** (wider than the 65 mm standard HAT); committed | room for 5 kV creepage |
| Insulation | **Conformal coat** baseline; **pot/encapsulate** if more clearance needed | makes 5 kV fit a small board |
| HV spacing | **4 mm** clearance + creepage + edge on HV nets; **milled slots** between opposite polarities / channels / terminal pads | coated 5 kV figure; slots add creepage (KiCad treats slots as creepage barriers). Enforced in `HV Pi Hat.kicad_dru` |
| Max voltage | Design **headroom to 5 kV**; run variable/lower in firmware | |
| DEA load | **< 1 nF** | charge & discharge both fast |
| Bleeder | **100 MΩ** (R1/R2) | two-channel 200 µA budget; part is already 100 MΩ |
| HV output connector | **2-position terminal block per channel** + a **milled slot between its two pads** | 1×1 HV terminals hard to source; slot restores creepage |
| HV setpoint (PGM) | **PWM → RC → op-amp ×1.55 → PGM** (MCP6001-OT) | Pi has no DAC; 3.3 V PWM alone caps ~3.3 kV — gain to reach 0–5 kV |
| Current limit | **ILIMIT (pin 7) tied to 5 V** (disabled) | module is inherently 200 µA |
| Indicators | **Kept**, as a **parallel** branch off each channel MOSFET | the limit was *headroom*, not current — a series stack starved the opto |
| Discharge | **Active**: 2nd opto + series R per channel (independent charge / hold / discharge) | user request; controllable actuator relaxation |
| Safety bleeder | **1 GΩ always-on across each output, DNP-able** | fail-safe bleed-down when unpowered |

## Added during the autonomous build pass (2026-06-07) — see `AUTONOMOUS_BUILD_LOG.md` for full rationale

| Area | Decision | Why |
|---|---|---|
| Indicator branch | **+5V → R(470 Ω) → D → MOSFET DRAIN** (not the opto-LED node) | the as-built schematic tied the indicator to the ~2.9 V opto-LED node (≈0.1 V headroom → wouldn't light); the design's drain node gives ~6 mA. Fixed value 47→**470 Ω** (47 Ω on the drain node would over-drive the LED) |
| Input bulk caps | **Keep 47/1/0.1 µF on +5V** (not moved to VIN across the ferrite); **add C5 0.1 µF op-amp decoupling** | a ferrite bead is ~transparent at the module's 45–80 kHz switching freq, so moving bulk across it is negligible benefit + a risky rewire; op-amp decoupling was missing from the design |
| Custom-symbol pin types | **MOSFET SRC/DRAIN, opto pins, module HVRTN → passive; ILIMIT → input** (in `.kicad_sch` *and* `HV_Electronics.kicad_sym`) | the symbols typed passive terminals as "output" → false ERC output-output errors; corrected to model reality and clear ERC |
| Power flags | **PWR_FLAG on +5V and GND** | HAT is powered from the Pi (no on-board supply) — satisfies ERC "power pin not driven" |
| HV netclass binding | **`.kicad_pro` pattern `/HV_*` → HV_5kV** (removed the orphaned `netclass_flag` directives) | centralized, survives net renames; the HV nets were named with an `HV_` prefix for this |
| Passive footprints | **0603** for the four 51 Ω opto-LED R (power margin ~0.09 W) + previously-unfootprinted parts; **1206** for the 47 µF | 0402 was marginal for the opto-LED resistors; 0603/1206 source trivially and hand-solder |
| **HV output connector** | **OPEN — `SHV-R` flagged, reselection recommended.** Footprint is oversized (~34 mm) and the real SHV-R is only 3.5 kV-continuous rated. | doubled-opto HV zone + this connector is over-constrained on 85×56; and 3.5 kV continuous is marginal for a 5 kV design → **needs a user decision** (this supersedes the earlier "2-pos terminal block" item, which the user had already replaced with SHV) |
