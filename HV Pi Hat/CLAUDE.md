# HV Pi Hat: agent onboarding (keep this file short)

**What:** A 2-channel high-voltage driver for dielectric elastomer actuators (DEAs), built as a
Raspberry Pi 5 add-on board. Drives up to **5 kV** into **< 1 nF** loads. KiCad **10** project,
this directory. The KiCad 9 CLI cannot load the schematic.

## Read first, then open only what you need
| Doc | What's in it |
|---|---|
| `docs/adr/` | Design decisions, one file each. Start with the index in `docs/adr/README.md` |
| `docs/CONTROL_DESIGN.md` | Control and drive circuit: **source of truth for values** |
| `docs/REVIEW_FINDINGS.md` | Bugs found in the original design (the "why") |
| `docs/TOOLING.md` | kicad-cli / pcbnew commands and KiCad 10 scripting gotchas |
| `docs/BOM_SOURCED.md`, `fab/BOM.csv` | Sourced parts; BOM regenerated from the schematic |
| `docs/HV_CONNECTOR_OPTIONS.md` | HV output termination study |
| `datasheets/README.md` | Parts, verified specs, gotchas |
| `tools/` | `HvInterlayer.py` and `PotMargin.py` (HV checks DRC cannot do), `revb/` (rev B build), `MakeLeadPair.py` |
| `docs/AUTONOMOUS_BUILD_LOG.md` | Historical log of the June 2026 build pass. Where it disagrees with an ADR, the ADR wins |

## 30-second orientation
SMHV0550 (5 kV / 200 uA module) makes the HV rail. Per channel: two HVM OPTO-100 (10 kV)
opto-couplers, one **charges** the DEA from the rail and one **discharges** it through 100 MOhm
to GND, each driven by a TN0610 MOSFET off a Pi GPIO. A 1 GOhm bleeder sits across each output.
HV setpoint = PWM, RC, op-amp (x1.55), module PGM. HV is on the outer layers only with the inner
layers voided beneath it (ADR-0002). The HV zone will be **potted** on both faces (ADR-0003);
until the IEC 60664-3 type 2 spacings are in hand, the interim layout rule is 2 mm, enforced by
`HV Pi Hat.kicad_dru`.

## Top gotchas (don't relearn these the hard way)
- OPTO-100 CTR is about **0.15 %**, so the opto-LED resistors are **51 Ohm** (not 200 Ohm).
- SMHV **`ILIMIT` (pin 7) MUST tie to 5 V**, or the module sources almost no current.
- `MHR0317SA107F70` = **100 MOhm** (the old "50 M" label was wrong).
- The 1 GOhm safety bleeders R25/R26 are **populated** by default (fail-safe when unpowered).
- PGM is held at 0 V at boot by R8 (100 k) only if U2's ground is connected. A GND pour island
  once cut U2.2 and R8.1 off; check GND connectivity after any re-pour.
- Order the PCB with the stackup named in ADR-0002 (JLC04201H-7628D), not the default.
- Schematic edits = eeschema **GUI** (no schematic Python API). The **PCB is scriptable** via `pcbnew`.
- The board is **rev B**: the standard **65 x 56.0 mm HAT outline** for a THT header (ADR-0004), built by
  `tools/revb/` (BuildRevB.py places, AutoRoute.py routes). J3/J4 are soldered HV lead pairs, not
  terminals. LV signals stay out of the pot except over U1's LV pin row. **20 mm standoffs**
  (ADR-0005): the Pi 5 Active Cooler sits under the bottom pot. The GPIO header for 20 mm is not
  yet chosen.

## Conventions
- Don't `git commit` / `push` unless asked. `render_*.png` / `drc_*.json` are git-ignored (regenerable).
- No fabrication outputs are committed until the ADR-0003 prerequisites are done and a human EE has
  reviewed the board (`fab/README.md`).
- Session state and next steps live outside the repo (the PR body for a branch); do not add status
  or session-log files here.
- kicad-cli: `/c/Program Files/KiCad/10.0/bin/kicad-cli.exe`; KiCad python (`pcbnew`): same dir, `python.exe`.
