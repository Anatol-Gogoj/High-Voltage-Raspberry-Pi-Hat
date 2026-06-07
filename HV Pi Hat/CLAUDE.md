# HV Pi Hat — agent onboarding (keep this file short)

**What:** A 2-channel high-voltage driver for Dielectric Elastomer Actuators (DEAs), built as a
Raspberry Pi 5 HAT. Drives up to **5 kV** into **< 1 nF** loads. KiCad 9 project, this directory.
**State:** mid-build — schematic control-circuit rework in progress (see `docs/STATUS.md`).

## Read first, then open only what you need (keeps context small)
| Doc | What's in it |
|---|---|
| `docs/STATUS.md` | Where we are, task list, next steps — **read first** |
| `docs/DECISIONS.md` | Locked design decisions + rationale |
| `docs/CONTROL_DESIGN.md` | Corrected control/drive circuit — **source of truth for values** |
| `docs/EESCHEMA_TODO.md` | Schematic build checklist + live progress |
| `docs/REVIEW_FINDINGS.md` | Bugs found in the original design (the "why") |
| `docs/TOOLING.md` | kicad-cli / pcbnew / DRC / render / netlist commands |
| `datasheets/README.md` | Parts, verified specs, gotchas |

## 30-second orientation
SMHV0550 (5 kV / 200 µA module) makes the HV rail. Per channel: two HVM OPTO-100 (10 kV)
opto-couplers — one **charges** the DEA from the rail, one **discharges** it through a resistor
to GND — each driven by a TN0610 MOSFET off a Pi GPIO. HV setpoint = PWM → RC → op-amp(×1.55)
→ module PGM. HV nets held to 4 mm clearance + creepage (conformal-coated), enforced by
`HV Pi Hat.kicad_dru`.

## Top gotchas (don't relearn these the hard way)
- OPTO-100 CTR ≈ **0.15 %** → opto-LED resistors ~**51 Ω** (not 200 Ω) to reach 5 kV.
- SMHV **`ILIMIT` (pin 7) MUST tie to 5 V**, or the module sources ~no current.
- `MHR0317SA107F70` = **100 MΩ** (the old "50 M" label was wrong).
- Schematic edits = eeschema **GUI** (no schematic Python API). The **PCB is scriptable** via `pcbnew`.
- Board is **85 × 56 mm** (intentionally wider than a 65 mm HAT) for HV creepage.

## Conventions
- Don't `git commit` / `push` unless asked. `render_*.png` / `drc_*.json` are git-ignored (regenerable).
- kicad-cli: `/c/Program Files/KiCad/9.0/bin/kicad-cli.exe` · KiCad python (`pcbnew`): same dir, `python.exe`.
